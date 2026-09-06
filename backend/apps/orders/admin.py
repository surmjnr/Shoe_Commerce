from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product_name", "size", "quantity", "unit_price", "subtotal")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_number",
        "buyer_name",
        "buyer_phone",
        "total",
        "payment_method",
        "payment_status",
        "order_status",
        "created_at",
    )
    list_filter = ("order_status", "payment_status", "payment_method")
    search_fields = ("order_number", "buyer_name", "buyer_phone")
    readonly_fields = ("order_number", "created_at", "updated_at")
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product_name", "size", "quantity", "unit_price", "subtotal")
    search_fields = ("order__order_number", "product_name")
