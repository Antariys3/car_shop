from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect, resolve_url
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView


from carshop.car_utils import create_clients, crop_image
from carshop.invoices import create_invoice, verify_signature
from .forms import CreateCarsForm
from .models import CarType, OrderQuantity, Car, Licence, Client
from .models import Order


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
        context["cars"] = Car.objects.filter(
            blocked_by_order=None, owner=None
        ).select_related("car_type")
        return context

    def post(self, request, *args, **kwargs):
        client = create_clients(request.user)
        car_id = request.POST.get("car_id")
        car = Car.objects.select_related("car_type").get(id=car_id)

        order = Order.objects.filter(client_id=client.id, is_paid=False).first()
        if order:
            OrderQuantity.objects.create(car_type=car.car_type, quantity=1, order=order)

        else:
            order = Order.objects.create(client=client)
            OrderQuantity.objects.create(car_type=car.car_type, quantity=1, order=order)

        car.block(order)
        car.add_owner(client)

        cars = Car.objects.filter(blocked_by_order=None, owner=None).select_related(
            "car_type"
        )
        return render(request, "cars_list.html", {"cars": cars})


class CarDetailView(View):
    model = Car
    template_name = "car_detail.html"

    def get(self, request, *args, **kwargs):
        car_id = self.kwargs.get("car_id")
        car = Car.objects.filter(id=car_id).prefetch_related("car_type").first()
        if car is None:
            raise Http404("Car does not exist")
        cars_count = Car.objects.filter(
            color=car.color,
            year=car.year,
            blocked_by_order=None,
            owner=None,
            car_type__name=car.car_type.name,
            car_type__brand=car.car_type.brand,
        ).count()
        return render(
            request, self.template_name, {"car": car, "cars_count": cars_count}
        )

    @method_decorator(login_required, name="dispatch")
    def post(self, request, *args, **kwargs):
        client = create_clients(request.user)
        if client is None:
            return redirect("login")
        car_id = self.kwargs.get("car_id")
        quantity = int(request.POST.get("number"))
        car = Car.objects.select_related("car_type").get(id=car_id)
        cars = Car.objects.filter(
            blocked_by_order=None,
            owner=None,
            color=car.color,
            car_type__name=car.car_type.name,
            car_type__brand=car.car_type.brand,
        )[:quantity]
        order = Order.objects.filter(client_id=client.id, is_paid=False).first()
        for car in cars:
            if order:
                OrderQuantity.objects.create(
                    car_type=car.car_type, quantity=1, order=order
                )

            else:
                order = Order.objects.create(client=client)
                OrderQuantity.objects.create(
                    car_type=car.car_type, quantity=1, order=order
                )

            car.block(order)
            car.add_owner(client)
        return redirect("basket")


@method_decorator(login_required, name="dispatch")
class BasketView(View):
    template_name = "basket.html"

    def get(self, request, *args, **kwargs):
        owner = Client.objects.filter(email=request.user.email).first()
        order = Order.objects.filter(is_paid=False, client_id=owner).first()
        if order is None:
            return render(request, self.template_name, {"order": order})
        cars = Car.objects.filter(blocked_by_order=order).select_related("car_type")
        total_price = sum(car.car_type.price for car in cars)
        context = {
            "order": order,
            "cars": cars,
            "total_price": total_price,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        client = Client.objects.filter(email=request.user.email).first()
        order_id = request.POST.get("order_id")
        order = Order.objects.get(id=order_id)
        cars = Car.objects.filter(blocked_by_order=order, owner=client).select_related(
            "car_type"
        )
        # webhook_url = create_invoice(order, cars, "https://webhook.site/b77edef1-6a93-4fa6-8dff-ae65350eb84c")
        webhook_url = resolve_url("webhook-mono")

        create_invoice(order, cars, webhook_url)
        print(order.invoice_url)
        return redirect(order.invoice_url)


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(require_POST, name='post')
class MonoAcquiringWebhookReceiver(View):

    def post(self, request):
        try:
            verify_signature(request)
        except Exception as e:
            return JsonResponse({"status": "error"}, status=400)

        reference = request.POST.get("reference")
        order = get_object_or_404(Order, id=reference)

        if order.invoice_id != request.POST.get("invoiceId"):
            return JsonResponse({"status": "error"}, status=400)

        order.status = request.POST.get("status", "error")
        order.save()

        if order.status == "success":
            order.is_paid = True
            order.save()
            return JsonResponse({"status": "Paid"}, status=200)

        return JsonResponse({"status": "ok"})


@method_decorator(login_required, name="dispatch")
class PaymentStatusView(TemplateView):
    model = Order
    template_name = "payment_state.html"

    def get(self, request, *args, **kwargs):
        owner = Client.objects.filter(email=request.user.email).first()
        print(owner)
        if not owner:
            return render(request, self.template_name, {"order": owner})
        order = Order.objects.filter(client_id=owner)
        print(order)
        if not order:
            return render(request, self.template_name, {"order": order})
        return render(request, self.template_name, {"order": order})


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

    return redirect("cars_list")


def issuance_of_a_license(request, order_id):
    licenses = Licence.objects.filter(order_id=order_id)
    return render(request, "issuance_of_a_license.html", {"licenses": licenses, "order_id": order_id})


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
    cars = Car.objects.filter(blocked_by_order=None, owner=None).prefetch_related(
        "car_type"
    )
    car_types = (
        CarType.objects.filter(id__in=cars.values_list("car_type__id", flat=True))
        .values("brand", "name", "image")
        .distinct()
    )
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
