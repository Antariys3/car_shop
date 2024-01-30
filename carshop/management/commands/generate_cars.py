from django.core.files import File
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction

from carshop.models import Car, CarType
from carshop.car_utils import crop_image


class CarsGenerator:
    def __init__(self, brand, name, price, color, year, image, image_name):
        self.brand = brand
        self.name = name
        self.price = price
        self.color = color
        self.year = year
        self.image = image
        self.image_name = image_name


alfa_romeo_image = "carshop/static/database_autocomplete/alfa-romeo-red_2.jpg"
audi_image = "carshop/static/database_autocomplete/audi A-6_2.jpg"
bmv_image = "carshop/static/database_autocomplete/BMW_M5_F90.png"
passat_image = "carshop/static/database_autocomplete/volkswagen-passat_2.jpg"
mercedes_image = "carshop/static/database_autocomplete/Mercedes_C205.png"

alfa_romeo = CarsGenerator(
    "Alfa Romeo",
    "Giulia",
    20000,
    "Red",
    "2015",
    alfa_romeo_image,
    "alfa_romeo_red_2.jpg",
)
audi = CarsGenerator("AUDI", "A-6", 12000, "Blue", "2012", audi_image, "audi A-6_2.jpg")
bmv = CarsGenerator("BMV", "M-5", 25000, "Blue", "2022", bmv_image, "BMW_M5_F90.png")
passat = CarsGenerator(
    "Volkswagen",
    "Passat",
    10000,
    "metallic",
    "2010",
    passat_image,
    "volkswagen-passat_2.jpg",
)
mercedes = CarsGenerator(
    "Mercedes-Benz",
    "C205",
    23000,
    "white",
    "2022",
    mercedes_image,
    "Mercedes_C205.png",
)


def generate_cars(self, car_gen):
    for _ in range(4):
        try:
            with transaction.atomic():
                car_type = CarType.objects.create(
                    brand=car_gen.brand, name=car_gen.name, price=car_gen.price
                )
                if car_gen.image:
                    image_content = open(car_gen.image, "rb").read()
                    image_file = ContentFile(image_content)
                    car_type.image.save(
                        car_gen.image_name, crop_image(File(image_file))
                    )
                car = Car(car_type=car_type, color=car_gen.color, year=car_gen.year)
                car.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Successfully added car: {car_type.brand} {car_type.name}"
                    )
                )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {e}"))


class Command(BaseCommand):
    help = "Generation of adding four types of cars, three each, to the database."

    def handle(self, *args, **options):
        generate_cars(self, bmv)
        generate_cars(self, audi)
        generate_cars(self, alfa_romeo)
        generate_cars(self, passat)
        generate_cars(self, mercedes)
