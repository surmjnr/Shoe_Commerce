import logging
import uuid

import requests
from django.conf import settings

from apps.orders.models import PaymentStatus

from .base import PaymentInitResult, PaymentProvider, PaymentVerifyResult

logger = logging.getLogger(__name__)


class MoMoPaymentProvider(PaymentProvider):
    """Mobile Money payment provider abstraction."""

    def __init__(self):
        self.api_key = settings.PAYMENT_API_KEY
        self.secret = settings.PAYMENT_SECRET
        self.base_url = getattr(settings, "PAYMENT_API_URL", "")

    def initialize_payment(self, order, phone, amount, metadata=None):
        reference = f"MOMO-{uuid.uuid4().hex[:12].upper()}"

        if not self.api_key or not self.base_url:
            logger.warning("MoMo credentials not configured, falling back to mock behavior")
            return PaymentInitResult(
                success=True,
                reference=reference,
                message="MoMo not configured. Payment pending manual verification.",
                metadata={"phone": phone},
            )

        try:
            response = requests.post(
                f"{self.base_url}/payments/initialize",
                json={
                    "amount": str(amount),
                    "phone": phone,
                    "reference": reference,
                    "order_number": order.order_number,
                },
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
            return PaymentInitResult(
                success=True,
                reference=data.get("reference", reference),
                checkout_url=data.get("checkout_url"),
                message=data.get("message", "Payment initiated."),
                metadata=data,
            )
        except requests.RequestException as e:
            logger.error("MoMo initialization failed: %s", e)
            return PaymentInitResult(
                success=False,
                reference=reference,
                message="Payment initialization failed. Please try again.",
            )

    def verify_payment(self, reference):
        if not self.api_key or not self.base_url:
            return PaymentVerifyResult(
                success=False,
                status=PaymentStatus.PENDING,
                reference=reference,
                message="MoMo not configured.",
            )

        try:
            response = requests.get(
                f"{self.base_url}/payments/verify/{reference}",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
            status = (
                PaymentStatus.PAID
                if data.get("status") == "success"
                else PaymentStatus.PENDING
            )
            return PaymentVerifyResult(
                success=status == PaymentStatus.PAID,
                status=status,
                reference=reference,
                message=data.get("message", ""),
                metadata=data,
            )
        except requests.RequestException as e:
            logger.error("MoMo verification failed: %s", e)
            return PaymentVerifyResult(
                success=False,
                status=PaymentStatus.FAILED,
                reference=reference,
                message="Payment verification failed.",
            )

    def handle_webhook(self, payload, headers=None):
        reference = payload.get("reference", "")
        if payload.get("status") in ("success", "paid"):
            status = PaymentStatus.PAID
        elif payload.get("status") == "failed":
            status = PaymentStatus.FAILED
        else:
            status = PaymentStatus.PENDING

        return PaymentVerifyResult(
            success=status == PaymentStatus.PAID,
            status=status,
            reference=reference,
            message="Webhook processed.",
            metadata=payload,
        )
