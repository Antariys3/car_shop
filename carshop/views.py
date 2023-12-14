from django.contrib.auth import logout
from django.contrib.auth.forms import User
from django.contrib.auth.views import PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.mail import send_mail
from django.core.signing import Signer, BadSignature
from django.db.models import Count
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy

from Car_shop import settings
from .faker import fake
from .forms import CreateCarsForm, UserCreationFormWithEmail
from .models import Order, CarType, OrderQuantity, Car, Licence, Client


def send_activation_email(request, user: User):
    user_signed = Signer().sign(user.id)
    signer_url = request.build_absolute_uri(f"/activate/{user_signed}")
    send_mail(
        "Registration complete",
        f"Click here to activate your account: {signer_url}",
        f"{settings.DEFAULT_FROM_EMAIL}",
        [user.email],
        fail_silently=False,
    )


class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    success_message = (
        "We've emailed you instructions for setting your password, "
        "if an account exists with the email you entered. You should receive them shortly."
        " If you don't receive an email, "
        "please make sure you've entered the address you registered with, and check your spam folder."
    )
    success_url = reverse_lazy("login")


def activate(request, user_signed):
    try:
        user_id = Signer().unsign(user_signed)
    except BadSignature:
        return redirect("login")
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return redirect("login")
    user.is_active = True
    user.save()
    return redirect("login")


def register(request):
    if request.method == "GET":
        form = UserCreationFormWithEmail()
        return render(request, "registration/register.html", {"form": form})
    form = UserCreationFormWithEmail(request.POST)
    if form.is_valid():
        form.instance.is_active = False
        form.save()
        send_activation_email(request, form.instance)
        return redirect("login")
    return render(request, "registration/register.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("home")


def checking_mail(request):
    return render(request, "registration/mail.html")


def index(request):
    return render(request, "index.html", {"user": request.user})


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

    return redirect("orders_page")


def payment(request, order_id):
    licenses = Licence.objects.filter(order_id=order_id)
    return render(request, "payment.html", {"licenses": licenses, "order_id": order_id})


def create_cars(request):
    if request.method == "GET":
        form = CreateCarsForm()
        return render(request, "create_cars.html", {"form": form})
    form = CreateCarsForm(request.POST, request.FILES)
    if form.is_valid():
        brand = form.cleaned_data["brand"]
        name = form.cleaned_data["name"]
        price = form.cleaned_data["price"]
        color = form.cleaned_data["color"]
        year = form.cleaned_data["year"]
        quantity = form.cleaned_data["quantity"]
        image = form.cleaned_data["image"]

        for _ in range(quantity):
            car_type = CarType.objects.create(brand=brand, name=name, price=price)
            car_type.image.save(f"{image}", image)
            car = Car(car_type=car_type, color=color, year=year)
            car.save()
        return redirect("cars_list")
    return render(request, "create_cars.html", {"form": form})


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
                    car_type.image.save(f"{image_file}", image_file)

        return redirect("cars_list")
