from datetime import datetime

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

    quantity = forms.IntegerField(
        label="Количество машин",
        widget=forms.NumberInput(attrs={"class": "form-control"}),
        validators=[
            MinValueValidator(0, message="Количество машин должно быть положительным"),
            MaxValueValidator(20, message="Максимум 20 машин"),
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
