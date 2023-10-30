from django.shortcuts import render, redirect
from .forms import CarsList
from .models import Order, CarType, OrderQuantity, Car


def index(request):
    return render(request, 'index.html', )


def cars_list(request):
    if request.method == "GET":
        form = CarsList()
        return render(request, 'cars_list.html', {'form': form})

    form = CarsList(request.POST)
    if form.is_valid():
        client = form.cleaned_data['client']
        order = Order.objects.create(client=client)

        for car_type in form.car_types:
            quantity = form.cleaned_data[car_type]
            if quantity > 0:
                car_type_objs = CarType.objects.filter(name=car_type)
                for car_type_obj in car_type_objs:
                    order_quantity = OrderQuantity.objects.create(
                        car_type=car_type_obj,
                        quantity=quantity,
                        order=order
                    )

                    cars_to_reserve = Car.objects.filter(car_type=car_type_obj, blocked_by_order=None)[:quantity]
                    for car in cars_to_reserve:
                        car.block(order)
                        car.add_owner(client)

        return redirect('orders_page')
    return render(request, 'cars_list.html', {'form': form})


def orders_page(request):
    list_orders = Order.objects.all()
    print(list_orders)
    return render(request, 'orders_page.html', {'list_orders': list_orders})


def order_edit(request):
    return render(request, 'order_edit.html')
