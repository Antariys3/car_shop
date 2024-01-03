from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, View, TemplateView

from carshop.car_utils import create_clients, crop_image
from .faker import fake
from .forms import CreateCarsForm
from .models import Order, CarType, OrderQuantity, Car, Licence, Client


def logout_view(request):
    logout(request)
    return redirect("cars_list")


def index(request):
    return render(request, "index.html", {"user": request.user})


class CarsShopView(TemplateView):
    model = Car
    template_name = "cars_list.html"
    context_object_name = "cars"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cars'] = Car.objects.filter(blocked_by_order=None, owner=None).select_related("car_type")
        return context

    def post(self, request, *args, **kwargs):
        client = create_clients(request.user)
        car_id = request.POST.get('car_id')
        car = Car.objects.select_related("car_type").get(id=car_id)

        order = Order.objects.filter(client_id=client.id, is_paid=False).first()
        if order:
            OrderQuantity.objects.create(car_type=car.car_type, quantity=1, order=order)

        else:
            order = Order.objects.create(client=client)
            OrderQuantity.objects.create(car_type=car.car_type, quantity=1, order=order)

        car.block(order)
        car.add_owner(client)

        cars = Car.objects.filter(blocked_by_order=None, owner=None).select_related("car_type")
        return render(request, "cars_list.html", {'cars': cars})


class CarDetailView(DetailView):
    model = Car
    template_name = "car_detail.html"

    def get(self, request, *args, **kwargs):
        car_id = self.kwargs.get('car_id')
        car = Car.objects.filter(id=car_id).prefetch_related('car_type').first()
        if car is None:
            raise Http404("Car does not exist")
        return render(request, self.template_name, {'car': car})


@method_decorator(login_required, name='dispatch')
class BasketView(View):
    template_name = "basket.html"

    def get(self, request, *args, **kwargs):
        owner = Client.objects.filter(email=request.user.email).first()
        order = Order.objects.filter(is_paid=False, client_id=owner).first()
        if order is None:
            return render(request, self.template_name, {'order': order})
        cars = Car.objects.filter(blocked_by_order=order).select_related("car_type")
        total_price = sum(car.car_type.price for car in cars)
        context = {
            'order': order,
            'cars': cars,
            'total_price': total_price,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        order_id = request.POST.get('order_id')
        order = Order.objects.get(id=order_id)
        order.is_paid = True
        order.save()

        cars = Car.objects.filter(blocked_by_order=order.id)
        for car in cars:
            Licence.objects.create(car=car, number=fake.car_number(), order_id=order.id)
        return redirect("payment", order.id)


def orders_page(request):
    list_orders = Order.objects.filter(is_paid=False)
    return render(request, "orders_page.html", {"list_orders": list_orders})


def delete_order(request, order_id):
    cars = Car.objects.filter(blocked_by_order=order_id)
    for car in cars:
        car.unblock()
        car.remove_owner()
    order = get_object_or_404(Order, id=order_id)
    order.delete()

    return redirect("orders_page")


def payment(request, order_id):
    licenses = Licence.objects.filter(order_id=order_id)
    return render(request, "payment.html", {"licenses": licenses, "order_id": order_id})


@login_required
def sell_cars(request):
    if request.method == "GET":
        form = CreateCarsForm()
        return render(request, "sell_cars.html", {"form": form})
    form = CreateCarsForm(request.POST, request.FILES)
    if form.is_valid():
        brand = form.cleaned_data["brand"]
        name = form.cleaned_data["name"]
        price = form.cleaned_data["price"]
        color = form.cleaned_data["color"]
        year = form.cleaned_data["year"]
        image = form.cleaned_data["image"]

        try:
            with transaction.atomic():
                car_type = CarType.objects.create(brand=brand, name=name, price=price)
                car_type.image.save(f"{image}", crop_image(image))
                car = Car(car_type=car_type, color=color, year=year)
                car.save()
        except Exception as e:
            print(f"Ошибка: {e}")
        return redirect("cars_list")
    return render(request, "sell_cars.html", {"form": form})


def image_edit(request):
    car_types = CarType.objects.values("brand", "name", "image").distinct()
    for car in car_types:
        car["car_type"] = CarType.objects.filter(
            brand=car["brand"], name=car["name"], image=car["image"]
        ).first()

    if request.method == "GET":
        return render(request, "image_edit.html", {"car_types": car_types})

    if request.method == "POST":
        for car in car_types:
            car_type_id = request.POST.get(f'car_type_id_{car["car_type"].id}')
            image_file = request.FILES.get(f'image_{car["car_type"].id}')

            if car_type_id and image_file:
                car_type = CarType.objects.get(id=car_type_id)
                car_types = CarType.objects.filter(
                    name=car_type.name, image=car_type.image
                )
                for car_type in car_types:
                    car_type.image.delete()
                    car_type.image.save(f"{image_file}", crop_image(image_file))

        return redirect("cars_list")
