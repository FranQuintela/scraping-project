#encoding:utf-8
# from main.models import Genero, Director, Pais, Pelicula
# from main.forms import BusquedaPorFechaForm, BusquedaPorGeneroForm
import shelve

from main.models import Product, UserInformation, Rating, Size
from django.shortcuts import render, redirect, get_object_or_404

from bs4 import BeautifulSoup
import urllib.request
import lxml
from datetime import datetime
from main.recommendations import  transformPrefs, calculateSimilarItems, getRecommendations, getRecommendedItems, topMatches
from main.forms import TypeForm, PriceForm, UserForm

# For Selenium to work, it must access the browser driver.
from selenium import webdriver
from selenium.webdriver.common.by import By
# Woosh
from whoosh.index import create_in,open_dir
from whoosh.fields import Schema, TEXT, DATETIME, KEYWORD, NUMERIC
from whoosh.qparser import QueryParser, MultifieldParser, OrGroup
import re, os, shutil
import random

options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
options.add_argument('--headless')

userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36";
options.add_argument("user-agent=%s"+ userAgent)

driver = webdriver.Chrome("C:/Users/xisco/Documents/scraping-project/EjercicioDjangoII/chromedriver.exe", chrome_options=options)

import time



#función auxiliar que hace scraping en la web y carga los datos en la base datos
def populateDB():
    """Hacemos scraping en la web con BueautifulSoup y Selenium y creamos objetos en la BD con los datos obtenidos"""


    #variables para contar el número de registros que vamos a almacenar
    # num_directores = 0
    num_users = 1
    num_products = 0
    num_ratings = 0
    num_sizes = 0

    dict_p={}
    dict_u={}
    dict_r={}
    dict_s={}
    
    #borramos todas las tablas de la BD
    UserInformation.objects.all().delete()
    Product.objects.all().delete()
    Rating.objects.all().delete()
    Size.objects.all().delete()
    
    # Creamos las tallas porque las necesitaremos para reconocer que tipo de producto es más adelante
    sizes_clothing = ["XS", "S", "M", "L", "XL","XXL", "2XL", "3XL"]
    # range(30,50,0.5)
    sizes_shoes = [str(i/2) for i in range(60, 100)]

    # Creamos un usuario de prueba que dejará valoraciones en los productos para asegurarnos de que tenemos coincidencias
    # en el sistema de recomendación
    u = UserInformation.objects.create(id = num_users, name="Test Person")
    dict_u["Test Person"]=u
    num_users = num_users +1 

    
    # ----------------------CARGAMOS LA PAGINA PRINCIPAL------------------
    for i in range(1,5):

        f = urllib.request.urlopen("https://www.zalando.es/hombre-rebajas/?sale=true&p="+str(i))
        # &p=2
        web_code = BeautifulSoup(f, "lxml")

        PRODUCT_A_CLASS = "g88eG_ oHRBzn LyRfpJ _LM JT3_zV g88eG_"
        lista_a_products = web_code.find_all("a", class_= PRODUCT_A_CLASS)
        
        
        # ----------------------CARGAMOS LAS PAGINAS DE CADA PRODUCTO------------------
        for a_product in lista_a_products:
            print("---------------------------------")
            link_product = "https://www.zalando.es" + a_product['href']
            print("link_product: "+ link_product)

            # products urls starst with /, with this i get rid of non products links
            if a_product['href'].startswith('/'): 
            
            # CARGAMOS LOS DATOS OCULTOS UTILIZANDO SELENIUM PARA SIMULAR LOS CLICKS EN LOS DESPLEGABLES
                driver.get(link_product)   

                # ----------------------CARGAMOS SIZES------------------
                SHOW_SIZE_BUTTON = ".lRlpGv > .\\_7Cm1F9"
                hasSizes = len((driver.find_elements_by_css_selector(SHOW_SIZE_BUTTON))) > 0
                if hasSizes:
                    try:
                        driver.find_element(By.CSS_SELECTOR, SHOW_SIZE_BUTTON).click()
                        page_source = driver.page_source
                    except:
                        pass
                
                # ----------------------CARGAMOS RATINGS------------------
                SHOW_RATINGS_BUTTON = ".-NV4KN:nth-child(2) .z-oVg8"
                hasRatings = len((driver.find_elements_by_css_selector(SHOW_RATINGS_BUTTON))) > 0
                if hasRatings:
                    SHOW_RATINGS_BUTTON = ".-NV4KN:nth-child(2) ._0xLoFW "
                    driver.find_element(By.CSS_SELECTOR, SHOW_RATINGS_BUTTON).send_keys('\n')

                # ----------------------CARGAMOS MAS RATINGS------------------
                    
                    hasMoreRatings = True
                    while hasMoreRatings is True:
                        try:
                            driver.find_element(By.CSS_SELECTOR, "._8P5KBX > .K82if3").click()
                        except:
                            hasMoreRatings = False
                    
                    
                    # for x in range(len(more_buttons)):
                    #     if more_buttons[x].is_displayed():
                    #         driver.execute_script("arguments[0].click();", more_buttons[x])
                    #         time.sleep(1)
                    page_source = driver.page_source
                
                page_source = driver.page_source

                # ----------------------EXTRAEMOS DATOS CON BEAUTIFUL SOUP------------------
                web_code = BeautifulSoup(page_source, 'lxml')

                # ----------------------EXTRAEMOS SECCION CON DATOS PRINCIPALES ------------------
                PRODUCT_DIV_DATA_CLASS = "qMZa55 VHXqc_ rceRmQ _4NtqZU mIlIve"
                product_data = web_code.find("div", class_=PRODUCT_DIV_DATA_CLASS)
                # si no tiene este div no es un product, puede ser alguna promoción o una sección de outfits, saltamos esta iteración
                if product_data == None:
                    continue 

                # ----------------------EXTRAEMOS NAME----------------------
                PRODUCT_H1_NAME_CLASS = "OEhtt9 ka2E9k uMhVZi z-oVg8 pVrzNP w5w9i_ _1PY7tW _9YcI4f"
                product_name_h1 = product_data.find("h1",class_=PRODUCT_H1_NAME_CLASS)
                product_name = "Undefined"
                if(product_name_h1 != None):
                    product_name = product_name_h1.string

                # ----------------------EXTRAEMOS IMG----------------------

                PRODUCT_IMG_IMG_CLASS = "_6uf91T z-oVg8 u-6V88 ka2E9k uMhVZi FxZV-M _2Pvyxl JT3_zV EKabf7 mo6ZnF _1RurXL mo6ZnF PZ5eVw"
                product_img = web_code.find("img", class_=PRODUCT_IMG_IMG_CLASS)["src"]

                # ----------------------EXTRAEMOS AVG_RATING----------------------
                # vamos a tener que iterar por varios resultados para ver cual es el de rating porque no hay un id o clase único del rating
                PRODUCT_BUTTON_RATING_CLASS = "kMvGAR _6-WsK3 Md_Vex Nk_Omi _MmCDa to_CKO NN8L-8 K82if3"
                posible_product_buttons_rating = product_data.find_all("button",class_=PRODUCT_BUTTON_RATING_CLASS)
                for posible_product_button_rating in posible_product_buttons_rating:
                    product_buttons_rating = posible_product_button_rating.find("div",class_="_0xLoFW FCIprz").find("div",class_="_0xLoFW")
                    
                    if product_buttons_rating !=None:
                        product_rating_rating = product_buttons_rating["aria-label"].split("/")[0]
                        product_rating_rating = float(product_rating_rating) 
                
                # ----------------------EXTRAEMOS BRAND----------------------
                PRODUCT_SPAN_BRAND = "_7Cm1F9 ka2E9k uMhVZi dgII7d z-oVg8 pVrzNP ONArL- isiDul"
                product_brand = "Undefined"
                if(web_code.find("span",class_=PRODUCT_SPAN_BRAND) != None):
                    product_brand = web_code.find("span",class_=PRODUCT_SPAN_BRAND).text
                
                # ----------------------EXTRAEMOS COLOR----------------------
                PRODUCT_SPAN_COLOR = "u-6V88 ka2E9k uMhVZi dgII7d z-oVg8 pVrzNP"
                product_color = web_code.find("span",class_=PRODUCT_SPAN_COLOR).text
                    
                # ----------------------EXTRAEMOS CURRENT_PRICE----------------------
                PRODUCT_SPAN_CURRENT_PRICE = "uqkIZw ka2E9k uMhVZi dgII7d z-oVg8 _88STHx cMfkVL"
                product_current_price = web_code.find("span",class_=PRODUCT_SPAN_CURRENT_PRICE).text
                # Ajustamos la información a lo que necesitamos
                product_current_price = re.sub(',', '.', re.sub('€', '', re.sub('desde ', '', product_current_price)))
                product_current_price = float(product_current_price) 

                # ----------------------EXTRAEMOS OLD_PRICE----------------------
                PRODUCT_SPAN_OLD_PRICE = "uqkIZw ka2E9k uMhVZi FxZV-M z-oVg8 weHhRC ZiDB59"
                product_old_price = web_code.find("span",class_=PRODUCT_SPAN_OLD_PRICE).text
                # Ajustamos la información a lo que necesitamos
                product_old_price = re.sub(',', '.', re.sub('€', '', re.sub('desde ', '', product_old_price)))
                product_old_price = float(product_old_price) 

                # ----------------------ALMACENAMOS PRODUCT EN LA DB----------------------
                id_p = num_products  
                num_products = num_products + 1
                p = Product.objects.create(id = id_p,name = product_name, img = product_img, brand = product_brand, color= product_color,
                current_price = product_current_price, old_price = product_old_price, avg_rating=product_rating_rating, url=link_product )
                p.save()
                # 
                # 

                # ----------------------EXTRAEMOS SIZES ----------------------
                if(hasSizes):
                    # la unica forma de extraer el tipo del producto es a través de las tallas asi que lo extraeremos aquí
                    product_type = "Undefined"

                    PRODUCT_DIV_SIZE = "zaI4jo JT3_zV _0xLoFW _78xIQ- EJ4MLB"
                    size_divs = web_code.find_all("div", class_= PRODUCT_DIV_SIZE)

                    for size_div in size_divs:
                        PRODUCT_DIV_SIZE_1 = "_7Cm1F9 ka2E9k uMhVZi dgII7d z-oVg8 pVrzNP"
                        PRODUCT_DIV_SIZE_2 = "_7Cm1F9 ka2E9k uMhVZi dgII7d z-oVg8 D--idb"

                        if(size_div.find("span",class_=PRODUCT_DIV_SIZE_1) != None):
                            product_size = size_div.find("span",class_=PRODUCT_DIV_SIZE_1).text
                            
                        elif(size_div.find("span",class_=PRODUCT_DIV_SIZE_2) != None):
                            product_size = size_div.find("span",class_=PRODUCT_DIV_SIZE_2).text

                # ----------------------ALMACENAMOS SIZE EN LA DB----------------------
                        if product_size not in dict_s:
                            id_s = num_sizes

                            if product_size in sizes_clothing:
                                product_type = "Clothing"

                            else:
                                try:
                                    # aquí convertimos mapeamos integers a double: talla 40 -> 40.0
                                    product_size = str(float(product_size))
                                except:
                                    pass
                                if product_size in sizes_shoes:
                                    product_type = "Shoes"
                                else:
                                    product_type = "Undetermined"
                                
                            s = Size.objects.create(id = id_s, size=product_size, product_type = product_type)
                            s.save()
                            dict_s[product_size]=s
                            num_sizes = num_sizes + 1 
                        
                # ----------------------ASOCIAMOS LAS TALLAS DEL PRODUCTO----------------------                    
                        p.sizes.add(dict_s[product_size])

                # ----------------------ACTUALIZAMOS EL TIPO DEL PRODUCTO A TRAVÉS DE LA TALLA----------------------       
                    first_size = p.sizes.first()
                    if first_size != None:
                        product_type = first_size.product_type
                    p.type = product_type
                    p.save()


                dict_p[id_p] = p

                # ----------------------EXTRAEMOS LOS RATINGS (VALORACIONES A LOS PRODUCTOS)----------------------
                PRODUCT_DIV_RATINGS_CLASS = "DvypSJ aC4gN7 _1o06TD Rft9Ae lTABpz"
                product_ratings_divs = web_code.find_all("div",class_=PRODUCT_DIV_RATINGS_CLASS)

                for product_rating_div in product_ratings_divs:
                    
                    PRODUCT_H5_RATINGS_CLIENT_CLASS = "ZcZXP0 ka2E9k uMhVZi z-oVg8 pVrzNP"
                    product_rating_client = product_rating_div.find("h5",class_=PRODUCT_H5_RATINGS_CLIENT_CLASS).string
                    user_name = product_rating_client

                # ----------------------ALMACENAMOS USUARIO QUE DEJÓ LA VALORACIÓN EN LA BD----------------------
                    if user_name not in dict_u:
                        id_u = num_users
                        u = UserInformation.objects.create(id = id_u, name=product_rating_client)
                        dict_u[user_name]=u
                        num_users = num_users + 1 

                # ----------------------ALMACENAMOS RATINGS EN LA BD----------------------
                    
                    PRODUCT_DIV_RATING_CLASS = "qMZa55 fg5xcc"
                    product_rating_div = product_rating_div.find("div",class_=PRODUCT_DIV_RATING_CLASS)

                    PRODUCT_DIV_RATING_CLASS = "_0xLoFW"
                    product_rating_div = product_rating_div.find("div",class_=PRODUCT_DIV_RATING_CLASS)

                    
                    product_rating_rating = product_rating_div["aria-label"].split("/")[0]
                    id_r = num_ratings
                    r = Rating.objects.create(id = id_r, user = dict_u[user_name], product = dict_p[id_p], rating = product_rating_rating)
                    dict_r[user_name] = r  
                    num_ratings = num_ratings + 1

                # ----------------------ALMACENAMOS RATING DEL USUARIO DE PRUEBA EN LA BD----------------------
                id_r = num_ratings
                r = Rating.objects.create(id = id_r, user = dict_u["Test Person"], product = dict_p[id_p], rating = random.uniform(0.0, 5.0))
                dict_r["Test Person"] = r  
                num_ratings = num_ratings + 1

    return (num_products,num_users,num_ratings)
        
