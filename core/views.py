from django.shortcuts import render

def index(request):
    return render(request, "home/index.html")

def ingresso(request):
    return render(request, "home/ingresso.html")

def plano(request):
    return render(request, "home/plano.html")

def horarios(request):
    return render(request, "home/horarios.html")

def avaliacoes(request):
    return render(request, "home/avaliacoes.html")

def contactos(request):
    return render(request, "home/contactos.html")

def informacoes(request):
    return render(request, "home/informacoes.html")

def login_view(request):
    return render(request, "auth/login.html")