from django.urls import path

from .views import AdminStoreSettingsView, PublicStoreSettingsView

urlpatterns = [
    path("settings/", PublicStoreSettingsView.as_view(), name="public-settings"),
    path("admin/settings/", AdminStoreSettingsView.as_view(), name="admin-settings"),
]
