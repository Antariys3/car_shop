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
    index,
    orders_page,
    delete_order,
    payment,
    sell_cars,
    logout_view,
    image_edit,
    CarsShopView,
    CarDetailView,
    BasketView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("carshop.urls")),
    path("", index, name="home"),
    path("cars_list/", CarsShopView.as_view(), name="cars_list"),
    path("car/<int:car_id>/", CarDetailView.as_view(), name="car_detail"),
    path("basket/", BasketView.as_view(), name="basket"),
    path("orders_page/", orders_page, name="orders_page"),
    path("order/<int:order_id>/delete/", delete_order, name="delete_order"),
    path("payment/<int:order_id>/", payment, name="payment"),
    path("sell_cars/", sell_cars, name="sell_cars"),
    path("logout", logout_view, name="logout"),
    path("accounts/", include("allauth.urls"), name="google_login"),
    path("image_edit/", image_edit, name="image_edit"),
]
