from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.test import APITransactionTestCase
import json
import responses


class CustomObtainAuthTokenTest(APITestCase):
    def test_token_creation(self):
        url = reverse("api_token_auth")
        data = {
            "username": "testuser",
            "password": "testpassword",
            "email": "test@example.com",
        }

        response = self.client.post(url, data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert "token" in response.json()
        assert (
            response.json()["token"] != ""
        )  # Check that the token is not empty

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword",
            email="test@example.com",
        )
        # self.token = Token.objects.create(user=self.user)

    def test_invalid_credentials(self):
        url = reverse("api_token_auth")
        data = {
            "username": "testuser",
            "password": "wrongpassword",
            "email": "test@example.com",
        }

        response = self.client.post(url, data, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "error" in response.json()
        assert response.json()["error"] == "Invalid credentials"


class TestCarsApi(APITransactionTestCase):
    fixtures = ["test_cars"]

    # def tearDown(self):
    #     call_command("flush", interactive=False)

    def test_cars_list(self):
        response = self.client.get("/api/cars/")
        assert response.status_code == 200
        assert response.json() == {
            "count": 2,
            "next": None,
            "previous": None,
            "results": [
                {
                    "id": 2,
                    "car_type": {
                        "id": 2,
                        "name": "A-6",
                        "brand": "AUDI",
                        "price": 12000,
                        "image": "http://testserver/carshop/static/media/audi_rs-6.jpg",
                    },
                    "color": "белый",
                    "year": 2012,
                },
                {
                    "id": 1,
                    "car_type": {
                        "id": 1,
                        "name": "Passat",
                        "brand": "Volkswagen",
                        "price": 10000,
                        "image": "http://testserver/carshop/static/media/audi_rs-6.jpg",
                    },
                    "color": "black",
                    "year": 2010,
                },
            ],
        }


class TestBasketApi(APITransactionTestCase):
    fixtures = ["test_cars"]

    def test_add_cars_to_basket(self):
        user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.client.force_authenticate(user)

        response = self.client.post("/api/add_to_cart/1/")
        assert response.status_code == 200
        assert response.json() == {
            "id": 1,
            "car_type": {
                "id": 1,
                "name": "Passat",
                "brand": "Volkswagen",
                "price": 10000,
                "image": "/carshop/static/media/audi_rs-6.jpg",
            },
            "color": "black",
            "year": 2010,
        }

    def test_views_basket(self):
        user = User.objects.create_user(
            username="testuser",
            password="testpassword",
            email="antar33@gmail.com",
        )
        self.client.force_authenticate(user)
        self.assertTrue(user.is_authenticated)
        response = self.client.get("/api/cart/")
        assert response.status_code == 200
        assert response.json() == {
            "cart": {
                "order": {
                    "id": 1,
                    "client": {
                        "id": 1,
                        "name": "Andre Tarasenko",
                        "email": "antar33@gmail.com",
                        "phone": "+48795468444",
                    },
                    "is_paid": False,
                    "invoice_url": None,
                    "status": None,
                    "invoice_id": None,
                },
                "cars": [
                    {
                        "id": 3,
                        "car_type": {
                            "id": 3,
                            "name": "Passat",
                            "brand": "Volkswagen",
                            "price": 10000,
                            "image": "/carshop/static/media/audi_rs-6.jpg",
                        },
                        "color": "black",
                        "year": 2010,
                    }
                ],
                "total_price": 10000,
            }
        }

    @responses.activate
    def test_creating_a_payment_link(self):
        user = User.objects.create_user(
            username="testuser",
            password="testpassword",
            email="antar33@gmail.com",
        )
        self.client.force_authenticate(user)
        body = {}
        responses.add(
            responses.POST,
            "https://api.monobank.ua/api/merchant/invoice/create",
            json={
                "invoiceId": 25,
                "pageUrl": "https://pay.mbnk.biz/123456iDfJtqzNXqC",
            },
        )
        response = self.client.post(
            "/api/cart/", json.dumps(body), content_type="application/json"
        )
        assert response.status_code == 200
        assert response.json() == {
            "invoice_url": "https://pay.mbnk.biz/123456iDfJtqzNXqC"
        }