def save_data():
    """ Almacenamos los datos recogidos en populateDB en un archivo que utilizaremos para las funcionalides de Woosh"""
    
    # ----------------------DEFINIMOS ESTRUCTURA CON LAS PROPIEDADES A GUARDAR----------------------
    schem = Schema(name=TEXT(stored=True), img=TEXT, color=TEXT(stored=True),  brand=TEXT(stored=True),  type=TEXT(stored=True),
    current_price=NUMERIC(stored=True))

    # sizes=KEYWORD(stored=True,commas=True)

    if os.path.exists("Index"):
        shutil.rmtree("Index")
    os.mkdir("Index")
    ix = create_in("Index", schema=schem)
    writer = ix.writer()

    # ----------------------GUARDAMOS EN EL DOCUMENTO CADA PRODUCTO DE LA BD----------------------
    i=0
    products=Product.objects.all()
    for product in products:
        writer.add_document(name=product.name, img=product.img, color=product.color, brand=product.brand, type=product.type, current_price = product.current_price)    
        i+=1
    writer.commit()
    print("Fin de indexado", "Se han indexado "+str(i)+ " productos")    
        

    # ----------------------MAPEO DE CONFIRMACION.HTML Y CARGADB.HTML----------------------
def carga(request):
    """Procesa confirmación.html y procesa la carga de datos si el usuario pulsa el botón de cargar datos"""
 
    if request.method=='POST':
        if 'Aceptar' in request.POST:  
            num_products, num_users, num_ratings = populateDB()
            save_data()
            mensaje="Se han almacenado: " + str(num_products) +" products " + str(num_users) +" users "  + str(num_ratings) +" ratings " 
            return render(request, 'cargaBD.html', {'mensaje':mensaje})    
            
        else:
            return redirect("/")
           
    return render(request, 'confirmacion.html')

    # ----------------------MAPEO DE INICIO.HTML----------------------
