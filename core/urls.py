from django.urls import path
from . import views

app_name = "home"

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("ingresso/", views.ingresso, name="ingresso"),
    path("plano/", views.plano, name="plano"),
    path("horarios/", views.horarios, name="horarios"),
    path("avaliacoes/", views.avaliacoes, name="avaliacoes"),
    path("contactos/", views.contactos, name="contactos"),
    path("informacoes/", views.informacoes, name="informacoes"),
    path("inscricao_turno/", views.inscricao_turno, name="inscricao_turno"),
]