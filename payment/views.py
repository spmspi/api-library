from rest_framework import viewsets
from django.db import transaction

import stripe

from books.permissions import IsAdminOrReadOnly, IsAdminOrIfAuthenticatedReadOnly
from borrowing.task import send_notification_task
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from payment.models import Payment
from payment.serializers import PaymentSerializer, PaymentDetailSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly, )

    def get_queryset(self):
        current_user = self.request.user
        queryset = self.queryset

        if current_user.is_staff:
            return queryset
        return queryset.filter(borrowing__user=current_user)

    def get_serializer_class(self):
        if self.action == "detail":
            return PaymentDetailSerializer
        return PaymentSerializer


class PaymentSuccessView(APIView):
    def get(self, request):

        session_id = request.query_params.get("session_id")
        session = stripe.checkout.Session.retrieve(session_id)
        payment = Payment.objects.get(session_id=session_id)

        if session.payment_status == "paid":
            payment.status = Payment.StatusEnum.PAID
            payment.save()

            message = (
                f"<b>💵Payment successful!💵</b>\n"
                f"Book: {payment.borrowing.book.title} \n"
                f"User: {payment.borrowing.user}\n"
                f"Money paid: {payment.money} USD\n"
            )

            transaction.on_commit(lambda: send_notification_task.delay(message))
            return Response({"detail": "Payment successful"}, status=status.HTTP_200_OK)

        return Response(
            {"detail": "Payment not completed"},
            status=status.HTTP_402_PAYMENT_REQUIRED,
        )

class PaymentCancelView(APIView):
    def get(self, request):
        return Response(
            {"detail": "Payment was cancelled. You can pay later from your borrowings."},
            status=status.HTTP_200_OK,
        )