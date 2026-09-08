from django.db import models
from django.utils.text import slugify


class ProductStatus(models.TextChoices):
    DRAFT = "DRAFT", "Draft"
    PUBLISHED = "PUBLISHED", "Published"
    HIDDEN = "HIDDEN", "Hidden"
    OUT_OF_STOCK = "OUT_OF_STOCK", "Out of Stock"


class ConfigurationBase(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Brand(ConfigurationBase):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Category(ConfigurationBase):
    value = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Condition(ConfigurationBase):
    value = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Color(ConfigurationBase):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Size(ConfigurationBase):
    value = models.CharField(max_length=20, unique=True)

    class Meta:
        ordering = ["value"]

    def __str__(self):
        return self.value


class Product(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField(blank=True)
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, blank=True, null=True, related_name="products")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, blank=True, null=True, related_name="products")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    condition = models.ForeignKey(Condition, on_delete=models.PROTECT, blank=True, null=True, related_name="products")
    color = models.ForeignKey(Color, on_delete=models.PROTECT, blank=True, null=True, related_name="products")
    status = models.CharField(
        max_length=20, choices=ProductStatus.choices, default=ProductStatus.DRAFT
    )
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "-created_at"]),
            models.Index(fields=["category"]),
            models.Index(fields=["brand"]),
            models.Index(fields=["slug"]),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def total_stock(self):
        return self.variants.filter(is_active=True).aggregate(
            total=models.Sum("stock_quantity")
        )["total"] or 0

    @property
    def available_sizes(self):
        return list(
            self.variants.filter(is_active=True, stock_quantity__gt=0)
            .values_list("size__value", flat=True)
            .order_by("size")
        )

    @property
    def primary_image(self):
        return self.images.order_by("sort_order").first()


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to="products/")
    alt_text = models.CharField(max_length=255, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sort_order", "created_at"]

    def __str__(self):
        return f"{self.product.name} - Image {self.sort_order}"


class ProductVariant(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="variants"
    )
    size = models.ForeignKey(Size, on_delete=models.PROTECT, null=True, related_name="variants")
    sku = models.CharField(max_length=50, blank=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["product", "size"]
        ordering = ["size"]

    def __str__(self):
        return f"{self.product.name} - Size {self.size.value if self.size else 'Unknown'}"
