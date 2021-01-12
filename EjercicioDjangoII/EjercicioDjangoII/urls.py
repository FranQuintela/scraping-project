from django.urls import path
from django.contrib import admin
from main import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.inicio),
    path('carga/',views.carga),
    path('peliculasporpais/', views.lista_peliculasporpais),
    path('peliculas/', views.lista_peliculas),
    path('buscarpeliculasporgenero/', views.buscar_peliculasporgenero),
    path('buscarpeliculasporfecha/', views.buscar_peliculasporfecha),
    ]