def inicio(request):
    """Procesa inicio.html"""
    num_products=Product.objects.all().count()
    return render(request,'inicio.html', {'num_products':num_products})

    # ----------------------MAPEO DE PRODUCTS.HTML----------------------
def list_products(request):
    """Procesa products.html y lista la información desde la BD"""
    products=Product.objects.all()
    users=UserInformation.objects.all()
    ratings=Rating.objects.all()
    return render(request,'products.html', {'products':products,'users':users,'ratings':ratings})

    # ----------------------MAPEO DE PRODUCTSTOPRATED.HTML----------------------
def list_products_top_rated(request):
    """Procesa productstoprated.html y lista los productos ordandos por rating """
    products=Product.objects.all().order_by('-avg_rating')
    return render(request,'productstoprated.html', {'products':products})


    # ----------------------MAPEO DE PRODUCTSBYTYPE.HTML----------------------
def search_products_by_type(request):
    """Procesa productstoprated.html, carga la información introducida en el formulario y 
    recoge los productos en función del product_type introducido haciendo uso de Woosh"""
    
    formulario = TypeForm()
    products = []

    if request.method=='POST':
        formulario = TypeForm(request.POST)
        if formulario.is_valid():
            type = formulario.cleaned_data['type']

            ix=open_dir("Index")      
            with ix.searcher() as searcher:
                
                query = QueryParser("type", ix.schema).parse(type)
                results = searcher.search(query, limit=20) 
                for r in results: 
                    product = Product.objects.all().filter(name=r['name']).first()
                    products.append(product)

    return render(request, 'productsbytype.html', {'formulario':formulario, 'products':products})

    # ----------------------MAPEO DE PRODUCTSBYPRICEINTERVAL.HTML----------------------    
