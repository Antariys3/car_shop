from django.core.files import File
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction

from carshop.images_processing import crop_image
from carshop.models import Car, CarType


class CarsGenerator:
    def __init__(self, car_data):
        self.brand = car_data.get("brand")
        self.name = car_data.get("name")
        self.price = car_data.get("price")
        self.color = car_data.get("color")
        self.year = car_data.get("year")
        self.image = car_data.get("image")
        self.image_name = car_data.get("image_name")


alfa_romeo_data = {
    "brand": "Alfa Romeo",
    "name": "Giulia",
    "price": 20000,
    "color": "Red",
    "year": "2015",
    "image": "carshop/static/database_autocomplete/alfa-romeo-red_2.jpg",
    "image_name": "alfa_romeo_red_2.jpg",
}
alfa_romeo = CarsGenerator(alfa_romeo_data)

audi_data = {
    "brand": "AUDI",
    "name": "A-6",
    "price": 12000,
    "color": "Blue",
    "year": "2012",
    "image": "carshop/static/database_autocomplete/audi A-6_2.jpg",
    "image_name": "audi A-6_2.jpg",
}
audi = CarsGenerator(audi_data)

bmv_data = {
    "brand": "BMV",
    "name": "M-5",
    "price": 25000,
    "color": "Blue",
    "year": "2022",
    "image": "carshop/static/database_autocomplete/BMW_M5_F90.png",
    "image_name": "BMW_M5_F90.png",
}
bmv = CarsGenerator(bmv_data)

passat_data = {
    "brand": "Volkswagen",
    "name": "Passat",
    "price": 10000,
    "color": "metallic",
    "year": "2010",
    "image": "carshop/static/database_autocomplete/volkswagen-passat_2.jpg",
    "image_name": "volkswagen-passat_2.jpg",
}
passat = CarsGenerator(passat_data)

mercedes_data = {
    "brand": "Mercedes-Benz",
    "name": "C205",
    "price": 23000,
    "color": "white",
    "year": "2022",
    "image": "carshop/static/database_autocomplete/Mercedes_C205.png",
    "image_name": "Mercedes_C205.png",
}
mercedes = CarsGenerator(mercedes_data)


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
                car = Car(
                    car_type=car_type, color=car_gen.color, year=car_gen.year
                )
                car.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Successfully added car: {car_type.brand} {car_type.name}"
                    )
                )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {e}"))


class Command(BaseCommand):
    help = (
        "Generation of adding four types of cars, three each, to the database."
    )

    def handle(self, *args, **options):
        generate_cars(self, bmv)
        generate_cars(self, audi)
        generate_cars(self, alfa_romeo)
        generate_cars(self, passat)
        generate_cars(self, mercedes)
