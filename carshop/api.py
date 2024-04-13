import django_filters.rest_framework
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework import status
from rest_framework import viewsets
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from rest_framework import filters

from carshop.invoices import create_invoice, verify_signature
from carshop.serializers import (
    CarSerializer,
    OrderSerializer,
)
from .models import Order, OrderQuantity, Car


class CustomObtainAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")
        email = request.data.get("email")

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = None

        if user and user.check_password(password):
            # User exists, check password
            token, created = Token.objects.get_or_create(user=user)
            return Response({"token": token.key})
        elif not user:
            # User does not exist, create a new one
            user = User.objects.create(username=username, email=email)
            user.set_password(password)
            user.save()

            token = Token.objects.create(user=user)
            return Response({"token": token.key})
        else:
            # User exists, but password is incorrect
            return Response(
                {"error": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED,
            )


class CarsAPIView(viewsets.ModelViewSet):
    queryset = Car.objects.filter(
        blocked_by_order=None, owner=None
    ).select_related("car_type")
    serializer_class = CarSerializer
    http_method_names = ["get"]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [
        django_filters.rest_framework.DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["year", "car_type__price"]
    search_fields = ["car_type__brand", "car_type__name"]
    ordering_fields = ["year", "car_type__price"]


class AddToCartAPIView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def post(self, request, car_id, *args, **kwargs):
        # adding a car to cart
        client = User.objects.filter(username=request.user).first()
        order, created = Order.objects.get_or_create(
            client=client, is_paid=False
        )
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

        OrderQuantity.objects.create(
            car_type=car.car_type, quantity=1, order=order
        )
        car_serializer = CarSerializer(car)
        return Response(car_serializer.data, status=status.HTTP_200_OK)


class CartAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # view cart with cars
        owner = User.objects.filter(email=request.user.email).first()
        order = Order.objects.filter(is_paid=False, client_id=owner).first()
        if order is None:
            return Response(
                {"error": f"User {owner} has an empty cart"},
                status=status.HTTP_404_NOT_FOUND,
            )
        cars = Car.objects.filter(blocked_by_order=order).select_related(
            "car_type"
        )
        total_price = sum(car.car_type.price for car in cars)
        context = {
            "order": OrderSerializer(order).data,
            "cars": CarSerializer(cars, many=True).data,
            "total_price": total_price,
        }
        return Response({"cart": context}, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        # buying a car and issuing registration numbers
        client = User.objects.filter(email=request.user.email).first()
        order = get_object_or_404(
            Order,
            client_id=client,
            is_paid=False,
        )

        cars = Car.objects.filter(
            blocked_by_order=order, owner=client
        ).select_related("car_type")

        create_invoice(order, cars, reverse("webhook-mono", request=request))

        return Response({"invoice_url": order.invoice_url})

    def delete(self, request, *args, **kwargs):
        # a method that removes a cart or one car
        owner = User.objects.filter(email=request.user.email).first()
        order = Order.objects.filter(is_paid=False, client_id=owner).first()

        if order is None:
            return Response(
                {"error": "cart empty"}, status=status.HTTP_404_NOT_FOUND
            )

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
        car_in_order = get_object_or_404(
            OrderQuantity, order_id=order, car_type_id=pk
        )
        if not car_in_order:
            return Response(
                {"error": "Method DELETE not allowed"},
                status=status.HTTP_404_NOT_FOUND,
            )
        car_in_order.delete()
        car = Car.objects.get(blocked_by_order=order.id, car_type_id=pk)
        car.unblock()
        car.remove_owner()
        return Response(
            {
                "massage": "The car from the basket has been successfully removed."
            },
            status=status.HTTP_200_OK,
        )


class MonoAcquiringWebhookReceiver(APIView):
    def post(self, request):
        try:
            verify_signature(request)
        except Exception as e:
            return Response({"status": "errors"}, status=400)
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


class PaymentStatusApi(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_number, *args, **kwargs):
        owner = User.objects.filter(email=request.user.email).first()

        if not owner:
            return Response(
                {"error": "Client not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        order_number = request.query_params.get("order_number")

        if not order_number:
            return Response(
                {"error": "Order number is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            order = Order.objects.get(id=order_number, client_id=owner)
        except Order.DoesNotExist:
            return Response(
                {"error": f"Order with number {order_number} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        status_data = {"order_number": order.id, "status": order.status}

        return Response(status_data, status=status.HTTP_200_OK)
