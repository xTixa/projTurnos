
from django.http import HttpResponse

def index(request):
    return HttpResponse("<h1>Bem-vindo ao projeto Django!</h1><p>Página principal básica de teste.</p>")
