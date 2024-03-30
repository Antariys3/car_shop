from django.urls import path
from rest_framework import routers
from rest_framework.authtoken import views

from carshop.api import (
    CarsAPIView,
    CustomObtainAuthToken,
    AddToCartAPIView,
    CartAPIView,
    MonoAcquiringWebhookReceiver,
    PaymentStatusApi,
)

router = routers.DefaultRouter()
router.register("cars", CarsAPIView, "cars")

urlpatterns = router.urls
urlpatterns += [
    path("api-token-auth/", CustomObtainAuthToken.as_view(), name="api_token_auth"),
    path("add_to_cart/<int:car_id>/", AddToCartAPIView.as_view(), name="add_to_cart"),
    path("cart/", CartAPIView.as_view(), name="cart"),
    path("cart/<int:pk>/", CartAPIView.as_view(), name="cart-detail"),
    path("webhook-mono/", MonoAcquiringWebhookReceiver.as_view(), name="webhook-mono"),
    path("payment_status/<int:order_number>/", PaymentStatusApi.as_view(), name="payment_status"),
]
