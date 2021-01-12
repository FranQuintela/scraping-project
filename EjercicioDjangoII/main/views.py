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
    # num_directores = 0
    # num_paises = 0
    # num_generos = 0
    num_products = 0
    
    #borramos todas las tablas de la BD
    # Director.objects.all().delete()
    # Pais.objects.all().delete()
    # Genero.objects.all().delete()
    Product.objects.all().delete()
    
    #extraemos los datos de la web con BS
    f = urllib.request.urlopen("https://www.zalando.es/hombre-rebajas/?sale=true")
    s = BeautifulSoup(f, "lxml")
    
    PRODUCT_A_CLASS = "g88eG_ oHRBzn LyRfpJ _LM JT3_zV g88eG_"
    lista_a_products = s.find_all("a", class_= PRODUCT_A_CLASS)
    # lista_link_peliculas = s.find("ul", class_="elements").find_all("li")
    # extraemos los enlaces a los productos
    for a_product in lista_a_products:
        print("---------------------------------")
        link_product = "https://www.zalando.es" + a_product['href']
        # products urls starst with /, with this i get rid of non products links
        if a_product['href'].startswith('/'): 
            print("link_product: "+ link_product)
            # entramos a la pagina individual del producto
            f = urllib.request.urlopen(link_product)
            s = BeautifulSoup(f, "lxml")
            # cogemos los datos
            PRODUCT_DIV_DATA_CLASS = "qMZa55 VHXqc_ rceRmQ _4NtqZU mIlIve"
            product_data = s.find("div", class_=PRODUCT_DIV_DATA_CLASS)

            PRODUCT_H1_NAME_CLASS = "OEhtt9 ka2E9k uMhVZi z-oVg8 pVrzNP w5w9i_ _1PY7tW _9YcI4f"
            product_name = product_data.find("h1",class_=PRODUCT_H1_NAME_CLASS).string
            print(product_name)

            PRODUCT_IMG_IMG_CLASS = "_6uf91T z-oVg8 u-6V88 ka2E9k uMhVZi FxZV-M _2Pvyxl JT3_zV EKabf7 mo6ZnF _1RurXL mo6ZnF PZ5eVw"
            product_img = s.find("img", class_=PRODUCT_IMG_IMG_CLASS)["src"]
            print(product_img)

            PRODUCT_BUTTON_RATING_CLASS = "kMvGAR _6-WsK3 Md_Vex Nk_Omi _MmCDa to_CKO NN8L-8 K82if3"
            product_button_rating = product_data.find("button",class_=PRODUCT_BUTTON_RATING_CLASS)
            if product_button_rating !=None:
                product_rating = product_button_rating.find("div",class_="_0xLoFW FCIprz").find("div",class_="_0xLoFW")["aria-label"]
                print(product_rating)
                # .split("/")[0]

            PRODUCT_DIV_RATINGS_CLASS = "DvypSJ aC4gN7 _1o06TD Rft9Ae lTABpz"
            product_ratings = s.find_all("div",class_=PRODUCT_DIV_RATINGS_CLASS)
            
            if product_ratings == None:
                print("no ratings founds")
            else:
                print("ratings founds")
                print(product_ratings)


            for product_rating in product_ratings:
                print(product_rating)

                PRODUCT_H5_RATINGS_CLIENT_CLASS = "ZcZXP0 ka2E9k uMhVZi z-oVg8 pVrzNP"
                product_rating_client = product_rating.find("div",class_=PRODUCT_H5_RATINGS_CLIENT_CLASS)
                print(product_rating_client)

            
            #almacenamos en la BD
            p = Product.objects.create(name = product_name, img = product_img)
            num_products = num_products + 1
    return (num_products)
        
    # for link_pelicula in lista_a_products:
    #     f = urllib.request.urlopen("https://www.elseptimoarte.net/"+link_pelicula.a['href'])
    #     s = BeautifulSoup(f, "lxml")
    #     aux = s.find("main", class_="informativo").find_all("section",class_="highlight")
    #     datos = aux[0].div.dl
    #     titulo_original = datos.find("dt",string="Título original").find_next_sibling("dd").string.strip()
    #     #si no tiene título se pone el título original
    #     if (datos.find("dt",string="Título")):
    #         titulo = datos.find("dt",string="Título").find_next_sibling("dd").string.strip()
    #     else:
    #         titulo = titulo_original      
    #     paises = "".join(datos.find("dt",string="País").find_next_sibling("dd").stripped_strings)
    #     pais = paises.split(sep=",")[0]  #sólo se pide el primer país
    #     fecha = datetime.strptime(datos.find("dt",string="Estreno en España").find_next_sibling("dd").string.strip(), '%d/%m/%Y')
        
    #     generos_director = s.find("div",id="datos_pelicula")
    #     generos = "".join(generos_director.find("p",class_="categorias").stripped_strings)
    #     generos = generos.split(sep=",")
    #     directores = "".join(generos_director.find("p",class_="director").stripped_strings)
    #     director = directores.split(sep=",")[0]  #sólo se pide el primer director 
        
    #     #almacenamos en la BD
    #     director_obj, creado = Director.objects.get_or_create(nombre=director)
    #     if creado:
    #         num_directores = num_directores + 1
    #     pais_obj, creado = Pais.objects.get_or_create(nombre=pais)
    #     if creado:
    #         num_paises = num_paises + 1
    #     lista_generos_obj = []
    #     for genero in generos:
    #         genero_obj, creado = Genero.objects.get_or_create(nombre=genero)
    #         lista_generos_obj.append(genero_obj)
    #         if creado:
    #             num_generos = num_generos + 1
    #     p = Pelicula.objects.create(titulo = titulo, tituloOriginal = titulo_original,
    #                             fechaEstreno = fecha,
    #                             pais = pais_obj,                               
    #                             director = director_obj)
    #     #añadimos la lista de géneros
    #     for g in lista_generos_obj:
    #         p.generos.add(g)
    #     num_peliculas = num_peliculas + 1

    # return ((num_peliculas, num_directores, num_generos, num_paises))
        
#carga los datos desde la web en la BD
def carga(request):
 
    if request.method=='POST':
        if 'Aceptar' in request.POST:  
            num_products = populateDB()
            mensaje="Se han almacenado: " + str(num_products) +" productos " 
            return render(request, 'cargaBD.html', {'mensaje':mensaje})    
            # num_peliculas, num_directores, num_generos, num_paises = populateDB()
            # mensaje="Se han almacenado: " + str(num_peliculas) +" peliculas, " + str(num_directores) +" directores, " + str(num_generos) +" generos, " + str(num_paises) +" paises"
            # return render(request, 'cargaBD.html', {'mensaje':mensaje})
        else:
            return redirect("/")
           
    return render(request, 'confirmacion.html')

#muestra el número de películas que hay en la BD
def inicio(request):
    # num_peliculas=Pelicula.objects.all().count()
    num_products=Product.objects.all().count()
    return render(request,'inicio.html', {'num_products':num_products})

#muestra un listado con los datos de las películas (título, título original, país, director, géneros y fecha de estreno)
def list_products(request):
    products=Product.objects.all()
    return render(request,'products.html', {'products':products})

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
