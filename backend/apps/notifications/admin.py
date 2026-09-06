from django.contrib import admin

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("type", "recipient", "order", "status", "attempts", "sent_at", "created_at")
    list_filter = ("type", "status")
    search_fields = ("recipient", "order__order_number")
    readonly_fields = ("created_at", "updated_at", "sent_at")
