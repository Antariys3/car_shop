from django import forms
from .models import CarType, Car, Client


class CarsList(forms.Form):
    car_types = CarType.objects.values_list('name', flat=True).distinct()

    for car_type in car_types:
        car_count = Car.objects.filter(car_type__name=car_type, blocked_by_order=None).count()
        quantity_choices = [(str(i), str(i)) for i in range(0, car_count + 1)]
        car_type_obj = CarType.objects.filter(name=car_type).first()
        car_brand = car_type_obj.brand

        # Создаем поле формы для каждого типа машины
        locals()[car_type] = forms.ChoiceField(
            label=f'{car_brand} {car_type}',
            choices=quantity_choices,
            widget=forms.Select(attrs={'class': 'form-control'})
        )
    clients = Client.objects.all()
    client_choices = [(client.id, client.name) for client in clients]
    client = forms.ModelChoiceField(
        queryset=Client.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Выберите клиента'
    )
