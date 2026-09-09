import pytest
from django.db import IntegrityError
from rest_framework.test import APIClient

from apps.orders.models import Order, OrderStatus, PaymentMethod, PaymentStatus
from apps.products.models import Brand, Category, Color, Condition, Product, ProductStatus, ProductVariant, Size


@pytest.mark.django_db
class TestProductAPI:
    def test_list_published_products(self, product):
        client = APIClient()
        response = client.get("/api/v1/products/")
        assert response.status_code == 200
        assert response.data["count"] >= 1

    def test_product_detail_by_slug(self, product):
        client = APIClient()
        response = client.get(f"/api/v1/products/{product.slug}/")
        assert response.status_code == 200
        assert response.data["name"] == "Nike Air Max"

    def test_admin_requires_auth(self, product):
        client = APIClient()
        response = client.get("/api/v1/admin/products/")
        assert response.status_code == 401

    def test_admin_list_with_auth(self, product, admin_user):
        client = APIClient()
        client.force_authenticate(user=admin_user)
        response = client.get("/api/v1/admin/products/")
        assert response.status_code == 200

    def test_admin_can_manage_brands(self, admin_user):
        client = APIClient()
        client.force_authenticate(user=admin_user)
        response = client.post(
            "/api/v1/admin/configuration/brands/",
            {"name": "Asics"},
            format="json",
        )
        assert response.status_code == 201
        option_id = response.data["id"]
        assert Brand.objects.filter(pk=option_id).exists()
        response = client.delete(f"/api/v1/admin/configuration/brands/{option_id}/")
        assert response.status_code == 204

    def test_public_catalogue_options_use_configuration(self):
        Category.objects.create(value="TRAIL", name="Trail Shoes")
        Brand.objects.create(name="Asics")
        client = APIClient()
        categories = client.get("/api/v1/categories/")
        brands = client.get("/api/v1/brands/")
        assert categories.status_code == 200
        assert "TRAIL" in {item["value"] for item in categories.data}
        assert brands.status_code == 200
        assert "Asics" in {item["name"] for item in brands.data}

    def test_list_filters_are_combined_on_backend(self):
        brand, _ = Brand.objects.get_or_create(name="Nike - combined filter")
        category, _ = Category.objects.get_or_create(value="SNEAKERS_FILTER", name="Sneakers Filter")
        condition, _ = Condition.objects.get_or_create(value="NEW_FILTER", name="New Filter")
        color, _ = Color.objects.get_or_create(name="Black Filter")
        size_42, _ = Size.objects.get_or_create(value="42-combined")
        matching = Product.objects.create(
            name="Nike Air Max",
            brand=brand,
            category=category,
            price=850,
            status=ProductStatus.PUBLISHED,
            condition=condition,
            color=color,
        )
        ProductVariant.objects.create(product=matching, size=size_42, stock_quantity=4, sku="")

        other = Product.objects.create(
            name="Adidas Runner",
            brand=Brand.objects.get_or_create(name="Adidas")[0],
            category=category,
            price=700,
            status=ProductStatus.PUBLISHED,
            condition=condition,
            color=color,
        )
        ProductVariant.objects.create(product=other, size=size_42, stock_quantity=1, sku="AD-1")

        response = APIClient().get(
            "/api/v1/products/",
            {
                "brand": brand.name,
                "category": category.value,
                "condition": condition.value,
                "color": color.name,
                "size": size_42.value,
                "min_price": 800,
                "max_price": 900,
            },
        )

        assert response.status_code == 200
        assert response.data["count"] == 1
        assert response.data["results"][0]["name"] == "Nike Air Max"

    def test_empty_sku_is_allowed_and_duplicate_nonempty_sku_is_not(self):
        product_a = Product.objects.create(
            name="Empty SKU A",
            price=100,
            status=ProductStatus.PUBLISHED,
            brand=Brand.objects.create(name="Brand A sku"),
            category=Category.objects.create(value="SNEAKERS_SKU", name="Sneakers SKU"),
            condition=Condition.objects.create(value="NEW_SKU", name="New SKU"),
            color=Color.objects.create(name="Red SKU"),
        )
        product_b = Product.objects.create(
            name="Empty SKU B",
            price=120,
            status=ProductStatus.PUBLISHED,
            brand=Brand.objects.create(name="Brand B sku"),
            category=Category.objects.create(value="RUNNING_SKU", name="Running SKU"),
            condition=Condition.objects.create(value="USED_SKU", name="Used SKU"),
            color=Color.objects.create(name="Blue SKU"),
        )

        ProductVariant.objects.create(product=product_a, size=Size.objects.create(value="41-sku"), stock_quantity=2, sku="")
        ProductVariant.objects.create(product=product_b, size=Size.objects.create(value="42-sku"), stock_quantity=3, sku="")

        ProductVariant.objects.create(product=product_a, size=Size.objects.create(value="43-sku"), stock_quantity=1, sku="ABC-123")

        with pytest.raises(IntegrityError):
            ProductVariant.objects.create(product=product_b, size=Size.objects.create(value="44-sku"), stock_quantity=1, sku="ABC-123")


@pytest.mark.django_db
class TestAdminOrdersAPI:
    def test_admin_order_search_and_payment_filter_work(self):
        order = Order.objects.create(
            buyer_name="Mabel Boateng",
            buyer_phone="0240000000",
            delivery_address="Accra",
            payment_method=PaymentMethod.PAY_ON_DELIVERY,
            payment_status=PaymentStatus.PAID,
            order_status=OrderStatus.PENDING,
            subtotal="100.00",
            total="130.00",
        )
        other = Order.objects.create(
            buyer_name="Kwame Mensah",
            buyer_phone="0241111111",
            delivery_address="Kumasi",
            payment_method=PaymentMethod.MOMO,
            payment_status=PaymentStatus.PENDING,
            order_status=OrderStatus.CONFIRMED,
            subtotal="200.00",
            total="230.00",
        )

        client = APIClient()
        from django.contrib.auth import get_user_model

        User = get_user_model()
        admin = User.objects.create_superuser(email='admin-orders@test.com', password='pass123')
        client.force_authenticate(user=admin)

        response = client.get("/api/v1/admin/orders/", {"search": "mabel", "payment_status": "PAID"})
        assert response.status_code == 200
        assert response.data["count"] == 1
        assert response.data["results"][0]["buyer_name"] == "Mabel Boateng"

        response = client.get("/api/v1/admin/orders/", {"payment_status": "PENDING"})
        assert response.status_code == 200
        assert response.data["count"] == 1
        assert response.data["results"][0]["buyer_name"] == "Kwame Mensah"
