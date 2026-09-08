from decimal import Decimal

from rest_framework import serializers

from .models import Product, ProductCategory, ProductImage, ProductOption, ProductVariant


class ProductImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ("id", "image", "image_url", "alt_text", "sort_order", "created_at")
        read_only_fields = ("id", "created_at")

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = (
            "id",
            "size",
            "sku",
            "stock_quantity",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class ProductListSerializer(serializers.ModelSerializer):
    primary_image_url = serializers.SerializerMethodField()
    available_sizes = serializers.ListField(read_only=True)
    total_stock = serializers.IntegerField(read_only=True)

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "slug",
            "brand",
            "category",
            "price",
            "color",
            "status",
            "is_featured",
            "primary_image_url",
            "available_sizes",
            "total_stock",
            "created_at",
        )

    def get_primary_image_url(self, obj):
        image = obj.primary_image
        if image and image.image:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(image.image.url)
            return image.image.url
        return None


class ProductDetailSerializer(ProductListSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)

    class Meta(ProductListSerializer.Meta):
        fields = ProductListSerializer.Meta.fields + (
            "description",
            "condition",
            "images",
            "variants",
            "updated_at",
        )


class ProductVariantInputSerializer(serializers.Serializer):
    size = serializers.CharField(max_length=10)
    stock_quantity = serializers.IntegerField(min_value=0, default=0)
    sku = serializers.CharField(max_length=50, required=False, allow_blank=True)
    is_active = serializers.BooleanField(default=True)

    def validate_sku(self, value):
        if value and not all(character.isalnum() or character in "-_" for character in value):
            raise serializers.ValidationError("SKU may contain only letters, numbers, hyphens, and underscores.")
        return value


class ProductOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductOption
        fields = ("id", "option_type", "value", "label", "created_at")
        read_only_fields = ("id", "created_at")

    def validate(self, attrs):
        option_type = attrs.get("option_type", getattr(self.instance, "option_type", None))
        value = attrs.get("value", getattr(self.instance, "value", "")).strip()
        if not value:
            raise serializers.ValidationError({"value": "This field may not be blank."})
        query = ProductOption.objects.filter(option_type=option_type, value__iexact=value)
        if self.instance:
            query = query.exclude(pk=self.instance.pk)
        if query.exists():
            raise serializers.ValidationError({"value": "This option already exists."})
        attrs["value"] = value
        attrs.setdefault("label", value)
        return attrs


class AdminProductSerializer(serializers.ModelSerializer):
    variants = ProductVariantSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    total_stock = serializers.IntegerField(read_only=True)

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "slug",
            "description",
            "brand",
            "category",
            "price",
            "condition",
            "color",
            "status",
            "is_featured",
            "variants",
            "images",
            "total_stock",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "slug", "created_at", "updated_at")


class AdminProductCreateUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True)
    brand = serializers.CharField(max_length=100, required=False, allow_blank=True)
    category = serializers.CharField(max_length=100, required=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal("0.01"))
    condition = serializers.CharField(required=True)
    color = serializers.CharField(max_length=50, required=True)
    status = serializers.CharField(required=False)
    is_featured = serializers.BooleanField(required=False, default=False)
    variants = ProductVariantInputSerializer(many=True, required=False)

    def validate_variants(self, variants):
        sizes = [variant["size"].strip() for variant in variants]
        if any(not size for size in sizes):
            raise serializers.ValidationError("Every variant must have a size.")
        if len(sizes) != len(set(sizes)):
            raise serializers.ValidationError("A product cannot contain the same size twice.")
        for variant, size in zip(variants, sizes):
            variant["size"] = size
        return variants


class CategorySerializer(serializers.Serializer):
    value = serializers.CharField()
    label = serializers.CharField()
