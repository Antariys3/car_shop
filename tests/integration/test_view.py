import re

import pytest
import requests
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from carshop.models import Car, Order

SERVER_URL = "https://boiling-fortress-51276-88bb58822abe.herokuapp.com/api/"


def test_get_api_cars():
    r = requests.get(SERVER_URL + "cars/")
    r.raise_for_status()
    assert r.status_code == 200


def test_get_api_car_by_id():
    car_id = "100"
    expected_url = f"{SERVER_URL}cars/{car_id}"
    expected_response = {
        "id": 100,
        "car_type": {
            "id": 102,
            "name": "Astra",
            "brand": "Opel",
            "price": 9000,
            "image": re.compile(
                r"https://cars-shop-aws\.s3\.amazonaws\.com/Images_of_cars/Opel_Astra_blue\.png.*"
            ),
        },
        "color": "синий",
        "year": 2009,
    }

    try:
        response = requests.get(expected_url)
        response.raise_for_status()
    except HTTPError as e:
        pytest.fail(f"Request failed with status code {e.response.status_code}")

    assert response.status_code == 200
    assert expected_response["car_type"]["image"].match(
        response.json()["car_type"]["image"]
    )
    expected_response["car_type"]["image"] = response.json()["car_type"][
        "image"
    ]
    assert response.json() == expected_response
