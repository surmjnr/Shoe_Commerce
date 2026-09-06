from django.conf import settings
from django.db import models


class StoreSettings(models.Model):
    """Singleton model for store/business settings."""

    business_name = models.CharField(max_length=255, default="Your Shoe Store")
    logo = models.ImageField(upload_to="store/", blank=True, null=True)
    description = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    whatsapp_number = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    delivery_information = models.TextField(blank=True)
    payment_information = models.TextField(blank=True)
    currency = models.CharField(max_length=3, default="GHS")
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=30)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Store Settings"
        verbose_name_plural = "Store Settings"

    def __str__(self):
        return self.business_name

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(
            pk=1,
            defaults={
                "business_name": "Your Shoe Store",
                "currency": settings.DEFAULT_CURRENCY,
                "delivery_fee": settings.DEFAULT_DELIVERY_FEE,
            },
        )
        return obj
