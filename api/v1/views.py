import json
from datetime import datetime

import requests
from decouple import config
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from api.utils import main
from api.v1.exceptions import (
    BaseAPIException,
    MedicineUnavailableException,
    BucketDoesNotExistException
)
from api.v1.permissions import RiderOnlyPermission
from api.v1.serializers import (
    MedicineSerializer,
    CreateOrderSerializer,
    ValidateLocationSerializer, OrderListSerializer
)
from core.utils import get_random_code
from inventory.models import Medicine, Cluster, Stock
from orders.constants import OrderStatusTypes
from orders.models import (
    Order, OrderItem, Bucket, BucketItem)


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


class OrderView(APIBaseView):
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
                created_by=request.user,
                cluster=cluster
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
                        order=order,
                        medicine=medicine_obj,
                        quantity=quantity,
                        store=stock.store,
                        value=value)
                    order_value += value
                except IndexError:
                    raise MedicineUnavailableException(medicine=medicine_obj.__str__())
            return Response({
                "status": "success",
                "code": order.code,
                "order_value": order_value
            })
        else:
            return serializer.errors

    def get(self, request, *args, **kwargs):
        queryset = Order.objects.filter(
            created_by=request.user).order_by("-created_date")
        serializer = OrderListSerializer(queryset, many=True)
        return Response(serializer.data)



class BucketView(APIBaseView):
    permission_classes = [RiderOnlyPermission, IsAuthenticated]

    def populate_response_data(self, bucket_items):
        data = [
            {
                "id": item.id,
                "username": item.order.created_by.first_name,
                "contact_number": item.order.contact_number,
                "location": item.order.location
            } for item in bucket_items
        ]
        return data

    def get(self, request, *args, **kwargs):
        try:
            active_bucket = Bucket.objects.get(
                rider=request.user.user_rider,
                is_active=True
            )
            bucket_items = BucketItem.objects.filter(
                bucket=active_bucket,
                is_delivered=False
            ).order_by("order_number")
            data = self.populate_response_data(bucket_items)
            return Response(data)
        except ObjectDoesNotExist:
            raise BucketDoesNotExistException()


    def populate_buckets(self, cluster, now, optimized_routes, rider):
        orders = Order.objects.filter(
            cluster=cluster, status='created', created_date__lt=now).order_by('id')
        for route in optimized_routes.keys():
            bucket = Bucket(rider=rider)
            bucket.save()
            for i in range(len(orders)):
                order = orders[i]
                BucketItem.objects.create(
                    bucket=bucket,
                    order=order,
                    order_number=optimized_routes[route]['path'][i]
                )
                order.status = OrderStatusTypes.PICKED
                order.save()
            return bucket

    def post(self, request, *args, **kwargs):
        try:
            active_bucket = Bucket.objects.get(
                rider=request.user.user_rider,
                is_active=True
            )
            bucket_items = BucketItem.objects.filter(
                bucket=active_bucket,
                is_delivered=False
            ).order_by("order_number")
            data = self.populate_response_data(bucket_items)
            return Response(data)
        except ObjectDoesNotExist:
            pass

        cluster = request.user.user_rider.cluster
        now = datetime.now()
        # solving the problem with google OR Tools
        optimized_routes = main(cluster, now)
        bucket = self.populate_buckets(cluster, now, optimized_routes, request.user.user_rider)

        bucket_items = BucketItem.objects.filter(
            bucket=bucket,
            is_delivered=False
        ).order_by("order_number")
        data = self.populate_response_data(bucket_items)
        return Response(data)

class MarkAsDeliveredView(APIView):
    def post(self, request, *args, **kwargs):
        id = kwargs.get("id", None)
        is_final = request.GET.get("is_final", False)
        if not id:
            raise BaseAPIException()
        try:
            bucket_item = BucketItem.objects.get(id=id)
            bucket_item.is_delivered = True
            bucket_item.save()
            bucket_item.order.status = OrderStatusTypes.DELIVERED
            bucket_item.order.save()
            if is_final:
                bucket = bucket_item.bucket
                bucket.is_active = False
                bucket.save()
            return Response({"status": "success"})
        except ObjectDoesNotExist:
            raise BaseAPIException()


class GetPrescribedMedications(APIBaseView):

    def get_authorization_headers(self):
        hsLoginBaseUrl = config("hsLoginBaseUrl")
        client_id = config("client_id")
        client_secret = config("client_secret")
        adminMobileNo = config("adminMobileNo")
        mpin = config("mpin")
        hospitalCode = config("hospitalCode")
        auth_url = (
            f"{hsLoginBaseUrl}/oauth/token?grant_type=password"
            f"&username={adminMobileNo}&password={mpin}&"
            f"hospCode={hospitalCode}&client_secret={client_secret}&"
            f"client_id={client_id}")
        response = requests.request(url=auth_url, method='GET')
        if response.status_code == 200:
            response_dict = json.loads(response.text)
            access_token = response_dict.get("access_token")
            return {
                "Authorization": f"Bearer {access_token}"
            }
        else:
            raise BaseAPIException()

    def get(self, request, *args, **kwargs):
        headers = self.get_authorization_headers()
        try:
            customer = request.user.customer
            baseUrl = config("baseUrl")
            mobileAPIversion = config("mobileAPIversion")
            prescribed_medicines_url = (
                f"{baseUrl}{mobileAPIversion}/getCurrentMedicationDetails?"
                f"patientEId={customer.userEID}")
            response = requests.request(
                url=prescribed_medicines_url,
                method='GET',
                headers=headers
            )
            if response.status_code == 200:
                response_dict = json.loads(response.text)
                medicine_details = response_dict.get("data")
                data = []
                for medicine_data in medicine_details:
                    code = medicine_data["brandName"]
                    try:
                        medicine = Medicine.objects.get(code=code)
                        frequency = medicine_data["frequency"]
                        frequency = sum(int(
                            element) for element in frequency.split('-'))
                        days = medicine_data["days"]
                        days = int(days[:-4])
                        data.append(
                            {
                                "id": medicine.id,
                                "name": medicine.name,
                                "image": request.build_absolute_uri(medicine.image.url),
                                "quantity": days * frequency
                            }
                        )
                    except ObjectDoesNotExist:
                        pass
            else:
                raise BaseAPIException()
        except ObjectDoesNotExist:
            data = []
        return Response(data)
