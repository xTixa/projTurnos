from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from horarios.views import index


urlpatterns = [
    path('', index, name='home'),
    path('ei/horarios/', include('horarios.urls')),
    path('admin/', admin.site.urls),
]
