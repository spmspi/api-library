from rest_framework import viewsets

from payment.models import Payment
from payment.serializers import PaymentSerializer, PaymentDetailSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()


    def get_queryset(self):
        current_user = self.request.user
        queryset = self.queryset

        if not current_user.is_staff:
            return queryset.filter(user=current_user)

    def get_serializer_class(self):
        if self.action == "detail":
            return PaymentDetailSerializer
        return PaymentSerializer
