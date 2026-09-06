from django.urls import path

from .views import (
    AdminDashboardView,
    AdminOrderDetailView,
    AdminOrderListView,
    AdminOrderPaymentUpdateView,
    AdminOrderStatusUpdateView,
    OrderCreateView,
    OrderTrackView,
)

urlpatterns = [
    path("orders/", OrderCreateView.as_view(), name="order-create"),
    path("orders/track/", OrderTrackView.as_view(), name="order-track"),
    path("admin/dashboard/", AdminDashboardView.as_view(), name="admin-dashboard"),
    path("admin/orders/", AdminOrderListView.as_view(), name="admin-order-list"),
    path("admin/orders/<int:pk>/", AdminOrderDetailView.as_view(), name="admin-order-detail"),
    path(
        "admin/orders/<int:pk>/status/",
        AdminOrderStatusUpdateView.as_view(),
        name="admin-order-status",
    ),
    path(
        "admin/orders/<int:pk>/payment/",
        AdminOrderPaymentUpdateView.as_view(),
        name="admin-order-payment",
    ),
]
