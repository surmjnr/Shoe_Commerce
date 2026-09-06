import logging

from celery import shared_task

from .services import WhatsAppService

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_order_notification_task(self, order_id):
    try:
        WhatsAppService.send_order_notification(order_id)
    except Exception as exc:
        logger.error("Notification task failed: %s", exc)
        raise self.retry(exc=exc) from exc


@shared_task
def retry_failed_notifications_task():
    WhatsAppService.retry_failed_notifications()
