from io import BytesIO

# TODO below lib is not in requirements
from PIL import Image
from django.core.files.base import ContentFile

from carshop.constants import ASPECT_RATIO


# TODO this file should be in other app
def crop_image(image):
    # function that crops the image to an aspect ratio of 16:9
    img = Image.open(image)
    width, height = img.size
    target_width = int(height * ASPECT_RATIO)

    img_cropped = cropping_img(
        height,
        img,
        target_width,
        width,
    )

    img_cropped_to_RGB = img_cropped.convert("RGB")
    output_buffer = BytesIO()
    img_cropped_to_RGB.save(output_buffer, format="PNG")

    return ContentFile(output_buffer.getvalue(), name=image.name)


def cropping_img(height, img, target_width, width):
    # If the image width is larger than the target width, crop the sides
    if width > target_width:
        left_margin = int((width - target_width) / 2)
        right_margin = int(width - left_margin)
        img_cropped = img.crop((left_margin, 0, right_margin, height))

    # If the image height is greater than the target, crop the top and bottom
    elif width < target_width:
        target_height = int(width / ASPECT_RATIO)
        top_margin = int((height - target_height) / 2)
        bottom_margin = int(height - top_margin)
        img_cropped = img.crop((0, top_margin, width, bottom_margin))

    else:
        img_cropped = img.copy()
    return img_cropped
