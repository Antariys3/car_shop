from django.contrib.auth import logout
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect, get_object_or_404

from .faker import fake
from .forms import CarsList, CreateCarsForm
from .models import Order, CarType, OrderQuantity, Car, Licence


def index(request):
    return render(request, "index.html", {"user": request.user})


def cars_list(request):
    if request.method == "GET":
        form = CarsList()
        return render(request, "cars_list.html", {"form": form})

    form = CarsList(request.POST)
    form.car_types = CarType.objects.values_list("name", flat=True).distinct()
    if form.is_valid():
        client = form.cleaned_data["client"]
        order = Order.objects.create(client=client)

        for car_type in form.car_types:
            quantity = form.cleaned_data[car_type]
            if quantity > 0:
                car_type_obj = CarType.objects.filter(name=car_type).first()
                OrderQuantity.objects.create(
                    car_type=car_type_obj, quantity=quantity, order=order
                )

                cars_to_reserve = Car.objects.filter(
                    car_type__name=car_type_obj.name, blocked_by_order=None
                )[:quantity]
                for car in cars_to_reserve:
                    car.block(order)
                    car.add_owner(client)

        return redirect("orders_page")
    return render(request, "cars_list.html", {"form": form})


def orders_page(request):
    list_orders = Order.objects.filter(is_paid=False)
    return render(request, "orders_page.html", {"list_orders": list_orders})


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


def delete_order(request, order_id):
    cars = Car.objects.filter(blocked_by_order=order_id)
    for car in cars:
        car.unblock()
        car.remove_owner()
    order = get_object_or_404(Order, id=order_id)
    order.delete()

    list_orders = Order.objects.all()
    return render(request, "orders_page.html", {"list_orders": list_orders})


def payment(request, order_id):
    licenses = Licence.objects.filter(order_id=order_id)
    return render(request, "payment.html", {"licenses": licenses, "order_id": order_id})


def create_cars(request):
    if request.method == "GET":
        form = CreateCarsForm()
        return render(request, "create_cars.html", {"form": form})
    form = CreateCarsForm(request.POST)
    if form.is_valid():
        brand = form.cleaned_data["brand"]
        name = form.cleaned_data["name"]
        price = form.cleaned_data["price"]
        color = form.cleaned_data['color']
        year = form.cleaned_data['year']
        quantity = form.cleaned_data["quantity"]

        for _ in range(quantity):
            car_type = CarType.objects.create(brand=brand, name=name, price=price)
            car = Car(
                car_type=car_type,
                color=color,
                year=year
            )
            car.save()
        return redirect("cars_list")
    return render(request, "create_cars.html", {"form": form})


def register(request):
    if request.method == "GET":
        form = UserCreationForm()
        return render(request, "registration/register.html", {"form": form})
    form = UserCreationForm(request.POST)
    if form.is_valid():
        form.save()
        return redirect("login")
    return render(request, "registration/register.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("home")
