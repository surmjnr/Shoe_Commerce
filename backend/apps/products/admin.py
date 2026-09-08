from django.contrib import admin

from .models import Product, ProductImage, ProductOption, ProductVariant


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
    search_fields = ("name", "brand", "slug")
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
    search_fields = ("product__name", "sku", "size")


@admin.register(ProductOption)
class ProductOptionAdmin(admin.ModelAdmin):
    list_display = ("label", "option_type", "value", "created_at")
    list_filter = ("option_type",)
    search_fields = ("label", "value")
    ordering = ("option_type", "label")
