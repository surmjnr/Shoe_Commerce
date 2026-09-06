from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class WhatsAppSendResult:
    success: bool
    message_id: str = ""
    error: str = ""


class WhatsAppProvider(ABC):
    @abstractmethod
    def send_message(self, to: str, message: str) -> WhatsAppSendResult:
        pass
