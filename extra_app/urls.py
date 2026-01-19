from django.urls import path
from .views import caixa_sugestoes, feedback_sugestao, sugestoes_todas, sugestoes_eliminar

app_name = "extra_app"

urlpatterns = [
    #path("sugestao-teste/", inserir_sugestao_teste, name="sugestao_teste"), # Rota para inserir sugestão de teste "inserir_sugestao_teste é uma função que foi criada na views.py"
    path("sugestao/", caixa_sugestoes, name="sugestao"), # Rota para inserir sugestão de teste "inserir_sugestao_teste é uma função que foi criada na views.py"
    path("sugestao/feedback/<str:sugestao_id>/", feedback_sugestao, name="feedback_sugestao"), # Rota para dar like numa sugestão
    path("sugestao/list/", sugestoes_todas, name="sugestoes_todas"), #sugestoes_todas
    path("sugestao/eliminar/<str:sugestao_id>/", sugestoes_eliminar, name="sugestoes_eliminar"), # Eliminar sugestão
]
