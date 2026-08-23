from django.shortcuts import render
from rest_framework import viewsets

from payment.models import Payment
from payment.serializers import PaymentSerializer, PaymentListSerializer, PaymentDetailSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return PaymentListSerializer
        if self.action == "detail":
            return PaymentDetailSerializer
        return PaymentSerializer
