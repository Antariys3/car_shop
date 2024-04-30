from rest_framework import serializers

from .models import Car, CarType, User, Order, OrderQuantity


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email"]


class OrderSerializer(serializers.ModelSerializer):
    user = UserSerializer(source="client")

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
        # second way to open a nested dictionary
        # depth = 1


class OrderQuantitySerializer(serializers.ModelSerializer):
    car_type = CarTypeSerializer()
    order = OrderSerializer()

    class Meta:
        model = OrderQuantity
        fields = "__all__"
