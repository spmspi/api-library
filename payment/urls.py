from django.urls import include, path
from rest_framework import routers
from payment.views import PaymentViewSet, PaymentSuccessView, PaymentCancelView, stripe_webhook_view

router = routers.DefaultRouter()
router.register("", PaymentViewSet, basename="payment")

urlpatterns = [
    path("success/", PaymentSuccessView.as_view(), name="success"),
    path("cancel/", PaymentCancelView.as_view(), name="cancel"),
    path("webhook/", stripe_webhook_view, name="webhook"),
    path("", include(router.urls)),
]

app_name = "payment"
