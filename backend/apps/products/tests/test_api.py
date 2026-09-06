import pytest
from rest_framework.test import APIClient

from apps.products.models import ProductStatus


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
