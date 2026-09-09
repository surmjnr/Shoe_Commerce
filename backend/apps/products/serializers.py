from decimal import Decimal

from rest_framework import serializers

from .models import Brand, Category, Color, Condition, Product, ProductImage, ProductVariant, Size


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
    brand = serializers.CharField(source="brand.name", read_only=True, allow_null=True)
    category = serializers.CharField(source="category.name", read_only=True, allow_null=True)
    color = serializers.CharField(source="color.name", read_only=True, allow_null=True)
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
    variants = serializers.SerializerMethodField()

    class Meta(ProductListSerializer.Meta):
        fields = ProductListSerializer.Meta.fields + (
            "description",
            "condition",
            "images",
            "variants",
            "updated_at",
        )

    def get_variants(self, obj):
        return [
            {
                "id": variant.id,
                "size": variant.size.value if variant.size else "",
                "sku": variant.sku,
                "stock_quantity": variant.stock_quantity,
                "is_active": variant.is_active,
                "created_at": variant.created_at,
                "updated_at": variant.updated_at,
            }
            for variant in obj.variants.all()
        ]


class ProductVariantInputSerializer(serializers.Serializer):
    size = serializers.PrimaryKeyRelatedField(queryset=Size.objects.all())
    stock_quantity = serializers.IntegerField(min_value=0, default=0)
    sku = serializers.CharField(max_length=50, required=False, allow_blank=True)
    is_active = serializers.BooleanField(default=True)

    def validate_sku(self, value):
        if value and not all(character.isalnum() or character in "-_" for character in value):
            raise serializers.ValidationError("SKU may contain only letters, numbers, hyphens, and underscores.")
        return value


class AdminProductSerializer(serializers.ModelSerializer):
    variants = ProductVariantSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    total_stock = serializers.IntegerField(read_only=True)
    primary_image_url = serializers.SerializerMethodField()
    brand_name = serializers.CharField(source="brand.name", read_only=True, allow_null=True)
    category_name = serializers.CharField(source="category.name", read_only=True, allow_null=True)
    condition_name = serializers.CharField(source="condition.name", read_only=True, allow_null=True)
    color_name = serializers.CharField(source="color.name", read_only=True, allow_null=True)

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "slug",
            "description",
            "brand",
            "brand_name",
            "category",
            "category_name",
            "price",
            "condition",
            "condition_name",
            "color",
            "color_name",
            "status",
            "is_featured",
            "primary_image_url",
            "variants",
            "images",
            "total_stock",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "slug", "created_at", "updated_at")

    def get_primary_image_url(self, obj):
        image = obj.primary_image
        if image and image.image:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(image.image.url)
            return image.image.url
        return None


class AdminProductCreateUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True)
    brand = serializers.PrimaryKeyRelatedField(queryset=Brand.objects.all(), required=False, allow_null=True)
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), required=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal("0.01"))
    condition = serializers.PrimaryKeyRelatedField(queryset=Condition.objects.all(), required=True)
    color = serializers.PrimaryKeyRelatedField(queryset=Color.objects.all(), required=True)
    status = serializers.CharField(required=False)
    is_featured = serializers.BooleanField(required=False, default=False)
    variants = ProductVariantInputSerializer(many=True, required=False)

    def validate_variants(self, variants):
        sizes = [variant["size"].pk for variant in variants]
        if any(not size for size in sizes):
            raise serializers.ValidationError("Every variant must have a size.")
        if len(sizes) != len(set(sizes)):
            raise serializers.ValidationError("A product cannot contain the same size twice.")
        return variants


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ("id", "name", "created_at", "updated_at")


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "value", "name", "created_at", "updated_at")


class ConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Condition
        fields = ("id", "value", "name", "created_at", "updated_at")


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ("id", "name", "created_at", "updated_at")


class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = ("id", "value", "created_at", "updated_at")
