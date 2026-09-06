import pytest
from decimal import Decimal

from apps.orders.models import OrderStatus, PaymentMethod, PaymentStatus
from apps.orders.services import OrderService, OrderValidationError
from apps.products.models import ProductVariant


@pytest.mark.django_db
class TestOrderCreation:
    def test_successful_order_decrements_stock(self, product, store_settings):
        variant = product.variants.get(size="42")
        order = OrderService.create_order(
            {
                "buyer_name": "John Mensah",
                "buyer_phone": "0241234567",
                "delivery_address": "East Legon, Accra",
                "payment_method": PaymentMethod.PAY_ON_DELIVERY,
            },
            [{"product_id": product.id, "variant_id": variant.id, "quantity": 2}],
        )

        variant.refresh_from_db()
        assert variant.stock_quantity == 3
        assert order.total == Decimal("1730")  # 850*2 + 30 delivery
        assert order.payment_status == PaymentStatus.PENDING
        assert order.order_status == OrderStatus.PENDING

    def test_insufficient_stock_rejected(self, product, store_settings):
        variant = product.variants.get(size="42")

        with pytest.raises(OrderValidationError) as exc:
            OrderService.create_order(
                {
                    "buyer_name": "John Mensah",
                    "buyer_phone": "0241234567",
                    "delivery_address": "East Legon, Accra",
                    "payment_method": PaymentMethod.PAY_ON_DELIVERY,
                },
                [{"product_id": product.id, "variant_id": variant.id, "quantity": 10}],
            )

        assert "Insufficient stock" in str(exc.value)
        variant.refresh_from_db()
        assert variant.stock_quantity == 5


@pytest.mark.django_db
class TestOrderStatusTransitions:
    def test_valid_transition(self, product, store_settings):
        variant = product.variants.get(size="42")
        order = OrderService.create_order(
            {
                "buyer_name": "John Mensah",
                "buyer_phone": "0241234567",
                "delivery_address": "East Legon, Accra",
                "payment_method": PaymentMethod.PAY_ON_DELIVERY,
            },
            [{"product_id": product.id, "variant_id": variant.id, "quantity": 1}],
        )

        order = OrderService.update_status(order, OrderStatus.CONFIRMED)
        assert order.order_status == OrderStatus.CONFIRMED

        order = OrderService.update_status(order, OrderStatus.PROCESSING)
        assert order.order_status == OrderStatus.PROCESSING

    def test_invalid_transition_rejected(self, product, store_settings):
        variant = product.variants.get(size="42")
        order = OrderService.create_order(
            {
                "buyer_name": "John Mensah",
                "buyer_phone": "0241234567",
                "delivery_address": "East Legon, Accra",
                "payment_method": PaymentMethod.PAY_ON_DELIVERY,
            },
            [{"product_id": product.id, "variant_id": variant.id, "quantity": 1}],
        )

        with pytest.raises(OrderValidationError):
            OrderService.update_status(order, OrderStatus.DELIVERED)
