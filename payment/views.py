from rest_framework import viewsets
from django.db import transaction

import payment
from borrowing.task import send_notification_task
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from payment.models import Payment
from payment.serializers import PaymentSerializer, PaymentDetailSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()

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

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        message = (
            f"<b>New payments!</b>\n"
            f"Book: {payment.borrowing.book.title}\n"
            f"User: {self.request.user}\n"
            f"Expected return date: {payment.money}\n"
        )
        transaction.on_commit(lambda: send_notification_task.delay(message))


class PaymentSuccessView(APIView):
    def get(self, request):
        session_id = request.query_params.get("session_id")
        return Response({"detail": "Payment successful"}, status=status.HTTP_200_OK)
