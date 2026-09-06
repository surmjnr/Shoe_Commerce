from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class PaymentInitResult:
    success: bool
    reference: str
    checkout_url: str | None = None
    message: str = ""
    metadata: dict | None = None


@dataclass
class PaymentVerifyResult:
    success: bool
    status: str
    reference: str
    message: str = ""
    metadata: dict | None = None


class PaymentProvider(ABC):
    @abstractmethod
    def initialize_payment(
        self, order, phone: str, amount, metadata: dict | None = None
    ) -> PaymentInitResult:
        pass

    @abstractmethod
    def verify_payment(self, reference: str) -> PaymentVerifyResult:
        pass

    @abstractmethod
    def handle_webhook(self, payload: dict, headers: dict | None = None) -> PaymentVerifyResult:
        pass
