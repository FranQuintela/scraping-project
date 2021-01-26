from django.contrib import admin
# from main.models import Genero, Director, Pais, Pelicula
from main.models import Product

#registramos en el administrador de django los modelos 
admin.site.register(Product)
# admin.site.register(Director)
# admin.site.register(Pais)
# admin.site.register(Pelicula)