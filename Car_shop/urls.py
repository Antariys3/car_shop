"""
URL configuration for Car_shop project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include

from carshop.views import (
    delete_order,
    SellCarView,
    logout_view,
    image_edit,
    CarsShopView,
    CarDetailView,
    CartView,
    PaymentStatusView,
    PaymentStatusDetailsView,
    CustomSignupView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("carshop.urls")),
    path("", CarsShopView.as_view(), name="cars_list"),
    path("car/<int:car_id>/", CarDetailView.as_view(), name="car_detail"),
    path("cart/", CartView.as_view(), name="cart"),
    path("order/<int:order_id>/delete/", delete_order, name="delete_order"),
    path("sell_cars/", SellCarView.as_view(), name="sell_cars"),
    path("logout", logout_view, name="logout"),
    path("login/", include("allauth.account.urls"), name="account_login"),
    path("accounts/", include("allauth.urls")),
    path("accounts/", include("allauth.socialaccount.urls")),
    path("signup/", CustomSignupView.as_view(), name="custom_signup"),
    path("image_edit/", image_edit, name="image_edit"),
    path("payment_status/", PaymentStatusView.as_view(), name="payment_status"),
    path(
        "payment_status_details/<int:order_id>/",
        PaymentStatusDetailsView.as_view(),
        name="payment_status_details",
    ),
]
