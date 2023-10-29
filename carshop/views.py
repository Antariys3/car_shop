from django.shortcuts import render
from .forms import CarsList


def index(request):
    return render(request, 'index.html', )


def cars_list(request):
    form = CarsList()
    return render(request, 'cars_list.html', {'form': form})
