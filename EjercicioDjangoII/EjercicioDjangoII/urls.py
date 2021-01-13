from django.urls import path
from django.contrib import admin
from main import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.inicio),
    path('carga/',views.carga),
    path('loadRS', views.loadRS),

    path('productstoprated/', views.list_products_top_rated),
    path('products/', views.list_products),
    # path('buscarpeliculasporgenero/', views.buscar_peliculasporgenero),
    # path('buscarpeliculasporfecha/', views.buscar_peliculasporfecha),
    path('recommendedProductsUser', views.recommendedProductsUser),

    ]
