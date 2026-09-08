from django.urls import path

from .views import (
    AdminProductDetailView,
    AdminProductImageDeleteView,
    AdminProductImageUploadView,
    AdminProductOptionDetailView,
    AdminProductOptionListCreateView,
    AdminProductListCreateView,
    BrandListView,
    CategoryListView,
    FeaturedProductsView,
    NewArrivalsView,
    ProductDetailView,
    ProductListView,
)

urlpatterns = [
    path("products/", ProductListView.as_view(), name="product-list"),
    path("products/featured/", FeaturedProductsView.as_view(), name="featured-products"),
    path("products/new/", NewArrivalsView.as_view(), name="new-arrivals"),
    path("products/<slug:slug>/", ProductDetailView.as_view(), name="product-detail"),
    path("categories/", CategoryListView.as_view(), name="category-list"),
    path("brands/", BrandListView.as_view(), name="brand-list"),
    path("admin/products/", AdminProductListCreateView.as_view(), name="admin-product-list"),
    path(
        "admin/products/<int:pk>/",
        AdminProductDetailView.as_view(),
        name="admin-product-detail",
    ),
    path(
        "admin/products/<int:pk>/images/",
        AdminProductImageUploadView.as_view(),
        name="admin-product-images",
    ),
    path(
        "admin/products/<int:pk>/images/<int:image_id>/",
        AdminProductImageDeleteView.as_view(),
        name="admin-product-image-delete",
    ),
    path("admin/options/", AdminProductOptionListCreateView.as_view(), name="admin-option-list"),
    path("admin/options/<int:pk>/", AdminProductOptionDetailView.as_view(), name="admin-option-detail"),
]
