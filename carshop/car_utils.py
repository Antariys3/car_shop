from io import BytesIO

from PIL import Image
from django.core.files.base import ContentFile
from faker import Faker

from carshop.models import Client

fake = Faker("ru_RU")


def create_clients(user):
    client = Client.objects.filter(email=user.email).first()
    if client:
        return client

    if user.first_name and user.last_name:
        client_name = f"{user.first_name} {user.last_name}"
    else:
        client_name = user.username
    client = Client.objects.create(
        name=client_name, email=user.email, phone=fake.phone_number()
    )
    return client


def crop_image(image):
    # function that crops the image to an aspect ratio of 4:3
    img = Image.open(image)
    aspect_ratio = 4 / 3
    width, height = img.size
    new_width = int(height * aspect_ratio)
    left_margin = int((width - new_width) / 2)
    right_margin = int(width - left_margin)
    img_cropped = img.crop((left_margin, 0, right_margin, height))

    img_cropped = img_cropped.convert("RGB")
    output_buffer = BytesIO()
    img_cropped.save(output_buffer, format="JPEG")

    return ContentFile(output_buffer.getvalue())
