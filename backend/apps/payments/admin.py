from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("order", "provider", "amount", "status", "provider_reference", "created_at")
    list_filter = ("status", "provider")
    search_fields = ("order__order_number", "provider_reference")
    readonly_fields = ("created_at", "updated_at")
