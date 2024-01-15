import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from django.urls import reverse
from carshop.models import Car, Order
from rest_framework import status
import requests
import re

SERVER_URL = "https://boiling-fortress-51276-88bb58822abe.herokuapp.com/api/"


# def test_get_api_cars():
#     r = requests.get(SERVER_URL + "cars/")
#     r.raise_for_status()
#     assert r.status_code == 200

# def test_get_api_car_by_id():
#     car_id = "100"
#     expected_url = f"{SERVER_URL}cars/{car_id}"
#     expected_response = {
#         "id": 100,
#         "car_type": {
#             "id": 102,
#             "name": "Astra",
#             "brand": "Opel",
#             "price": 9000,
#             "image": re.compile(r'https://cars-shop-aws\.s3\.amazonaws\.com/Images_of_cars/Opel_Astra_blue\.png.*')
#         },
#         "color": "синий",
#         "year": 2009
#     }
#
#     try:
#         response = requests.get(expected_url)
#         response.raise_for_status()
#     except HTTPError as e:
#         pytest.fail(f"Request failed with status code {e.response.status_code}")
#
#     assert response.status_code == 200
#     assert expected_response["car_type"]["image"].match(response.json()["car_type"]["image"])
#     expected_response["car_type"]["image"] = response.json()["car_type"]["image"]
#     assert response.json() == expected_response

@pytest.mark.django_db
def test_add_to_cart_api():
    # Создаем тестового пользователя
    user = User.objects.create_user(username='testuser', password='testpassword')

    # Создаем тестовую машину
    car = Car.objects.create(
        car_type_id=110,  # Замените на реальный ID типа машины
        color='Red',
        year=2022
    )

    client = APIClient()
    client.force_authenticate(user=user)

    url = reverse('add-to-cart', kwargs={'car_id': car.id})
    response = client.post(url)

    assert response.status_code == status.HTTP_200_OK
    assert 'invoice_url' in response.data
