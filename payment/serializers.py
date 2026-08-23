from rest_framework import serializers

from payment.models import Payment
from user.serializers import UserSerializer


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ("id", "status", "type", "money")

class PaymentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ("id", "status", "type", "borrowing", "money" )


class PaymentDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = Payment
        fields = ("status", "type", "borrowing", "user", "session_id", "session_url", "money" )

