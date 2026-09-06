import pytest
from apps.payments.services import PaymentService
from apps.orders.models import PaymentMethod, PaymentStatus
from apps.orders.services import OrderService


@pytest.mark.django_db
class TestPaymentWebhook:
    def test_duplicate_webhook_is_idempotent(self, product, store_settings):
        variant = product.variants.first()
        order = OrderService.create_order(
            {
                "buyer_name": "John Mensah",
                "buyer_phone": "0241234567",
                "delivery_address": "East Legon, Accra",
                "payment_method": PaymentMethod.MOMO,
            },
            [{"product_id": product.id, "variant_id": variant.id, "quantity": 1}],
        )

        PaymentService.initialize_payment(order.id, "0241234567")
        reference = order.payment.provider_reference

        payload = {"reference": reference, "status": "success"}
        payment1 = PaymentService.handle_webhook(payload)
        payment2 = PaymentService.handle_webhook(payload)

        assert payment1.status == PaymentStatus.PAID
        assert payment2.status == PaymentStatus.PAID
        assert payment1.id == payment2.id
