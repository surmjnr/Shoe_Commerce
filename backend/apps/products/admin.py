from django.contrib import admin

from .models import Brand, Category, Color, Condition, Product, ProductImage, ProductVariant, Size


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "brand",
        "category",
        "price",
        "status",
        "is_featured",
        "created_at",
    )
    list_filter = ("status", "category", "brand", "is_featured")
    search_fields = ("name", "brand__name", "category__name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at", "updated_at")
    inlines = [ProductImageInline, ProductVariantInline]


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("product", "sort_order", "alt_text", "created_at")
    list_filter = ("product",)


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ("product", "size", "stock_quantity", "is_active", "sku")
    list_filter = ("is_active", "product")
    search_fields = ("product__name", "sku", "size__value")


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at", "updated_at")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "value", "created_at", "updated_at")
    search_fields = ("name", "value")
    ordering = ("name",)


@admin.register(Condition)
class ConditionAdmin(admin.ModelAdmin):
    list_display = ("name", "value", "created_at", "updated_at")
    search_fields = ("name", "value")
    ordering = ("name",)


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at", "updated_at")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ("value", "created_at", "updated_at")
    search_fields = ("value",)
    ordering = ("value",)
