#encoding:utf-8
# from main.models import Genero, Director, Pais, Pelicula
# from main.forms import BusquedaPorFechaForm, BusquedaPorGeneroForm
from main.models import Product
from django.shortcuts import render, redirect
from bs4 import BeautifulSoup
import urllib.request
import lxml
from datetime import datetime

#función auxiliar que hace scraping en la web y carga los datos en la base datos
def populateDB():
    #variables para contar el número de registros que vamos a almacenar
    num_directores = 0
    num_paises = 0
    num_generos = 0
    num_peliculas = 0
    
    #borramos todas las tablas de la BD
    Director.objects.all().delete()
    Pais.objects.all().delete()
    Genero.objects.all().delete()
    Pelicula.objects.all().delete()
    
    #extraemos los datos de la web con BS
    f = urllib.request.urlopen("https://www.elseptimoarte.net/estrenos/")
    s = BeautifulSoup(f, "lxml")
    lista_link_peliculas = s.find("ul", class_="elements").find_all("li")
    for link_pelicula in lista_link_peliculas:
        f = urllib.request.urlopen("https://www.elseptimoarte.net/"+link_pelicula.a['href'])
        s = BeautifulSoup(f, "lxml")
        aux = s.find("main", class_="informativo").find_all("section",class_="highlight")
        datos = aux[0].div.dl
        titulo_original = datos.find("dt",string="Título original").find_next_sibling("dd").string.strip()
        #si no tiene título se pone el título original
        if (datos.find("dt",string="Título")):
            titulo = datos.find("dt",string="Título").find_next_sibling("dd").string.strip()
        else:
            titulo = titulo_original      
        paises = "".join(datos.find("dt",string="País").find_next_sibling("dd").stripped_strings)
        pais = paises.split(sep=",")[0]  #sólo se pide el primer país
        fecha = datetime.strptime(datos.find("dt",string="Estreno en España").find_next_sibling("dd").string.strip(), '%d/%m/%Y')
        
        generos_director = s.find("div",id="datos_pelicula")
        generos = "".join(generos_director.find("p",class_="categorias").stripped_strings)
        generos = generos.split(sep=",")
        directores = "".join(generos_director.find("p",class_="director").stripped_strings)
        director = directores.split(sep=",")[0]  #sólo se pide el primer director 
        
        #almacenamos en la BD
        director_obj, creado = Director.objects.get_or_create(nombre=director)
        if creado:
            num_directores = num_directores + 1
        pais_obj, creado = Pais.objects.get_or_create(nombre=pais)
        if creado:
            num_paises = num_paises + 1
        lista_generos_obj = []
        for genero in generos:
            genero_obj, creado = Genero.objects.get_or_create(nombre=genero)
            lista_generos_obj.append(genero_obj)
            if creado:
                num_generos = num_generos + 1
        p = Pelicula.objects.create(titulo = titulo, tituloOriginal = titulo_original,
                                fechaEstreno = fecha,
                                pais = pais_obj,                               
                                director = director_obj)
        #añadimos la lista de géneros
        for g in lista_generos_obj:
            p.generos.add(g)
        num_peliculas = num_peliculas + 1

    return ((num_peliculas, num_directores, num_generos, num_paises))
        
#carga los datos desde la web en la BD
def carga(request):
 
    if request.method=='POST':
        if 'Aceptar' in request.POST:      
            num_peliculas, num_directores, num_generos, num_paises = populateDB()
            mensaje="Se han almacenado: " + str(num_peliculas) +" peliculas, " + str(num_directores) +" directores, " + str(num_generos) +" generos, " + str(num_paises) +" paises"
            return render(request, 'cargaBD.html', {'mensaje':mensaje})
        else:
            return redirect("/")
           
    return render(request, 'confirmacion.html')

#muestra el número de películas que hay en la BD
def inicio(request):
    # num_peliculas=Pelicula.objects.all().count()
    num_peliculas=0
    return render(request,'inicio.html', {'num_peliculas':num_peliculas})

#muestra un listado con los datos de las películas (título, título original, país, director, géneros y fecha de estreno)
def lista_peliculas(request):
    peliculas=Pelicula.objects.all()
    return render(request,'peliculas.html', {'peliculas':peliculas})

#muestra la lista de películas agrupadas por paises
def lista_peliculasporpais(request):
    peliculas=Pelicula.objects.all().order_by('pais')
    return render(request,'peliculasporpais.html', {'peliculas':peliculas})

#muestra un formulario con un choicefield con la lista de géneros que hay en la BD. Cuando se seleccione
#un género muestra los datos de todas las películas de ese género
def buscar_peliculasporgenero(request):
    formulario = BusquedaPorGeneroForm()
    peliculas = None
    
    if request.method=='POST':
        formulario = BusquedaPorGeneroForm(request.POST)      
        if formulario.is_valid():
            genero=Genero.objects.get(id=formulario.cleaned_data['genero'])
            peliculas = genero.pelicula_set.all()
            
    return render(request, 'peliculasbusquedaporgenero.html', {'formulario':formulario, 'peliculas':peliculas})

#muestra un formulario con un datefield. Cuando se escriba una fecha muestra los datos de todas las
#las películas con una fecha de estreno posterior a ella
def buscar_peliculasporfecha(request):
    formulario = BusquedaPorFechaForm()
    peliculas = None
    
    if request.method=='POST':
        formulario = BusquedaPorFechaForm(request.POST)      
        if formulario.is_valid():
            peliculas = Pelicula.objects.filter(fechaEstreno__gte=formulario.cleaned_data['fecha'])
            
    return render(request, 'peliculasbusquedaporfecha.html', {'formulario':formulario, 'peliculas':peliculas})
