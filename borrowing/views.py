from datetime import date
from django.db import transaction
from rest_framework import viewsets, status, request
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.urls import reverse
from payment.models import Payment
from payment.services import calculate_amount
from payment.stripe import create_checkout_session
from . import serializers
from .task import send_notification_task

from books.models import Book
from borrowing.models import Borrowing
from borrowing.serializers import (
    BorrowingSerializer,
    BorrowingDetailSerializer,
    BorrowingCreateSerializer,
)


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.select_related("book", "user").all()
    permission_classes = (IsAuthenticated,)

    @staticmethod
    def _params_to_ints(qs):
        """Converts a list of string IDs to a list of integers"""
        return [int(str_id) for str_id in qs.split(",")]

    def get_queryset(self):
        current_user = self.request.user
        queryset = self.queryset

        if not current_user.is_staff:
            return queryset.filter(user=current_user)

        user_param = self.request.query_params.get("user")

        if user_param:
            user_ids = self._params_to_ints(user_param)
            if user_ids:
                queryset = queryset.filter(user_id__in=user_ids)

        is_active = self.request.query_params.get("is_active")

        if is_active is not None:
            if is_active.lower() in "true":
                queryset = queryset.filter(actual_return_date__isnull=True)
            elif is_active.lower() in "false":
                queryset = queryset.filter(actual_return_date__isnull=False)

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return BorrowingSerializer
        if self.action == "create":
            return BorrowingCreateSerializer
        elif self.action == "retrieve":
            return BorrowingDetailSerializer
        return BorrowingSerializer

    def perform_create(self, serializer):
        with transaction.atomic():
            borrowing = serializer.save(user=self.request.user)
            book = serializer.validated_data["book"]
            book.inventory -= 1
            book.save()
            serializer.save(user=self.request.user)
            message = (
                f"<b>New Borrowing!</b>\n"
                f"Book: {book.title}\n"
                f"User: {self.request.user}\n"
                f"Expected return date: {borrowing.expected_return_date}\n"
            )
            transaction.on_commit(lambda: send_notification_task.delay(message))
            money = calculate_amount(borrowing)
            success_url = (
                self.request.build_absolute_uri(reverse("payment:success"))
                + "?session_id={CHECKOUT_SESSION_ID}"
            )
            cancel_url = self.request.build_absolute_uri(reverse("payment:cancel"))
            session = create_checkout_session(
                borrowing=borrowing,
                money=money,
                success_url=success_url,
                cancel_url=cancel_url,
            )

            Payment.objects.create(
                borrowing=borrowing,
                session_url=session.url,
                session_id=session.id,
                money=money,
                type=Payment.TypeEnum.PAYMENT,
            )
            self.payment_url = session.url

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        response.data["payment_url"] = self.payment_url
        return response

    @action(
        detail=True,
        methods=["post", "get"],
        url_path="return",
        permission_classes=[IsAuthenticated],
    )
    def return_book(self, request, pk=None):
        borrowing = self.get_object()

        if borrowing.actual_return_date is not None:
            return Response(
                {"Info": "The book had already been returned."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            borrowing.actual_return_date = date.today()
            borrowing.save()

            borrowing.book.inventory += 1
            borrowing.book.save()

            payment_url = None

            if borrowing.actual_return_date > borrowing.expected_return_date:
                money = calculate_amount(borrowing, payment_type=Payment.TypeEnum.FINE)

                success_url = (
                        self.request.build_absolute_uri(reverse("payment:success"))
                        + "?session_id={CHECKOUT_SESSION_ID}"
                )
                cancel_url = self.request.build_absolute_uri(reverse("payment:cancel"))

                session = create_checkout_session(
                    borrowing=borrowing,
                    money=money,
                    success_url=success_url,
                    cancel_url=cancel_url,
                )

                Payment.objects.create(
                    borrowing=borrowing,
                    session_url=session.url,
                    session_id=session.id,
                    money=money,
                    type=Payment.TypeEnum.FINE,
                    status=Payment.StatusEnum.PENDING,
                )

                payment_url = session.url

        serializer = BorrowingDetailSerializer(borrowing)
        data = serializer.data
        if payment_url:
            data["payment_url"] = payment_url

        return Response(data, status=status.HTTP_200_OK)