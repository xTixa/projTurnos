from django.urls import path
from .views import caixa_sugestoes

app_name = "extra_app"

urlpatterns = [
    #path("sugestao-teste/", inserir_sugestao_teste, name="sugestao_teste"), # Rota para inserir sugestão de teste "inserir_sugestao_teste é uma função que foi criada na views.py"
    path("sugestao/", caixa_sugestoes, name="sugestao"), # Rota para inserir sugestão de teste "inserir_sugestao_teste é uma função que foi criada na views.py"
]
