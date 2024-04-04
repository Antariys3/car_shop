from django.db import models
from django.contrib.auth.models import User

from carshop.faker import fake


class Client(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=254)
    phone = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class CarType(models.Model):
    name = models.CharField(max_length=50)
    brand = models.CharField(max_length=50)
    price = models.PositiveIntegerField()
    image = models.ImageField(upload_to="Images_of_cars", null=True, blank=True)

    def __str__(self):
        return f"{self.brand} {self.name}"


class Car(models.Model):
    car_type = models.ForeignKey(CarType, on_delete=models.CASCADE)
    color = models.CharField(max_length=50)
    year = models.IntegerField()
    blocked_by_order = models.ForeignKey(
        "Order", on_delete=models.SET_NULL, null=True, related_name="reserved_cars"
    )
    owner = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="cars"
    )
    seller = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="cars_sold")

    def block(self, order):
        self.blocked_by_order = order
        self.save()

    def unblock(self):
        self.blocked_by_order = None
        self.save()

    def sell(self):
        if not self.blocked_by_order:
            raise Exception("Car is not reserved")
        self.owner = self.blocked_by_order.client
        self.save()

    def add_owner(self, user):
        self.owner = user
        self.save()

    def add_seller(self, user):
        self.seller = user
        self.save()

    def remove_owner(self):
        self.owner = None
        self.save()

    def __str__(self):
        return self.color

    class Meta:
        ordering = ["-id"]


class Licence(models.Model):
    car = models.OneToOneField(
        Car, on_delete=models.SET_NULL, null=True, related_name="licence"
    )
    number = models.CharField(max_length=50)
    order = models.ForeignKey(
        "Order", on_delete=models.CASCADE, related_name="car_licence"
    )

    def create_car_number(self):
        self.number = fake.car_number()
        self.save()

    def __str__(self):
        return self.number


class Dealership(models.Model):
    name = models.CharField(max_length=50)
    available_car_types = models.ManyToManyField(CarType, related_name="dealerships")
    clients = models.ManyToManyField(User, related_name="dealerships")

    def __str__(self):
        return self.name


class Order(models.Model):
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    is_paid = models.BooleanField(default=False)
    invoice_url = models.CharField(max_length=100, null=True)
    status = models.CharField(max_length=100, null=True)
    invoice_id = models.CharField(max_length=100, null=True)


class OrderQuantity(models.Model):
    car_type = models.ForeignKey(
        CarType, on_delete=models.CASCADE, related_name="car_types"
    )
    quantity = models.PositiveIntegerField(default=1)
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="order_quantities"
    )


class Seller(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="seller_profile")
    car_type = models.ManyToManyField(CarType, related_name="sellers")


class CarPhotos(models.Model):
    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to="images", blank=True)


class MonoSettings(models.Model):
    public_key = models.CharField(max_length=250, unique=True)
    received_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def create_new(cls, get_monobank_public_key_callback):
        return cls.objects.create(public_key=get_monobank_public_key_callback())

    @classmethod
    def get_latest_or_add(cls, get_monobank_public_key_callback):
        latest = cls.objects.order_by("-received_at").first()
        if not latest:
            latest = cls.create_new(get_monobank_public_key_callback)
        return latest
