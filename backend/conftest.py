import pytest
from django.contrib.auth import get_user_model

from apps.common.models import StoreSettings
from apps.products.models import Brand, Category, Color, Condition, Product, ProductStatus, ProductVariant, Size

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
    brand, _ = Brand.objects.get_or_create(name="Nike")
    category, _ = Category.objects.get_or_create(value="SNEAKERS", defaults={"name": "Sneakers"})
    condition, _ = Condition.objects.get_or_create(value="NEW", defaults={"name": "New"})
    color, _ = Color.objects.get_or_create(name="Black")
    size_42, _ = Size.objects.get_or_create(value="42")
    size_43, _ = Size.objects.get_or_create(value="43")
    product = Product.objects.create(
        name="Nike Air Max",
        brand=brand,
        category=category,
        price=850,
        status=ProductStatus.PUBLISHED,
        condition=condition,
        color=color,
    )
    ProductVariant.objects.create(product=product, size=size_42, stock_quantity=5)
    ProductVariant.objects.create(product=product, size=size_43, stock_quantity=3)
    return product
