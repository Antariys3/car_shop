from django.core.files import File
from django.core.files.base import ContentFile
from PIL import Image
from django.core.management.base import BaseCommand
from django.db import transaction

from carshop.car_utils import crop_image
from carshop.models import Car, CarType


class CarsGenerator:
    def __init__(self, brand, name, price, color, year, image=None, image_name=None):
        self.brand = brand
        self.name = name
        self.price = price
        self.color = color
        self.year = year
        self.image = image
        self.image_name = image_name


# def generate_cars(gen):


class Command(BaseCommand):
    help = 'Generate and add cars to the database.'

    def handle(self, *args, **options):
        # bmv_image = Image.open("carshop/static/database_autocomplete/BMW_M5_F90.png")
        audi_photo = "carshop/static/database_autocomplete/alfa_romeo_2_2.jpeg"
        bmv_image = "carshop/static/database_autocomplete/BMW_M5_F90.png"
        bmv = CarsGenerator("BMV", "M-5", 25000, "Blue", "2022", bmv_image, "BMW_M5_F90.png")
        for _ in range(2):
            try:
                with transaction.atomic():
                    car_type = CarType.objects.create(brand=bmv.brand, name=bmv.name, price=bmv.price)
                    if bmv.image:
                        image_content = open(bmv.image, "rb").read()
                        image_file = ContentFile(image_content)
                        car_type.image.save(bmv.image_name, File(image_file))
                    car = Car(car_type=car_type, color=bmv.color, year=bmv.year)
                    car.save()
            except Exception as e:
                print(f"Ошибка: {e}")
