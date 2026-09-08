from django.db import transaction

from .models import Product, ProductImage, ProductStatus, ProductVariant


class ProductService:
    @staticmethod
    @transaction.atomic
    def create_product(data, variants_data=None, images=None):
        variants_data = variants_data or []
        product = Product.objects.create(**data)

        for variant_data in variants_data:
            ProductVariant.objects.create(product=product, **variant_data)

        if images:
            for idx, image in enumerate(images):
                ProductImage.objects.create(
                    product=product,
                    image=image,
                    sort_order=idx,
                    alt_text=product.name,
                )

        ProductService._sync_stock_status(product)
        return product

    @staticmethod
    @transaction.atomic
    def update_product(product, data, variants_data=None):
        for key, value in data.items():
            setattr(product, key, value)
        product.save()

        if variants_data is not None:
            existing_sizes = set()
            for variant_data in variants_data:
                size = variant_data["size"]
                existing_sizes.add(size.pk)
                ProductVariant.objects.update_or_create(
                    product=product,
                    size=size,
                    defaults={
                        "stock_quantity": variant_data.get("stock_quantity", 0),
                        "sku": variant_data.get("sku", ""),
                        "is_active": variant_data.get("is_active", True),
                    },
                )
            product.variants.exclude(size_id__in=existing_sizes).delete()

        ProductService._sync_stock_status(product)
        return product

    @staticmethod
    def update_inventory(product, size, quantity):
        variant = product.variants.get(size__value=size)
        variant.stock_quantity = max(0, quantity)
        variant.save()
        ProductService._sync_stock_status(product)
        return variant

    @staticmethod
    def publish_product(product):
        product.status = ProductStatus.PUBLISHED
        product.save()
        ProductService._sync_stock_status(product)
        return product

    @staticmethod
    def hide_product(product):
        product.status = ProductStatus.HIDDEN
        product.save()
        return product

    @staticmethod
    def delete_product(product):
        product.delete()

    @staticmethod
    def add_images(product, images, start_order=0):
        created = []
        for idx, image in enumerate(images):
            created.append(
                ProductImage.objects.create(
                    product=product,
                    image=image,
                    sort_order=start_order + idx,
                    alt_text=product.name,
                )
            )
        return created

    @staticmethod
    def delete_image(image):
        image.delete()

    @staticmethod
    def reorder_images(product, image_ids):
        for order, image_id in enumerate(image_ids):
            ProductImage.objects.filter(pk=image_id, product=product).update(
                sort_order=order
            )

    @staticmethod
    def _sync_stock_status(product):
        if product.status in (ProductStatus.DRAFT, ProductStatus.HIDDEN):
            return
        total = product.total_stock
        if total == 0 and product.status == ProductStatus.PUBLISHED:
            product.status = ProductStatus.OUT_OF_STOCK
            product.save(update_fields=["status", "updated_at"])
        elif total > 0 and product.status == ProductStatus.OUT_OF_STOCK:
            product.status = ProductStatus.PUBLISHED
            product.save(update_fields=["status", "updated_at"])

    @staticmethod
    def get_inventory(product):
        return list(
            product.variants.filter(is_active=True).values(
                "size__value", "stock_quantity", "sku"
            )
        )
