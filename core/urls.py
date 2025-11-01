from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "home"

urlpatterns = [
    path("", views.index, name="index"),
    path("ingresso/", views.ingresso, name="ingresso"),
    path("plano/", views.plano, name="plano"),
    path("horarios/", views.horarios, name="horarios"),
    path("avaliacoes/", views.avaliacoes, name="avaliacoes"),
    path("contactos/", views.contactos, name="contactos"),
    path("informacoes/", views.informacoes, name="informacoes"),
    path("perfil/", views.perfil, name="perfil"),
    path("login/",  auth_views.LoginView.as_view(template_name="auth/login.html"), name="login"),
    path("logout/", views.do_logout, name="logout"),
    path("turnos/inscrever/<int:turno_id>/", views.inscrever_turno, name="inscrever_turno"),
]
