"""
URL configuration for Carshop project.

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
from django.urls import path

from carshop.views import index, cars_list, orders_page, order_edit

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='home'),
    path('cars_list/', cars_list, name='cars_list'),
    path('orders_page/', orders_page, name='orders_page'),
    path("order_edit/<int:pk>/", order_edit, name='order_edit'),
]