def search_products_by_price_interval(request):
    """Procesa productsbypriceinterval.html, carga la información introducida en el formulario y 
    recoge los productos con price entre los prices introducidos haciendo uso de Woosh"""

    formulario = PriceForm()
    products = []
    message = ""

    if request.method=='POST':
        formulario = PriceForm(request.POST)
        if formulario.is_valid():
            price_interval = formulario.cleaned_data['price_interval']
            ix=open_dir("Index")      
            with ix.searcher() as searcher:
                
                try:
                    aux = price_interval.split()
                    price_interval = '['+ aux[0] + ' TO ' + aux[1] +']'
                    query = QueryParser("current_price", ix.schema).parse(price_interval)

                    results = searcher.search(query, limit=20) 
                    for r in results: 
                        product = Product.objects.all().filter(name=r['name']).first()
                        products.append(product)
                except:
                    message = "The price interval is not in the correct format, please try again"
                    pass

    return render(request, 'productsbypriceinterval.html', {'formulario':formulario, 'products':products, 'message': message})

    # ----------------------SISTEMAS DE RECOMENDACIÓN---------------------- 

    # ----------------------CARGA EL LOS DICCIONARIOS EN FUNCION DE LOS RATINGS----------------------    
def loadDict():
    """Funcion que carga en el diccionario Prefs todas las puntuaciones de usuarios a peliculas. 
    Tambien carga el diccionario inverso y la matriz de similitud entre items.
    Serializa los resultados en dataRS.dat"""

    print("------------------Loading dict...--------------------------")
    Prefs={}   # matriz de usuarios y puntuaciones a cada a items
    shelf = shelve.open("dataRS.dat")
    ratings = Rating.objects.all()
    for ra in ratings:
        user = int(ra.user.id)
        product = int(ra.product.id)
        print("Product url:" + ra.product.url + ", id= " + str(ra.product.id) )
        rating = float(ra.rating)
        Prefs.setdefault(user, {})
        Prefs[user][product] = rating
    shelf['Prefs']=Prefs
    shelf['ItemsPrefs']=transformPrefs(Prefs)
    shelf['SimItems']=calculateSimilarItems(Prefs, n=10)
    shelf.close()
    
    # ----------------------MAPEO DE LOADRS.HTML----------------------    
