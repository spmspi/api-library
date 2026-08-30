from django.urls import path, include
from rest_framework import routers
from django.urls import path
from payment.views import PaymentViewSet, PaymentSuccessView, PaymentCancelView

router = routers.DefaultRouter()
router.register("", PaymentViewSet, basename="payment")

urlpatterns = [
    path("success/", PaymentSuccessView.as_view(), name="success"),
    path("cancel/", PaymentCancelView.as_view(), name="cancel"),
    path("", include(router.urls)),
]

app_name = "payment"
