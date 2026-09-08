from rest_framework import generics, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsAdminUser

from .models import Product, ProductCategory, ProductImage, ProductOption, ProductOptionType
from .selectors import (
    filter_products,
    get_admin_products_queryset,
    get_distinct_brands,
    get_featured_products,
    get_new_arrivals,
    get_product_by_slug,
    get_published_products_queryset,
)
from .serializers import (
    AdminProductCreateUpdateSerializer,
    AdminProductSerializer,
    CategorySerializer,
    ProductDetailSerializer,
    ProductListSerializer,
    ProductOptionSerializer,
)
from .services import ProductService


class ProductListView(generics.ListAPIView):
    serializer_class = ProductListSerializer

    def get_queryset(self):
        queryset = get_published_products_queryset()
        return filter_products(queryset, self.request.query_params)


class ProductDetailView(generics.RetrieveAPIView):
    serializer_class = ProductDetailSerializer
    lookup_field = "slug"

    def get_object(self):
        product = get_product_by_slug(self.kwargs["slug"])
        if not product:
            from rest_framework.exceptions import NotFound

            raise NotFound("Product not found.")
        return product


class CategoryListView(APIView):
    def get(self, request):
        configured = ProductOption.objects.filter(option_type=ProductOptionType.CATEGORY)
        categories = list(configured.values("value", "label"))
        if not categories:
            categories = [
                {"value": choice[0], "label": choice[1]}
                for choice in ProductCategory.choices
            ]
        return Response(CategorySerializer(categories, many=True).data)


class BrandListView(APIView):
    def get(self, request):
        configured = list(
            ProductOption.objects.filter(option_type=ProductOptionType.BRAND).values_list(
                "value", flat=True
            )
        )
        return Response(configured or list(get_distinct_brands()))


class FeaturedProductsView(generics.ListAPIView):
    serializer_class = ProductListSerializer

    def get_queryset(self):
        return get_featured_products()


class NewArrivalsView(generics.ListAPIView):
    serializer_class = ProductListSerializer

    def get_queryset(self):
        return get_new_arrivals()


class AdminProductListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AdminProductCreateUpdateSerializer
        return AdminProductSerializer

    def get_queryset(self):
        return get_admin_products_queryset()

    def create(self, request, *args, **kwargs):
        serializer = AdminProductCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        variants = data.pop("variants", [])
        product = ProductService.create_product(data, variants)
        return Response(
            AdminProductSerializer(product, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


class AdminProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    queryset = get_admin_products_queryset()
    serializer_class = AdminProductSerializer

    def update(self, request, *args, **kwargs):
        product = self.get_object()
        serializer = AdminProductCreateUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        variants = data.pop("variants", None)
        product = ProductService.update_product(product, data, variants)
        return Response(
            AdminProductSerializer(product, context={"request": request}).data
        )

    def destroy(self, request, *args, **kwargs):
        product = self.get_object()
        ProductService.delete_product(product)
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminProductImageUploadView(APIView):
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        images = request.FILES.getlist("images")
        if not images:
            return Response(
                {"detail": "No images provided."}, status=status.HTTP_400_BAD_REQUEST
            )

        start_order = product.images.count()
        ProductService.add_images(product, images, start_order)
        product.refresh_from_db()
        return Response(
            AdminProductSerializer(product, context={"request": request}).data
        )


class AdminProductImageDeleteView(APIView):
    permission_classes = [IsAdminUser]

    def delete(self, request, pk, image_id):
        try:
            image = ProductImage.objects.get(pk=image_id, product_id=pk)
        except ProductImage.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        ProductService.delete_image(image)
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminProductOptionListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = ProductOptionSerializer

    def get_queryset(self):
        queryset = ProductOption.objects.all()
        option_type = self.request.query_params.get("option_type")
        return queryset.filter(option_type=option_type) if option_type else queryset


class AdminProductOptionDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    queryset = ProductOption.objects.all()
    serializer_class = ProductOptionSerializer

    def destroy(self, request, *args, **kwargs):
        option = self.get_object()
        field_map = {"BRAND": "brand", "CATEGORY": "category", "CONDITION": "condition", "COLOR": "color"}
        field = field_map.get(option.option_type)
        if field and Product.objects.filter(**{field: option.value}).exists():
            return Response({"detail": "This option is used by products and cannot be deleted."}, status=status.HTTP_409_CONFLICT)
        if option.option_type == "SIZE" and Product.objects.filter(variants__size=option.value).exists():
            return Response({"detail": "This size is used by products and cannot be deleted."}, status=status.HTTP_409_CONFLICT)
        return super().destroy(request, *args, **kwargs)
