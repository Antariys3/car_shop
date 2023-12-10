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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import (
    LoginView,
    PasswordResetConfirmView,
)
from django.urls import path

from carshop.views import (
    index,
    cars_list,
    orders_page,
    order_detail,
    delete_order,
    payment,
    create_cars,
    register,
    logout_view,
    activate,
    checking_mail,
    ResetPasswordView,
    create_car_photo,
)


class ResetView:
    pass


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", index, name="home"),
    path("cars_list/", cars_list, name="cars_list"),
    path("orders_page/", orders_page, name="orders_page"),
    path("order/<int:pk>/", order_detail, name="order_detail"),
    path("order/<int:order_id>/delete/", delete_order, name="delete_order"),
    path("payment/<int:order_id>/", payment, name="payment"),
    path("create_cars/", create_cars, name="create_cars"),
    path("register/", register, name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout", logout_view, name="logout"),
    path("activate/<user_signed>", activate, name="activate"),
    path("checking_mail/", checking_mail, name="checking_mail"),
    path("password_reset/", ResetPasswordView.as_view(), name="password_reset"),
    path(
        "forgot_password/confirm/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(
            template_name="registration/password_reset_confirm.html",
            success_url="/login/",
        ),
        name="password_reset_confirm",
    ),
    path("create_photo/", create_car_photo, name="create_photo")
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)