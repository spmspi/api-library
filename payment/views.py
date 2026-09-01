from rest_framework import viewsets
from django.db import transaction

import stripe

from app import settings
from books.permissions import IsAdminOrIfAuthenticatedReadOnly
from borrowing.task import send_notification_task
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from payment.models import Payment
from payment.serializers import PaymentSerializer, PaymentDetailSerializer
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self):
        current_user = self.request.user
        queryset = self.queryset

        if current_user.is_staff:
            return queryset
        return queryset.filter(borrowing__user=current_user)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return PaymentDetailSerializer
        return PaymentSerializer


class PaymentSuccessView(APIView):
    def get(self, request):
        return Response(
            {"detail": "Payment is begin processed"},
            status=status.HTTP_200_OK,
        )


class PaymentCancelView(APIView):
    def get(self, request):
        return Response(
            {
                "detail": "Payment was cancelled. You can pay later from your borrowings."
            },
            status=status.HTTP_200_OK,
        )


@csrf_exempt
def stripe_webhook_view(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        print(f"Error parsing payload: {e}")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        print(f"Error verifying webhook signature: {e}")
        return HttpResponse(status=400)

    if event.type == "checkout.session.completed":
        session = event.data.object
        try:
            with transaction.atomic():
                payment = Payment.objects.get(session_id=session.id)
                payment.status = Payment.StatusEnum.PAID
                payment.save()

                message = (
                    f"<b>💵Payment successful!💵</b>\n"
                    f"Book: {payment.borrowing.book.title} \n"
                    f"User: {payment.borrowing.user}\n"
                    f"Money paid: {payment.money} USD\n"
                )
                transaction.on_commit(lambda: send_notification_task.delay(message))

            print("Payment marked as paid")
        except Payment.DoesNotExist:
            print("Payment not found for this session")
    else:
        print(f"Unhandled event type {event.type}")

    return HttpResponse(status=200)
