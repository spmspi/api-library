from rest_framework import serializers

from borrowing.serializers import BorrowingSerializer
from payment.models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ("id", "status", "type", "borrowing", "money")


class PaymentDetailSerializer(serializers.ModelSerializer):
    borrowing = BorrowingSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = (
            "status",
            "type",
            "borrowing",
            "session_url",
            "money",
        )
