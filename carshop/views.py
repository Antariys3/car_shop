from django.shortcuts import render, redirect, get_object_or_404

from .faker import fake
from .forms import CarsList
from .models import Order, CarType, OrderQuantity, Car, Licence


def index(request):
    return render(
        request,
        "index.html",
    )


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
