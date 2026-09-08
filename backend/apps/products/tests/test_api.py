import pytest
from rest_framework.test import APIClient

from apps.products.models import ProductOption, ProductOptionType, ProductStatus


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

    def test_admin_can_manage_product_options(self, admin_user):
        client = APIClient()
        client.force_authenticate(user=admin_user)
        response = client.post(
            "/api/v1/admin/options/",
            {"option_type": "BRAND", "value": "Asics", "label": "Asics"},
            format="json",
        )
        assert response.status_code == 201
        option_id = response.data["id"]
        assert ProductOption.objects.filter(pk=option_id).exists()
        response = client.delete(f"/api/v1/admin/options/{option_id}/")
        assert response.status_code == 204

    def test_public_catalogue_options_use_configuration(self):
        ProductOption.objects.create(
            option_type=ProductOptionType.CATEGORY,
            value="TRAIL",
            label="Trail Shoes",
        )
        ProductOption.objects.create(
            option_type=ProductOptionType.BRAND,
            value="Asics",
            label="Asics",
        )
        client = APIClient()
        categories = client.get("/api/v1/categories/")
        brands = client.get("/api/v1/brands/")
        assert categories.status_code == 200
        assert "TRAIL" in {item["value"] for item in categories.data}
        assert brands.status_code == 200
        assert "Asics" in brands.data
