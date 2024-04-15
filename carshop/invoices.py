import base64
import hashlib

import ecdsa

# TODO above library is not in requirements.
import requests
from django.conf import settings

from carshop.constants import PUBLIC_KEY, REDIRECT_URL
from carshop.models import Order


def verify_signature(request):
    x_sing_base64 = request.headers["X-Sign"]
    body_test = request.body
    print(body_test)
    public_key_bytes = base64.b64decode(PUBLIC_KEY)
    signature_bytes = base64.b64decode(x_sing_base64)
    pub_key = ecdsa.VerifyingKey.from_pem(public_key_bytes.decode())

    ok = pub_key.verify(
        signature_bytes,
        body_test,
        sigdecode=ecdsa.util.sigdecode_der,
        hashfunc=hashlib.sha256,
    )
    print(ok)
    if not ok:
        raise Exception("Signature is not valid")


def create_invoice(order: Order, cars, webhook_url):
    amount, basket_order = basket_generator(cars)
    r = payment_request(amount, basket_order, order, webhook_url)
    r.raise_for_status()
    creating_order(order, r)


def payment_request(amount, basket_order, order, webhook_url):
    merchants_info = {
        "reference": str(order.id),
        "destination": "Купівля машин",
        "basketOrder": basket_order,
    }
    request_body = {
        "redirectUrl": REDIRECT_URL,
        "webHookUrl": webhook_url,
        "amount": amount,
        "merchantPaymInfo": merchants_info,
    }
    headers = {"X-Token": settings.MONOBANK_TOKEN}
    r = requests.post(
        "https://api.monobank.ua/api/merchant/invoice/create",
        json=request_body,
        headers=headers,
    )
    return r


def basket_generator(cars):
    amount = 0
    basket_order = []
    for car in cars:
        sum_ = car.car_type.price * 100
        amount += sum_
        basket_order.append(
            {
                "name": f"{car.car_type.brand} {car.car_type.name}",
                "qty": 1,
                "sum": sum_,
                "icon": car.car_type.image.url,
                "unit": "шт.",
            }
        )
    return amount, basket_order


def creating_order(order, r):
    order.invoice_id = r.json()["invoiceId"]
    order.invoice_url = r.json()["pageUrl"]
    order.status = "created"
    order.save()
