from django.shortcuts import render

def index(request):
    return render(request, "home/index.html")

def login_view(request):
    return render(request, "auth/login.html")