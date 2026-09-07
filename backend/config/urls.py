from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


def api_root(request):
    return JsonResponse(
        {
            "products": "/api/v1/products/",
            "settings": "/api/v1/settings/",
            "orders": "/api/v1/orders/",
            "documentation": "/api/docs/",
        }
    )


urlpatterns = [
    path("", api_root, name="root"),
    path("admin/", admin.site.urls),
    path("api/v1/", api_root, name="api-root"),
    path("api/v1/", include("apps.products.urls")),
    path("api/v1/", include("apps.orders.urls")),
    path("api/v1/", include("apps.payments.urls")),
    path("api/v1/", include("apps.accounts.urls")),
    path("api/v1/", include("apps.common.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
