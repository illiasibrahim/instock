from rest_framework import serializers
from geopy.geocoders import Nominatim
from haversine import haversine, Unit

from api.v1.exceptions import BaseAPIException, LocationOutOfBoundException, MedicinesRequiredException
from inventory.models import Medicine, Cluster
from orders.models import Order, OrderItem


class MedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicine
        fields = '__all__'


class ValidateLocationSerializer(serializers.Serializer):
    location = serializers.CharField()

    def validate(self, data):
        cleaned_data = super().validate(data)
        target_location = cleaned_data.get("location")
        locations = Cluster.objects.all().values_list("location", flat=True)
        try:
            assert locations.exists()
            cluster_location = self.find_closest_location(target_location, locations)
            cleaned_data.update({
                "cluster_location": cluster_location
            })
        except Exception as e:
            raise LocationOutOfBoundException()
        return cleaned_data

    @staticmethod
    def get_coordinates(location):
        geolocator = Nominatim(user_agent="instock")
        location_info = geolocator.geocode(location)
        return (location_info.latitude, location_info.longitude)

    def find_closest_location(self, target_location, locations, max_distance_km=4):
        target_coordinates = self.get_coordinates(target_location)
        location_coordinates = {location: self.get_coordinates(location) for location in locations}

        valid_locations = [
            location for location in location_coordinates.keys()
            if haversine(target_coordinates, location_coordinates[location], unit=Unit.KILOMETERS) <= max_distance_km
        ]
        if not valid_locations:
            raise LocationOutOfBoundException()

        closest_location = min(
            valid_locations,
            key=lambda location: haversine(target_coordinates, location_coordinates[location], unit=Unit.KILOMETERS)
        )
        return closest_location


class CreateOrderSerializer(serializers.Serializer):
    medicines = serializers.JSONField()
    location = serializers.CharField()
    contact_number = serializers.CharField()

    def validate(self, data):
        validated_data = super().validate(data)
        medicines = validated_data.get("medicines", None)
        if not medicines:
            raise MedicinesRequiredException()
        return validated_data


class OrderItemSerializer(serializers.ModelSerializer):
    medicine = serializers.SerializerMethodField()
    class Meta:
        model = OrderItem
        fields = ("medicine", "quantity", "value")

    def get_medicine(self, obj):
        return obj.medicine.name

class OrderListSerializer(serializers.ModelSerializer):
    order_items = serializers.SerializerMethodField()
    class Meta:
        model = Order
        fields = ("code", "contact_number", "status", "order_items")

    def get_order_items(self, obj):
        order_items = OrderItem.objects.filter(order=obj)
        serializer = OrderItemSerializer(order_items, many=True)
        return serializer.data
