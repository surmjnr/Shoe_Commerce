from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .serializers import AdminUserSerializer, CustomTokenObtainPairSerializer


class AdminLoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class AdminRefreshView(TokenRefreshView):
    pass


class AdminMeView(APIView):
    def get(self, request):
        if not request.user.is_authenticated or not request.user.is_staff:
            return Response(
                {"detail": "Authentication required."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        return Response(AdminUserSerializer(request.user).data)