def loadRS(request):
    """Procesa loadRS.html y carga la información de los dictionarios del Sistema de Recomendación"""
    loadDict()
    return render(request,'loadRS.html')

    # ----------------------MAPEO DE RECOMMENDATIONITEMS.HTML Y SEARCH_USER.HTML----------------------    
def recommendedProductsUser(request):
    """Procesa recommendationItems.html y search_user.html y recoge los producos recomendados para el usuario introducido.
    \n Esto lo hace usando los ratings que tienen coincidencias con otros usuarios a través del Sistema de Recomendación"""

    print("------------------Loading recomendations...--------------------------")

    if request.method=='GET':
        form = UserForm(request.GET, request.FILES)
        if form.is_valid():
            idUser = form.cleaned_data['id']
            user = get_object_or_404(UserInformation, pk=idUser)
            shelf = shelve.open("dataRS.dat")
            Prefs = shelf['Prefs']
            shelf.close()
            rankings = getRecommendations(Prefs,int(idUser))[0]
            others = getRecommendations(Prefs,int(idUser))[1]
            message = "We have compared this user product's rating and compared it to other users with similar ratings and these are the recommendations that came out"
            if len(rankings) == 0:
                message = "Bad luck with this user, you can still try with: 1"
                for other in others:
                    message += ", " + str(other)
            recommended = rankings[:4]
            products = []
            scores = []
            for re in recommended:
                products.append(Product.objects.get(pk=re[1]))
                scores.append(re[0])
                
            items= zip(products,scores)
            
            return render(request,'recommendationItems.html', {'user': user, 'items': items, 'message': message})

    form = UserForm()
    return render(request,'search_user.html', {'form': form})