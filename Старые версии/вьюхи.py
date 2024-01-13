from django.contrib.auth import logout
from django.db.models import Count
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, View, TemplateView
from django.contrib.auth.decorators import login_required
from carshop.car_utils import create_clients
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from carshop.faker import fake
from carshop.forms import CreateCarsForm
from carshop.models import Order, CarType, OrderQuantity, Car, Licence, Client


def cars_list(request):
    clients = Client.objects.all()
    car_types = (
        CarType.objects.filter(car__blocked_by_order=None, car__owner=None)
        .values("brand", "name", "image")
        .annotate(count=Count("car"))
    )
    for car in car_types:
        car["count"] = [i for i in range(0, car["count"] + 1)]
        car["car_type"] = CarType.objects.filter(
            brand=car["brand"], name=car["name"], image=car["image"]
        ).first()

    if request.method == "GET":
        return render(
            request,
            "cars_list.html",
            {"clients": clients, "car_types": car_types},
        )

    if request.method == "POST":
        client_id = request.POST.get("client")
        client = Client.objects.get(id=client_id)
        order = Order.objects.create(client=client)

        for car in car_types:
            brand = car["car_type"].brand
            name = car["car_type"].name
            image = car["car_type"].image
            quantity = int(request.POST.get(f"quantity_{brand}_{name}_{image}"))

            if quantity > 0:
                car_type_obj = CarType.objects.filter(name=name, image=image).first()
                OrderQuantity.objects.create(
                    car_type=car_type_obj, quantity=quantity, order=order
                )

                reserved_cars = Car.objects.filter(
                    car_type__name=car_type_obj.name,
                    car_type__image=car_type_obj.image,
                    blocked_by_order=None,
                )[:quantity]
                for reserved_car in reserved_cars:
                    reserved_car.block(order)
                    reserved_car.add_owner(client)

        return redirect("orders_page")


def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    cars = Car.objects.filter(blocked_by_order=pk)
    total_price = sum(car.car_type.price for car in cars)

    if request.method == "POST":
        order = Order.objects.get(pk=pk)
        order.is_paid = True
        order.save()

        cars = Car.objects.filter(blocked_by_order=order.id)
        for car in cars:
            Licence.objects.create(car=car, number=fake.car_number(), order_id=order.id)
        return redirect("payment", order.id)
    return render(
        request,
        "order_detail.html",
        {"cars": cars, "order": order, "total_price": total_price},
    )
