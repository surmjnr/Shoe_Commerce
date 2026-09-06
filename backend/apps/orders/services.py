import logging
from decimal import Decimal

from django.db import transaction
from django.db.models import Sum

from apps.common.models import StoreSettings
from apps.products.models import Product, ProductStatus, ProductVariant
from apps.products.services import ProductService

from .models import (
    Order,
    OrderItem,
    OrderStatus,
    PaymentMethod,
    PaymentStatus,
    generate_order_number,
)

logger = logging.getLogger(__name__)

VALID_STATUS_TRANSITIONS = {
    OrderStatus.PENDING: [OrderStatus.CONFIRMED, OrderStatus.CANCELLED],
    OrderStatus.CONFIRMED: [OrderStatus.PROCESSING, OrderStatus.CANCELLED],
    OrderStatus.PROCESSING: [OrderStatus.OUT_FOR_DELIVERY, OrderStatus.CANCELLED],
    OrderStatus.OUT_FOR_DELIVERY: [OrderStatus.DELIVERED, OrderStatus.CANCELLED],
    OrderStatus.DELIVERED: [],
    OrderStatus.CANCELLED: [],
}


class OrderValidationError(Exception):
    def __init__(self, message, code="validation_error"):
        self.message = message
        self.code = code
        super().__init__(message)


class OrderService:
    @staticmethod
    @transaction.atomic
    def create_order(order_data, items_data):
        store_settings = StoreSettings.load()
        delivery_fee = store_settings.delivery_fee

        validated_items = []
        subtotal = Decimal("0")

        for item in items_data:
            validated = OrderService._validate_cart_item(item)
            validated_items.append(validated)
            subtotal += validated["subtotal"]

        total = subtotal + delivery_fee

        order = Order.objects.create(
            order_number=generate_order_number(),
            buyer_name=order_data["buyer_name"],
            buyer_phone=order_data["buyer_phone"],
            delivery_address=order_data["delivery_address"],
            delivery_notes=order_data.get("delivery_notes", ""),
            payment_method=order_data["payment_method"],
            payment_status=PaymentStatus.PENDING,
            order_status=OrderStatus.PENDING,
            subtotal=subtotal,
            delivery_fee=delivery_fee,
            total=total,
        )

        for item in validated_items:
            variant = item["variant"]
            variant.stock_quantity -= item["quantity"]
            variant.save(update_fields=["stock_quantity", "updated_at"])

            OrderItem.objects.create(
                order=order,
                product=item["product"],
                variant=variant,
                product_name=item["product"].name,
                size=variant.size,
                quantity=item["quantity"],
                unit_price=item["unit_price"],
                subtotal=item["subtotal"],
            )

            ProductService._sync_stock_status(item["product"])

        logger.info("Order created: %s", order.order_number)

        from apps.notifications.tasks import send_order_notification_task

        transaction.on_commit(
            lambda: send_order_notification_task.delay(order.id)
        )

        return order

    @staticmethod
    def _validate_cart_item(item_data):
        product_id = item_data.get("product_id")
        variant_id = item_data.get("variant_id")
        quantity = item_data.get("quantity", 1)

        if not product_id or not variant_id:
            raise OrderValidationError("Product and variant are required.")

        if quantity < 1:
            raise OrderValidationError("Quantity must be at least 1.")

        try:
            product = Product.objects.select_for_update().get(pk=product_id)
        except Product.DoesNotExist:
            raise OrderValidationError("Product not found.")

        if product.status != ProductStatus.PUBLISHED:
            raise OrderValidationError(f"{product.name} is not available.")

        try:
            variant = ProductVariant.objects.select_for_update().get(
                pk=variant_id, product=product, is_active=True
            )
        except ProductVariant.DoesNotExist:
            raise OrderValidationError("Selected size is not available.")

        if variant.stock_quantity < quantity:
            raise OrderValidationError(
                f"Insufficient stock for {product.name} size {variant.size}. "
                f"Only {variant.stock_quantity} available."
            )

        unit_price = product.price
        subtotal = unit_price * quantity

        return {
            "product": product,
            "variant": variant,
            "quantity": quantity,
            "unit_price": unit_price,
            "subtotal": subtotal,
        }

    @staticmethod
    @transaction.atomic
    def update_status(order, new_status):
        current = order.order_status
        allowed = VALID_STATUS_TRANSITIONS.get(current, [])

        if new_status not in allowed:
            raise OrderValidationError(
                f"Cannot transition from {current} to {new_status}."
            )

        order.order_status = new_status

        if new_status == OrderStatus.DELIVERED:
            if order.payment_method == PaymentMethod.PAY_ON_DELIVERY:
                order.payment_status = PaymentStatus.PAID

        if new_status == OrderStatus.CANCELLED:
            OrderService._restore_stock(order)
            if order.payment_status == PaymentStatus.PAID:
                order.payment_status = PaymentStatus.REFUNDED

        order.save()
        logger.info("Order %s status updated to %s", order.order_number, new_status)
        return order

    @staticmethod
    def _restore_stock(order):
        for item in order.items.select_related("product", "variant"):
            if item.variant:
                item.variant.stock_quantity += item.quantity
                item.variant.save(update_fields=["stock_quantity", "updated_at"])
                if item.product:
                    ProductService._sync_stock_status(item.product)

    @staticmethod
    def cancel_order(order):
        return OrderService.update_status(order, OrderStatus.CANCELLED)

    @staticmethod
    def mark_payment_received(order):
        order.payment_status = PaymentStatus.PAID
        order.save(update_fields=["payment_status", "updated_at"])
        return order

    @staticmethod
    def get_order_by_number_and_phone(order_number, phone):
        try:
            return Order.objects.prefetch_related("items").get(
                order_number=order_number,
                buyer_phone=phone,
            )
        except Order.DoesNotExist:
            return None

    @staticmethod
    def get_dashboard_stats():
        orders = Order.objects.all()
        return {
            "total_products": Product.objects.count(),
            "total_orders": orders.count(),
            "pending_orders": orders.filter(order_status=OrderStatus.PENDING).count(),
            "total_sales": orders.filter(
                payment_status=PaymentStatus.PAID
            ).aggregate(total=Sum("total"))["total"]
            or Decimal("0"),
            "recent_orders": list(
                orders[:10].values(
                    "id",
                    "order_number",
                    "buyer_name",
                    "buyer_phone",
                    "total",
                    "payment_method",
                    "order_status",
                    "created_at",
                )
            ),
        }

    @staticmethod
    def get_orders(filters=None):
        queryset = Order.objects.prefetch_related("items").all()
        filters = filters or {}

        status = filters.get("status")
        if status:
            queryset = queryset.filter(order_status=status)

        return queryset

    @staticmethod
    def get_order(order_id):
        return Order.objects.prefetch_related("items").filter(pk=order_id).first()
