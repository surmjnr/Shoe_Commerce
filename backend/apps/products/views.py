from rest_framework import generics, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsAdminUser

from .models import Brand, Category, Color, Condition, Product, ProductImage, Size
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
    BrandSerializer,
    CategorySerializer,
    ColorSerializer,
    ConditionSerializer,
    ProductDetailSerializer,
    ProductListSerializer,
    SizeSerializer,
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
        return Response(CategorySerializer(Category.objects.all(), many=True).data)


class BrandListView(APIView):
    def get(self, request):
        return Response(BrandSerializer(Brand.objects.all(), many=True).data)


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


class ConfigurationListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser]
    model = None
    serializer_class = None

    def get_queryset(self):
        return self.model.objects.all()


class ConfigurationDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    model = None
    serializer_class = None

    def get_queryset(self):
        return self.model.objects.all()


class AdminBrandListCreateView(ConfigurationListCreateView):
    model = Brand
    serializer_class = BrandSerializer


class AdminBrandDetailView(ConfigurationDetailView):
    model = Brand
    serializer_class = BrandSerializer


class AdminCategoryListCreateView(ConfigurationListCreateView):
    model = Category
    serializer_class = CategorySerializer


class AdminCategoryDetailView(ConfigurationDetailView):
    model = Category
    serializer_class = CategorySerializer


class AdminConditionListCreateView(ConfigurationListCreateView):
    model = Condition
    serializer_class = ConditionSerializer


class AdminConditionDetailView(ConfigurationDetailView):
    model = Condition
    serializer_class = ConditionSerializer


class AdminColorListCreateView(ConfigurationListCreateView):
    model = Color
    serializer_class = ColorSerializer


class AdminColorDetailView(ConfigurationDetailView):
    model = Color
    serializer_class = ColorSerializer


class AdminSizeListCreateView(ConfigurationListCreateView):
    model = Size
    serializer_class = SizeSerializer


class AdminSizeDetailView(ConfigurationDetailView):
    model = Size
    serializer_class = SizeSerializer
