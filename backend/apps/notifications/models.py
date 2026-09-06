from django.db import models


class NotificationType(models.TextChoices):
    ORDER_CREATED = "ORDER_CREATED", "Order Created"
    ORDER_STATUS = "ORDER_STATUS", "Order Status Update"
    PAYMENT = "PAYMENT", "Payment Update"


class NotificationStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    SENT = "SENT", "Sent"
    FAILED = "FAILED", "Failed"
    RETRYING = "RETRYING", "Retrying"


class Notification(models.Model):
    type = models.CharField(max_length=30, choices=NotificationType.choices)
    recipient = models.CharField(max_length=50)
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="notifications",
        null=True,
        blank=True,
    )
    message = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=NotificationStatus.choices,
        default=NotificationStatus.PENDING,
    )
    attempts = models.PositiveIntegerField(default=0)
    last_error = models.TextField(blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.type} to {self.recipient} - {self.status}"
