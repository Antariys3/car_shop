from allauth.account.views import SignupView
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import UpdateView, DeleteView
from rest_framework.reverse import reverse

from carshop.forms import CustomSignupForm, SellCarsFormView
from carshop.images_processing import crop_image
from carshop.invoices import create_invoice
from carshop.models import Car, CarType, Order, OrderQuantity
from carshop.views.utils import order_saver, cars_counter, img_finder, reset_car


def logout_view(request):
    logout(request)
    return redirect("cars_list")


class CarsShopView(ListView):

    model = Car
    template_name = "cars_list.html"
    context_object_name = "cars"
    paginate_by = 12

    def get_queryset(self):
        return Car.objects.filter(blocked_by_order=None, owner=None).select_related(
            "car_type"
        )

    # processing the add to cart button
    @method_decorator(login_required, name="dispatch")
    def post(self, request, *args, **kwargs):

        client = request.user
        car_id = request.POST.get("car_id")
        car = Car.objects.select_related("car_type").get(id=car_id)

        order = Order.objects.filter(client_id=client.id, is_paid=False).first()
        order_saver(order, client, car)

        self.object_list = self.get_queryset()
        return self.render_to_response(self.get_context_data())


class CarDetailView(View):
    model = Car
    template_name = "car_detail.html"
    not_found_template_name = "car_not_found.html"

    def get(self, request, *args, **kwargs):
        car_id = self.kwargs.get("car_id")
        car = Car.objects.filter(id=car_id).prefetch_related("car_type").first()
        if car is None:
            return render(request, self.not_found_template_name)
        cars_count = cars_counter(car)
        return render(
            request, self.template_name, {"car": car, "cars_count": cars_count}
        )

    @method_decorator(login_required, name="dispatch")
    def post(self, request, *args, **kwargs):
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
        order = Order.objects.filter(client_id=request.user, is_paid=False).first()
        for car in cars:
            order_saver(order, request.user, car)
        return redirect("cart")


@method_decorator(login_required, name="dispatch")
class CartView(View):
    template_name = "cart.html"

    def get(self, request, *args, **kwargs):
        print("type Cart", type(request.user))
        order = Order.objects.filter(is_paid=False, client_id=request.user).first()
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

        order_id = request.POST.get("order_id")
        order = Order.objects.get(id=order_id)
        cars = Car.objects.filter(
            blocked_by_order=order, owner=request.user
        ).select_related("car_type")
        create_invoice(order, cars, reverse("webhook-mono", request=request))
        return redirect(order.invoice_url)


@method_decorator(login_required, name="dispatch")
class PaymentStatusView(TemplateView):
    model = Order
    template_name = "payment/payment_state.html"

    def get(self, request, *args, **kwargs):
        owner = request.user
        if not owner:
            return render(request, self.template_name, {"order": owner})
        order = Order.objects.filter(client_id=owner)
        if not order:
            return render(request, self.template_name, {"order": order})
        return render(request, self.template_name, {"order": order})


@method_decorator(login_required, name="dispatch")
class PaymentStatusDetailsView(TemplateView):
    template_name = "payment/payment_status_details.html"

    def get(self, request, *args, **kwargs):
        order_id = kwargs.get("order_id")

        order_quantities = OrderQuantity.objects.filter(order=order_id)

        cars_in_order = [
            {
                "brand": order_quantity.car_type.brand,
                "name": order_quantity.car_type.name,
                "price": order_quantity.car_type.price,
                "image": img_finder(order_quantity),
            }
            for order_quantity in order_quantities
        ]

        return render(
            request,
            self.template_name,
            {"cars_in_order": cars_in_order, "order": order_quantities},
        )


@method_decorator(login_required, name="dispatch")
class DeleteOrderView(DetailView):
    def post(self, request, *args, **kwargs):
        order_id = self.kwargs.get("order_id")
        cars = Car.objects.filter(blocked_by_order=order_id)
        [reset_car(car) for car in cars]
        order = get_object_or_404(Order, id=order_id)
        order.delete()
        return redirect("cars_list")


@method_decorator(login_required, name="dispatch")
class SellCarView(View):
    template_name = "sell_cars.html"

    def get(self, request):
        form = SellCarsFormView()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = SellCarsFormView(request.POST, request.FILES)
        if form.is_valid():
            brand = form.cleaned_data["brand"]
            name = form.cleaned_data["name"]
            price = form.cleaned_data["price"]
            color = form.cleaned_data["color"]
            year = form.cleaned_data["year"]
            image = form.cleaned_data["image"]

            try:
                with transaction.atomic():
                    car_type = CarType.objects.create(
                        brand=brand, name=name, price=price
                    )
                    car_type.image.save(f"{image}", crop_image(image))
                    car = Car(
                        car_type=car_type, color=color, year=year, seller=request.user
                    )
                    car.save()
            except ValidationError as e:
                print(f"ValidationError: {e}")
            return redirect("cars_list")
        return render(request, self.template_name, {"form": form})


@method_decorator(login_required, name="dispatch")
class MyListedCarsView(ListView):
    model = Car
    template_name = "my_listed_cars.html"
    success_url = reverse_lazy("cars_list")

    def get(self, request, *args, **kwargs):
        list_cars_sell = Car.objects.filter(
            blocked_by_order=None, seller=request.user
        ).select_related("car_type")
        return render(request, self.template_name, {"list_cars_sell": list_cars_sell})


@method_decorator(login_required, name="dispatch")
class SellCarUpdateView(UpdateView):
    model = Car
    form_class = SellCarsFormView
    template_name = "sell_cars/sell_car_update.html"

    def get_queryset(self):
        return super().get_queryset().select_related("car_type")

    def get_object(self, queryset=None):
        return get_object_or_404(Car, pk=self.kwargs["pk"], seller=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        car = self.get_object()
        initial_data = {
            "brand": car.car_type.brand,
            "name": car.car_type.name,
            "price": car.car_type.price,
            "image": car.car_type.image,
            "color": car.color,
            "year": car.year,
        }

        form = self.form_class(initial=initial_data)
        context["image_url"] = car.car_type.image.url if car.car_type.image else None
        context["form"] = form
        return context

    def post(self, request, *args, **kwargs):
        car_instance = self.get_object()
        car_type_instance = car_instance.car_type

        car_instance.color = request.POST.get("color")
        car_instance.year = request.POST.get("year")
        car_type_instance.brand = request.POST.get("brand")
        car_type_instance.name = request.POST.get("name")
        car_type_instance.price = request.POST.get("price")
        image = request.FILES.get("image")
        if image:
            car_type_instance.image.save(image.name, crop_image(image))

        try:
            with transaction.atomic():
                car_instance.save()
                car_type_instance.save()
        except ValidationError as e:
            print(f"ValidationError: {e}")
        return redirect("cars_list")


@method_decorator(login_required, name="dispatch")
class SellCarDeleteView(DeleteView):
    model = Car
    template_name = "sell_cars/sell_car_delete.html"
    success_url = reverse_lazy("cars_list")

    def form_valid(self, form):
        return super().form_valid(form)


class CustomSignupView(SignupView):
    form_class = CustomSignupForm
