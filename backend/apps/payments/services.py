import logging

from django.conf import settings
from django.db import transaction

from apps.orders.models import Order, OrderStatus, PaymentMethod, PaymentStatus
from apps.orders.services import OrderService

from .models import Payment
from .providers.base import PaymentProvider
from .providers.mock import MockPaymentProvider
from .providers.momo import MoMoPaymentProvider

logger = logging.getLogger(__name__)


def get_payment_provider() -> PaymentProvider:
    provider = settings.PAYMENT_PROVIDER.lower()
    if provider == "momo":
        return MoMoPaymentProvider()
    return MockPaymentProvider()


class PaymentService:
    @staticmethod
    @transaction.atomic
    def initialize_payment(order_id, phone):
        try:
            order = Order.objects.select_for_update().get(pk=order_id)
        except Order.DoesNotExist:
            raise ValueError("Order not found.")

        if order.payment_method != PaymentMethod.MOMO:
            raise ValueError("Order is not a Mobile Money payment.")

        if hasattr(order, "payment"):
            payment = order.payment
            if payment.status == PaymentStatus.PAID:
                raise ValueError("Payment already completed.")
        else:
            provider = get_payment_provider()
            result = provider.initialize_payment(order, phone, order.total)

            if not result.success:
                raise ValueError(result.message)

            payment = Payment.objects.create(
                order=order,
                provider=settings.PAYMENT_PROVIDER,
                provider_reference=result.reference,
                amount=order.total,
                status=PaymentStatus.PENDING,
                metadata=result.metadata or {},
            )

            return {
                "reference": payment.provider_reference,
                "checkout_url": result.checkout_url,
                "message": result.message,
            }

        return {
            "reference": order.payment.provider_reference,
            "message": "Payment already initialized.",
        }

    @staticmethod
    @transaction.atomic
    def verify_payment(reference):
        try:
            payment = Payment.objects.select_for_update().get(
                provider_reference=reference
            )
        except Payment.DoesNotExist:
            raise ValueError("Payment not found.")

        if payment.status == PaymentStatus.PAID:
            return payment

        provider = get_payment_provider()
        result = provider.verify_payment(reference)

        if result.success:
            payment.status = PaymentStatus.PAID
            payment.metadata.update(result.metadata or {})
            payment.save()

            payment.order.payment_status = PaymentStatus.PAID
            payment.order.save(update_fields=["payment_status", "updated_at"])

            if payment.order.order_status == OrderStatus.PENDING:
                OrderService.update_status(payment.order, OrderStatus.CONFIRMED)

        return payment

    @staticmethod
    @transaction.atomic
    def handle_webhook(payload, headers=None):
        provider = get_payment_provider()
        result = provider.handle_webhook(payload, headers)

        if not result.reference:
            logger.warning("Webhook missing reference")
            return None

        try:
            payment = Payment.objects.select_for_update().get(
                provider_reference=result.reference
            )
        except Payment.DoesNotExist:
            logger.warning("Payment not found for reference: %s", result.reference)
            return None

        if payment.status == PaymentStatus.PAID:
            logger.info("Duplicate webhook ignored for %s", result.reference)
            return payment

        if result.success:
            payment.status = PaymentStatus.PAID
            payment.metadata.update(result.metadata or {})
            payment.save()

            payment.order.payment_status = PaymentStatus.PAID
            payment.order.save(update_fields=["payment_status", "updated_at"])

            if payment.order.order_status == OrderStatus.PENDING:
                OrderService.update_status(payment.order, OrderStatus.CONFIRMED)

        elif result.status == PaymentStatus.FAILED:
            payment.status = PaymentStatus.FAILED
            payment.save()
            payment.order.payment_status = PaymentStatus.FAILED
            payment.order.save(update_fields=["payment_status", "updated_at"])

        return payment
