import pytest
from django.contrib.auth import get_user_model

from apps.common.models import StoreSettings
from apps.products.models import Product, ProductStatus, ProductVariant

User = get_user_model()


@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser(
        email="admin@test.com",
        password="testpass123",
    )


@pytest.fixture
def store_settings(db):
    return StoreSettings.load()


@pytest.fixture
def product(db):
    product = Product.objects.create(
        name="Nike Air Max",
        brand="Nike",
        category="SNEAKERS",
        price=850,
        status=ProductStatus.PUBLISHED,
        color="Black",
    )
    ProductVariant.objects.create(product=product, size="42", stock_quantity=5)
    ProductVariant.objects.create(product=product, size="43", stock_quantity=3)
    return product
