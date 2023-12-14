from django.core.management.base import BaseCommand
from faker import Faker

from carshop.models import Client

fake = Faker("ru_RU")


class Command(BaseCommand):
    help = "Add the specified number of clients to the database"

    def add_arguments(self, parser):
        parser.add_argument("number", nargs="?", type=int, default=5)

    def handle(self, *args, **options):
        for number_of_clients in range(options["number"]):
            client = Client.objects.create(
                name=fake.name_male(),
                email=fake.ascii_free_email(),
                phone=fake.phone_number(),
            )

            self.stdout.write(
                self.style.SUCCESS('Successfully added client "%s"' % client.id)
            )
