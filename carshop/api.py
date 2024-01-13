from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework import status
from rest_framework import viewsets
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

from carshop.car_utils import create_clients
from carshop.invoices import create_invoice, verify_signature
from carshop.serializers import (
    CarSerializer,
    OrderSerializer,
)
from .models import Order, OrderQuantity, Car, Client


class CustomObtainAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")
        email = request.data.get("email")

        # create a new user or update the token
        user, created = User.objects.get_or_create(
            username=username, defaults={"email": email}
        )

        if user.check_password(password):
            token, created = Token.objects.get_or_create(user=user)
            return Response({"token": token.key})
        else:
            return Response(
                {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )


class CarsAPIView(viewsets.ModelViewSet):
    queryset = Car.objects.filter(blocked_by_order=None, owner=None).select_related(
        "car_type"
    )
    serializer_class = CarSerializer
    http_method_names = ["get"]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class AddToCartAPIView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def post(self, request, car_id, *args, **kwargs):
        # adding a car to cart
        client = create_clients(request.user)
        order, created = Order.objects.get_or_create(client=client, is_paid=False)
        order_serializer = OrderSerializer(data=client)
        if order_serializer.is_valid():
            order_serializer.save()

        try:
            car = Car.objects.select_related("car_type").get(
                id=car_id, blocked_by_order=None, owner=None
            )
        except Car.DoesNotExist:
            return Response(
                {"error": "Car not found"}, status=status.HTTP_404_NOT_FOUND
            )
        car.block(order)
        car.add_owner(client)

        OrderQuantity.objects.create(car_type=car.car_type, quantity=1, order=order)
        car_serializer = CarSerializer(car)
        return Response(car_serializer.data, status=status.HTTP_200_OK)


class CartAPIView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, *args, **kwargs):
        # view cart with cars
        owner = Client.objects.filter(email=request.user.email).first()
        order = Order.objects.filter(is_paid=False, client_id=owner).first()
        if order is None:
            return Response(
                {"error": f"User {owner} has an empty cart"},
                status=status.HTTP_404_NOT_FOUND,
            )
        cars = Car.objects.filter(blocked_by_order=order).select_related("car_type")
        total_price = sum(car.car_type.price for car in cars)
        context = {
            "order": OrderSerializer(order).data,
            "cars": CarSerializer(cars, many=True).data,
            "total_price": total_price,
        }
        return Response({"cart": context}, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        # buying a car and issuing registration numbers
        client = Client.objects.filter(email=request.user.email).first()
        order = get_object_or_404(
            Order,
            client_id=client,
            is_paid=False,
        )

        cars = Car.objects.filter(blocked_by_order=order, owner=client).select_related('car_type')

        # create_invoice(order, cars, "https://webhook.site/209833c7-0212-4e72-aedc-742aaf0453ae")
        create_invoice(order, cars, reverse("webhook-mono", request=request))

        return Response({"invoice_url": order.invoice_url})

    def delete(self, request, *args, **kwargs):
        # a method that removes a cart or one car
        owner = Client.objects.filter(email=request.user.email).first()
        order = Order.objects.filter(is_paid=False, client_id=owner).first()

        if order is None:
            return Response({"error": "cart empty"}, status=status.HTTP_404_NOT_FOUND)

        pk = kwargs.get("pk", None)
        if pk is None:
            # removing all ordered cars from the cart
            cars = Car.objects.filter(blocked_by_order=order.id)
            for car in cars:
                car.unblock()
                car.remove_owner()
            order = get_object_or_404(Order, id=order.id)
            order.delete()
            return Response(
                {"massage": "The cart was successfully emptied"},
                status=status.HTTP_200_OK,
            )
        # removing one car from the cart
        car_in_order = get_object_or_404(OrderQuantity, order_id=order, car_type_id=pk)
        if not car_in_order:
            return Response(
                {"error": "Method DELETE not allowed"}, status=status.HTTP_404_NOT_FOUND
            )
        car_in_order.delete()
        car = Car.objects.get(blocked_by_order=order.id, car_type_id=pk)
        car.unblock()
        car.remove_owner()
        return Response(
            {"massage": "The car from the basket has been successfully removed."},
            status=status.HTTP_200_OK,
        )


class MonoAcquiringWebhookReceiver(APIView):

    def post(self, request):
        try:
            verify_signature(request)
        except Exception as e:
            return Response({"status": "error"}, status=400)
        reference = request.data.get("reference")
        order = Order.objects.get(id=reference)
        if order.invoice_id != request.data.get("invoiceId"):
            return Response({"status": "error"}, status=400)
        order.status = request.data.get("status", "error")
        order.save()
        if order.status == "success":
            order.is_paid = True
            order.save()
            return Response({"status": "Paid"}, status=200)
        return Response({"status": "ok"})
