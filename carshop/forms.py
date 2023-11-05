from django import forms

from .models import CarType, Car, Client


class CarsList(forms.Form):
    clients = Client.objects.all()
    client_choices = [(client.id, client.name) for client in clients]
    client = forms.ModelChoiceField(
        queryset=Client.objects.all(),
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Выберите клиента",
        empty_label="Покупатель не выбран"
    )

    def __init__(self, *args, **kwargs):
        super(CarsList, self).__init__(*args, **kwargs)

        car_types = CarType.objects.values_list("name", flat=True).distinct()

        for car_type in car_types:
            car_count = Car.objects.filter(
                car_type__name=car_type, blocked_by_order=None
            ).count()
            quantity_choices = [(str(i), str(i)) for i in range(0, car_count + 1)]
            car_type_obj = CarType.objects.filter(name=car_type).first()
            car_brand = car_type_obj.brand

            self.fields[car_type] = forms.ChoiceField(
                label=f"{car_brand} {car_type}",
                choices=quantity_choices,
                widget=forms.Select(attrs={"class": "form-control"}),
                required=False
            )

    def clean_client(self):
        client = self.cleaned_data.get("client")
        if not client:
            raise forms.ValidationError("Выберите клиента")
        return client

    def clean(self):
        cleaned_data = super().clean()

        for car_type, quantity in cleaned_data.items():
            if car_type not in ["client"] and quantity is not None:
                cleaned_data[car_type] = int(quantity)

        return cleaned_data
