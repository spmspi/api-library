from datetime import date

from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from borrowing.models import Borrowing
from borrowing.serializers import (
    BorrowingSerializer,
    BorrowingDetailSerializer,
    BorrowingCreateSerializer,
)


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.select_related("book", "user").all()
    serializer_class = BorrowingSerializer

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
            book = serializer.validated_data["book"]
            book.inventory -= 1
            book.save()
            serializer.save(user=self.request.user)

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

        serializer = BorrowingDetailSerializer(borrowing)
        return Response(serializer.data, status=status.HTTP_200_OK)
