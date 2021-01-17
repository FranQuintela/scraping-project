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
    path('productsbytype/', views.search_products_by_type),
    path('productsbypriceinterval/', views.search_products_by_price_interval),
    path('recommendedProductsUser', views.recommendedProductsUser),

    ]
