from rest_framework import serializers

from .models import Order, OrderItem, OrderStatus, PaymentMethod, PaymentStatus


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = (
            "id",
            "product_name",
            "size",
            "quantity",
            "unit_price",
            "subtotal",
        )


class OrderCreateItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    variant_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)


class OrderCreateSerializer(serializers.Serializer):
    buyer_name = serializers.CharField(max_length=255)
    buyer_phone = serializers.CharField(max_length=20)
    delivery_address = serializers.CharField()
    delivery_notes = serializers.CharField(required=False, allow_blank=True)
    payment_method = serializers.ChoiceField(choices=PaymentMethod.choices)
    items = OrderCreateItemSerializer(many=True, allow_empty=False)


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "order_number",
            "buyer_name",
            "buyer_phone",
            "delivery_address",
            "delivery_notes",
            "payment_method",
            "payment_status",
            "order_status",
            "subtotal",
            "delivery_fee",
            "total",
            "items",
            "created_at",
            "updated_at",
        )


class OrderTrackingSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status_timeline = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = (
            "order_number",
            "order_status",
            "payment_method",
            "payment_status",
            "total",
            "items",
            "status_timeline",
            "created_at",
            "updated_at",
        )

    def get_status_timeline(self, obj):
        statuses = [
            OrderStatus.PENDING,
            OrderStatus.CONFIRMED,
            OrderStatus.PROCESSING,
            OrderStatus.OUT_FOR_DELIVERY,
            OrderStatus.DELIVERED,
        ]
        if obj.order_status == OrderStatus.CANCELLED:
            return [
                {"status": s, "completed": False, "current": False}
                for s in statuses
            ] + [{"status": OrderStatus.CANCELLED, "completed": True, "current": True}]

        current_idx = (
            statuses.index(obj.order_status)
            if obj.order_status in statuses
            else -1
        )
        timeline = []
        for idx, status in enumerate(statuses):
            timeline.append(
                {
                    "status": status,
                    "completed": idx <= current_idx,
                    "current": idx == current_idx,
                }
            )
        return timeline


class OrderTrackLookupSerializer(serializers.Serializer):
    order_number = serializers.CharField()
    phone = serializers.CharField()


class OrderStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=OrderStatus.choices)


class AdminOrderSerializer(OrderSerializer):
    pass
