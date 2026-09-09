from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsAdminUser

from .models import Order
from .serializers import (
    AdminOrderSerializer,
    OrderCreateSerializer,
    OrderSerializer,
    OrderStatusUpdateSerializer,
    OrderTrackLookupSerializer,
    OrderTrackingSerializer,
)
from .services import OrderService, OrderValidationError


class OrderCreateView(APIView):
    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            order = OrderService.create_order(
                serializer.validated_data,
                serializer.validated_data["items"],
            )
        except OrderValidationError as e:
            return Response({"detail": e.message, "code": e.code}, status=400)

        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_201_CREATED,
        )


class OrderTrackView(APIView):
    def post(self, request):
        serializer = OrderTrackLookupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order = OrderService.get_order_by_number_and_phone(
            serializer.validated_data["order_number"],
            serializer.validated_data["phone"],
        )

        if not order:
            return Response(
                {"detail": "Order not found. Check your order number and phone."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(OrderTrackingSerializer(order).data)


class AdminDashboardView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        return Response(OrderService.get_dashboard_stats())


class AdminOrderListView(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = AdminOrderSerializer

    def get_queryset(self):
        return OrderService.get_orders(
            {
                "status": self.request.query_params.get("status"),
                "payment_status": self.request.query_params.get("payment_status"),
                "payment_method": self.request.query_params.get("payment_method"),
                "search": self.request.query_params.get("search"),
            }
        )


class AdminOrderDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = AdminOrderSerializer
    queryset = Order.objects.prefetch_related("items").all()


class AdminOrderStatusUpdateView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = OrderStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            order = OrderService.update_status(
                order, serializer.validated_data["status"]
            )
        except OrderValidationError as e:
            return Response({"detail": e.message}, status=status.HTTP_400_BAD_REQUEST)

        return Response(AdminOrderSerializer(order).data)


class AdminOrderPaymentUpdateView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        order = OrderService.mark_payment_received(order)
        return Response(AdminOrderSerializer(order).data)
