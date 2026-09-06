from django.urls import path

from .views import AdminLoginView, AdminMeView, AdminRefreshView

urlpatterns = [
    path("admin/auth/login/", AdminLoginView.as_view(), name="admin-login"),
    path("admin/auth/refresh/", AdminRefreshView.as_view(), name="admin-refresh"),
    path("admin/auth/me/", AdminMeView.as_view(), name="admin-me"),
]
