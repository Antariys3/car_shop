from datetime import datetime

from allauth.account.forms import SignupForm
from django.contrib.auth.models import User
from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator
from django.forms import ModelForm

from .models import CarType


class CreateCarsForm(ModelForm):
    colors = ["белый", "черный", "металик", "красный", "синий", "зеленый", "желтый"]

    color = forms.ChoiceField(
        label="Цвет",
        choices=[(color, color) for color in colors],
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    year = forms.IntegerField(
        label="Год",
        widget=forms.NumberInput(attrs={"class": "form-control"}),
        validators=[
            MinValueValidator(2000, message="Год должен быть не менее 2000"),
            MaxValueValidator(
                datetime.today().year, message="Год не может быть в будущем"
            ),
        ],
    )

    class Meta:
        model = CarType
        fields = ["brand", "name", "price", "image"]

        labels = {
            "brand": "Бренд",
            "name": "Марка",
            "price": "Цена",
            "image": "Выберите фото",
        }

        widgets = {
            "brand": forms.TextInput(attrs={"class": "form-control"}),
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "price": forms.NumberInput(attrs={"class": "form-control"}),
            "image": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }

    def clean_image(self):
        image = self.cleaned_data.get("image")
        if not image:
            raise forms.ValidationError("Не выбрана фотография машины")
        return image


class CustomSignupForm(SignupForm):
    username = forms.CharField(
        label="Имя пользователя", widget=forms.TextInput(attrs={"class": "form-input"})
    )
    email = forms.EmailField(
        label="Email", widget=forms.EmailInput(attrs={"class": "form-input"})
    )
    password1 = forms.CharField(
        label="Пароль", widget=forms.PasswordInput(attrs={"class": "form-input"})
    )
    password2 = forms.CharField(
        label="Повтор пароля", widget=forms.PasswordInput(attrs={"class": "form-input"})
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user
