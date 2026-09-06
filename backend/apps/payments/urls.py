from django.urls import path

from .views import PaymentInitializeView, PaymentWebhookView

urlpatterns = [
    path("payments/initialize/", PaymentInitializeView.as_view(), name="payment-initialize"),
    path("payments/webhook/", PaymentWebhookView.as_view(), name="payment-webhook"),
]
