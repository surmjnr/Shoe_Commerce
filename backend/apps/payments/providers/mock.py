import logging
import uuid

from apps.orders.models import PaymentStatus

from .base import PaymentInitResult, PaymentProvider, PaymentVerifyResult

logger = logging.getLogger(__name__)


class MockPaymentProvider(PaymentProvider):
    """Mock provider for local development."""

    def initialize_payment(self, order, phone, amount, metadata=None):
        reference = f"MOCK-{uuid.uuid4().hex[:12].upper()}"
        logger.info("Mock payment initialized: %s for order %s", reference, order.order_number)
        return PaymentInitResult(
            success=True,
            reference=reference,
            checkout_url=None,
            message="Mock payment initialized. Use webhook to confirm.",
            metadata={"phone": phone, "mock": True},
        )

    def verify_payment(self, reference):
        return PaymentVerifyResult(
            success=True,
            status=PaymentStatus.PAID,
            reference=reference,
            message="Mock payment verified.",
        )

    def handle_webhook(self, payload, headers=None):
        reference = payload.get("reference", "")
        status = payload.get("status", PaymentStatus.PAID)
        return PaymentVerifyResult(
            success=status == PaymentStatus.PAID,
            status=status,
            reference=reference,
            message="Mock webhook processed.",
        )
