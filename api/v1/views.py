from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from api.v1.exceptions import BaseAPIException, LocationOutOfBoundException, MedicineUnavailableException
from api.v1.serializers import MedicineSerializer, CreateOrderSerializer, ValidateLocationSerializer
from core.utils import get_random_code
from inventory.models import Medicine, Cluster, Stock
from orders.models import Order, OrderItem


class GetToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        try:
            var = user.user_rider
            role = "r"
        except ObjectDoesNotExist:
            role = "c"
        data = {
            "token": token.key,
            "role": role
        }
        return Response(data)


class APIBaseView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]


class MedicineListAPIView(ListAPIView, APIBaseView):
    queryset = Medicine.objects.all()
    serializer_class = MedicineSerializer
    filter_backends = [SearchFilter]
    search_fields = ['name']


class ValidateLocationView(APIBaseView):

    def post(self, request, *args, **kwargs):
        serializer = ValidateLocationSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            data = {
                "status": "success"
            }
            return Response(data)
        else:
            return serializer.errors


class CreateOrderView(APIBaseView):
    def post(self, request, *args, **kwargs):
        serializer = CreateOrderSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            medicines = serializer.validated_data.get("medicines", None)
            location = serializer.validated_data.get("location", None)
            location_serializer = ValidateLocationSerializer(data=request.data)
            if not location_serializer.is_valid():
                return location_serializer.errors
            cluster_location = location_serializer.validated_data.get("cluster_location")
            cluster = Cluster.objects.get(location=cluster_location)
            contact_number = serializer.validated_data.get("contact_number", None)
            code = get_random_code()
            while Order.objects.filter(code=code).exists():
                code = get_random_code()
            order = Order.objects.create(
                code=code,
                location=location,
                contact_number=contact_number,
                created_by=request.user
            )
            order_value = 0
            for medicine in medicines:
                medicine_obj = Medicine.objects.get(id=medicine["id"])
                quantity = medicine["quantity"]
                try:
                    stock = Stock.objects.filter(
                        medicine=medicine_obj,
                        store__cluster=cluster,
                        quantity__gte=quantity).order_by("price")[0]
                    value = stock.price * quantity
                    OrderItem.objects.create(
                        medicine=medicine_obj,
                        quantity=quantity,
                        store=stock.store,
                        value=value)
                    order_value += value
                except IndexError:
                    raise MedicineUnavailableException(medicine=medicine_obj.__str__())
            return Response({
                "status": "success",
                "order_id": order.code,
                "order_value": order_value
            })
        else:
            return serializer.errors
