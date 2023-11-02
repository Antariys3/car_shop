from django.db import models

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

    def __str__(self):
        return f"{self.brand} {self.name}"


class Car(models.Model):
    car_type = models.ForeignKey(CarType, on_delete=models.CASCADE)
    color = models.CharField(max_length=50)
    year = models.IntegerField()
    # заблокирован по приказу
    blocked_by_order = models.ForeignKey(
        "Order", on_delete=models.SET_NULL, null=True, related_name="reserved_cars"
    )
    # владелец
    owner = models.ForeignKey(
        Client, on_delete=models.SET_NULL, null=True, related_name="cars"
    )

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

    def add_owner(self, client):
        self.owner = client
        self.save()

    def remove_owner(self):
        self.owner = None
        self.save()

    def __str__(self):
        return self.color


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
    clients = models.ManyToManyField(Client, related_name="dealerships")

    def __str__(self):
        return self.name


class Order(models.Model):  # Заказ
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="orders")
    # оплачено
    is_paid = models.BooleanField(default=False)


class OrderQuantity(models.Model):  # Заказанное Количество
    car_type = models.ForeignKey(
        CarType, on_delete=models.CASCADE, related_name="order_quantities"
    )
    quantity = models.PositiveIntegerField(default=1)
    # Заказ
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="car_types")
