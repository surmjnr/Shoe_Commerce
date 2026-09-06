from rest_framework import serializers

from .models import StoreSettings


class StoreSettingsSerializer(serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()

    class Meta:
        model = StoreSettings
        fields = (
            "id",
            "business_name",
            "logo",
            "logo_url",
            "description",
            "phone",
            "whatsapp_number",
            "email",
            "address",
            "delivery_information",
            "payment_information",
            "currency",
            "delivery_fee",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def get_logo_url(self, obj):
        if obj.logo:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.logo.url)
            return obj.logo.url
        return None
