import logging
from datetime import datetime

from django.conf import settings
from django.utils import timezone

from apps.common.models import StoreSettings
from apps.orders.models import Order

from .models import Notification, NotificationStatus, NotificationType
from .providers.base import WhatsAppProvider
from .providers.mock import MockWhatsAppProvider
from .providers.whatsapp import WhatsAppBusinessProvider

logger = logging.getLogger(__name__)

MAX_RETRY_ATTEMPTS = 5


def get_whatsapp_provider() -> WhatsAppProvider:
    provider = settings.WHATSAPP_PROVIDER.lower()
    if provider == "whatsapp":
        return WhatsAppBusinessProvider()
    return MockWhatsAppProvider()


class WhatsAppService:
    @staticmethod
    def format_order_message(order: Order) -> str:
        store = StoreSettings.load()
        items_text = ""
        for item in order.items.all():
            items_text += (
                f"\n{item.product_name}\n"
                f"Size: {item.size}\n"
                f"Qty: {item.quantity}\n"
            )

        frontend_url = settings.FRONTEND_URL
        return (
            f"🛍️ NEW ORDER #{order.order_number}\n\n"
            f"Customer:\n{order.buyer_name}\n\n"
            f"Phone:\n{order.buyer_phone}\n\n"
            f"Product:{items_text}\n"
            f"Payment:\n{order.get_payment_method_display()}\n\n"
            f"Delivery:\n{order.delivery_address}\n\n"
            f"Total:\n{store.currency} {order.total}\n\n"
            f"View Order:\n{frontend_url}/admin/orders/{order.id}"
        )

    @staticmethod
    def send_order_notification(order_id: int):
        try:
            order = Order.objects.prefetch_related("items").get(pk=order_id)
        except Order.DoesNotExist:
            logger.error("Order %s not found for notification", order_id)
            return

        store = StoreSettings.load()
        recipient = store.whatsapp_number or store.phone

        if not recipient:
            logger.warning("No WhatsApp number configured")
            return

        message = WhatsAppService.format_order_message(order)

        notification = Notification.objects.create(
            type=NotificationType.ORDER_CREATED,
            recipient=recipient,
            order=order,
            message=message,
            status=NotificationStatus.PENDING,
        )

        WhatsAppService._send_notification(notification)

    @staticmethod
    def _send_notification(notification: Notification):
        provider = get_whatsapp_provider()
        notification.attempts += 1

        result = provider.send_message(notification.recipient, notification.message)

        if result.success:
            notification.status = NotificationStatus.SENT
            notification.sent_at = timezone.now()
            notification.last_error = ""
            logger.info("Notification sent for order %s", notification.order_id)
        else:
            notification.status = NotificationStatus.FAILED
            notification.last_error = result.error
            logger.error(
                "Notification failed for order %s: %s",
                notification.order_id,
                result.error,
            )

        notification.save()

    @staticmethod
    def retry_failed_notifications():
        failed = Notification.objects.filter(
            status=NotificationStatus.FAILED,
            attempts__lt=MAX_RETRY_ATTEMPTS,
        )

        for notification in failed:
            notification.status = NotificationStatus.RETRYING
            notification.save(update_fields=["status", "updated_at"])
            WhatsAppService._send_notification(notification)
