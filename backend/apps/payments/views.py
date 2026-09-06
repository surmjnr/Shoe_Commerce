import json
import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import PaymentInitializeSerializer
from .services import PaymentService

logger = logging.getLogger(__name__)


class PaymentInitializeView(APIView):
    def post(self, request):
        serializer = PaymentInitializeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = PaymentService.initialize_payment(
                serializer.validated_data["order_id"],
                serializer.validated_data["phone"],
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(result)


class PaymentWebhookView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        try:
            payload = request.data if isinstance(request.data, dict) else json.loads(request.body)
        except (json.JSONDecodeError, TypeError):
            return Response({"detail": "Invalid payload."}, status=400)

        payment = PaymentService.handle_webhook(payload, dict(request.headers))

        if payment:
            return Response({"status": "processed", "reference": payment.provider_reference})

        return Response({"status": "ignored"})
