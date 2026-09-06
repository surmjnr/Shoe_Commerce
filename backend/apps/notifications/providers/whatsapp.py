import logging
import uuid

import requests
from django.conf import settings

from .base import WhatsAppProvider, WhatsAppSendResult

logger = logging.getLogger(__name__)


class WhatsAppBusinessProvider(WhatsAppProvider):
    def __init__(self):
        self.api_url = settings.WHATSAPP_API_URL
        self.access_token = settings.WHATSAPP_ACCESS_TOKEN
        self.phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID

    def send_message(self, to, message):
        if not self.access_token or not self.phone_number_id:
            logger.warning("WhatsApp not configured, using mock behavior")
            return WhatsAppSendResult(
                success=True,
                message_id=f"unconfigured-{uuid.uuid4().hex[:8]}",
            )

        url = f"{self.api_url}/{self.phone_number_id}/messages"
        payload = {
            "messaging_product": "whatsapp",
            "to": to.replace("+", "").replace(" ", ""),
            "type": "text",
            "text": {"body": message},
        }

        try:
            response = requests.post(
                url,
                json=payload,
                headers={"Authorization": f"Bearer {self.access_token}"},
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
            message_id = data.get("messages", [{}])[0].get("id", "")
            return WhatsAppSendResult(success=True, message_id=message_id)
        except requests.RequestException as e:
            logger.error("WhatsApp send failed: %s", e)
            return WhatsAppSendResult(success=False, error=str(e))
