from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

def index(request):
    return HttpResponse("Bem-vindo ao projeto!")

urlpatterns = [
    path('', index),  # Define a rota principal
    path('ei/horarios/', include('horarios.urls')),
]
