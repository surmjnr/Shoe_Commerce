import logging
import uuid

from .base import WhatsAppProvider, WhatsAppSendResult

logger = logging.getLogger(__name__)


class MockWhatsAppProvider(WhatsAppProvider):
    def send_message(self, to, message):
        message_id = f"mock-{uuid.uuid4().hex[:8]}"
        logger.info("Mock WhatsApp to %s: %s", to, message[:100])
        return WhatsAppSendResult(success=True, message_id=message_id)
