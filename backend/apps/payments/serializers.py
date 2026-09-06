from rest_framework import serializers


class PaymentInitializeSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    phone = serializers.CharField(max_length=20)
