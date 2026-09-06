from django.db.models import Prefetch, Q

from .models import Product, ProductStatus, ProductVariant


def get_published_products_queryset():
    return (
        Product.objects.filter(status=ProductStatus.PUBLISHED)
        .prefetch_related(
            Prefetch(
                "variants",
                queryset=ProductVariant.objects.filter(is_active=True),
            ),
            "images",
        )
        .select_related()
    )


def get_product_by_slug(slug):
    return (
        Product.objects.filter(
            slug=slug,
            status=ProductStatus.PUBLISHED,
        )
        .prefetch_related(
            Prefetch(
                "variants",
                queryset=ProductVariant.objects.filter(is_active=True),
            ),
            "images",
        )
        .first()
    )


def filter_products(queryset, params):
    category = params.get("category")
    brand = params.get("brand")
    size = params.get("size")
    min_price = params.get("min_price")
    max_price = params.get("max_price")
    search = params.get("search")
    featured = params.get("featured")
    ordering = params.get("ordering", "-created_at")

    if category:
        queryset = queryset.filter(category=category)
    if brand:
        queryset = queryset.filter(brand__iexact=brand)
    if size:
        queryset = queryset.filter(
            variants__size=size,
            variants__is_active=True,
            variants__stock_quantity__gt=0,
        ).distinct()
    if min_price:
        queryset = queryset.filter(price__gte=min_price)
    if max_price:
        queryset = queryset.filter(price__lte=max_price)
    if search:
        queryset = queryset.filter(
            Q(name__icontains=search)
            | Q(brand__icontains=search)
            | Q(description__icontains=search)
            | Q(category__icontains=search)
        )
    if featured and featured.lower() in ("true", "1"):
        queryset = queryset.filter(is_featured=True)

    allowed_orderings = {
        "created_at": "created_at",
        "-created_at": "-created_at",
        "price": "price",
        "-price": "-price",
    }
    order_field = allowed_orderings.get(ordering, "-created_at")
    return queryset.order_by(order_field)


def get_admin_products_queryset():
    return Product.objects.prefetch_related("variants", "images").all()


def get_featured_products(limit=8):
    return get_published_products_queryset().filter(is_featured=True)[:limit]


def get_new_arrivals(limit=8):
    return get_published_products_queryset()[:limit]


def get_distinct_brands():
    return (
        Product.objects.filter(status=ProductStatus.PUBLISHED)
        .exclude(brand="")
        .values_list("brand", flat=True)
        .distinct()
        .order_by("brand")
    )
