from rest_framework import serializers

from .models import Product, ProductCategory, ProductImage, ProductVariant


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
    category = serializers.ChoiceField(choices=ProductCategory.choices)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0)
    condition = serializers.CharField(required=False)
    color = serializers.CharField(max_length=50, required=False, allow_blank=True)
    status = serializers.CharField(required=False)
    is_featured = serializers.BooleanField(required=False, default=False)
    variants = ProductVariantInputSerializer(many=True, required=False)


class CategorySerializer(serializers.Serializer):
    value = serializers.CharField()
    label = serializers.CharField()
