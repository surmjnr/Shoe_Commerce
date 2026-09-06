import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestAdminAuth:
    def test_login_success(self, admin_user):
        client = APIClient()
        response = client.post(
            "/api/v1/admin/auth/login/",
            {"email": "admin@test.com", "password": "testpass123"},
        )
        assert response.status_code == 200
        assert "access" in response.data
        assert "refresh" in response.data

    def test_login_failure(self, admin_user):
        client = APIClient()
        response = client.post(
            "/api/v1/admin/auth/login/",
            {"email": "admin@test.com", "password": "wrongpassword"},
        )
        assert response.status_code == 401
