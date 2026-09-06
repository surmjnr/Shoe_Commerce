from rest_framework import generics
from rest_framework.permissions import AllowAny

from apps.accounts.permissions import IsAdminUser

from .models import StoreSettings
from .serializers import StoreSettingsSerializer


class PublicStoreSettingsView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = StoreSettingsSerializer

    def get_object(self):
        return StoreSettings.load()


class AdminStoreSettingsView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = StoreSettingsSerializer

    def get_object(self):
        return StoreSettings.load()
