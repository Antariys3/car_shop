from rest_framework import serializers

from .models import Car, CarType, Client, Order, OrderQuantity, Licence


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
    client = ClientSerializer()

    class Meta:
        model = Order
        fields = "__all__"


class CarTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarType
        fields = "__all__"


class CarSerializer(serializers.ModelSerializer):
    car_type = CarTypeSerializer()

    class Meta:
        model = Car
        fields = ("id", "car_type", "color", "year")


class OrderQuantitySerializer(serializers.ModelSerializer):
    car_type = CarTypeSerializer()
    order = OrderSerializer()

    class Meta:
        model = OrderQuantity
        fields = "__all__"


class LicenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Licence
        fields = "__all__"
