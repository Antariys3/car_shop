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
    # function that crops the image to an aspect ratio of 16:9
    img = Image.open(image)
    aspect_ratio = 16 / 9
    width, height = img.size
    target_width = int(height * aspect_ratio)

    # Если ширина изображения больше целевой, обрезаем по бокам
    if width > target_width:
        left_margin = int((width - target_width) / 2)
        right_margin = int(width - left_margin)
        img_cropped = img.crop((left_margin, 0, right_margin, height))
    # Если высота изображения больше целевой, обрезаем сверху и снизу
    elif width < target_width:
        target_height = int(width / aspect_ratio)
        top_margin = int((height - target_height) / 2)
        bottom_margin = int(height - top_margin)
        img_cropped = img.crop((0, top_margin, width, bottom_margin))
    else:
        img_cropped = img.copy()

    img_cropped = img_cropped.convert("RGB")
    output_buffer = BytesIO()
    img_cropped.save(output_buffer, format="PNG")

    return ContentFile(output_buffer.getvalue(), name=image.name)
