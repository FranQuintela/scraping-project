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
from main.forms import UserForm, FilmForm

# For Selenium to work, it must access the browser driver.
from selenium import webdriver
from selenium.webdriver.common.by import By

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
    # Director.objects.all().delete()
    # Pais.objects.all().delete()
    UserInformation.objects.all().delete()
    Product.objects.all().delete()
    Rating.objects.all().delete()

    print("user_id:" + str(num_users))
    u = UserInformation.objects.create(id = num_users, name="Test Person")
    dict_u["Test Person"]=u
    num_users = num_users +1 

    f = urllib.request.urlopen("https://www.zalando.es/hombre-rebajas/?sale=true")
    s = BeautifulSoup(f, "lxml")

    PRODUCT_A_CLASS = "g88eG_ oHRBzn LyRfpJ _LM JT3_zV g88eG_"
    lista_a_products = s.find_all("a", class_= PRODUCT_A_CLASS)
    
    # lista_link_peliculas = s.find("ul", class_="elements").find_all("li")
    # extraemos los enlaces a los productos
    for a_product in lista_a_products:
        print("---------------------------------")
        link_product = "https://www.zalando.es" + a_product['href']
        
        print("link_product: "+ link_product)
        # products urls starst with /, with this i get rid of non products links
        if a_product['href'].startswith('/'): 
            # entramos a la pagina individual del producto
            driver.get(link_product)
            # print(driver.page_source)
            
            SHOW_SIZE_BUTTON = ".lRlpGv > .\\_7Cm1F9"
            hasSizes = len((driver.find_elements_by_css_selector(SHOW_SIZE_BUTTON))) > 0
            if hasSizes:
                try:
                    driver.find_element(By.CSS_SELECTOR, SHOW_SIZE_BUTTON).click()
                    page_source = driver.page_source
                except:
                    pass
            else:
                print("no sizes found")

            SHOW_RATINGS_BUTTON = ".-NV4KN:nth-child(2) .z-oVg8"
            hasRatings = len((driver.find_elements_by_css_selector(SHOW_RATINGS_BUTTON))) > 0
            if hasRatings:
                SHOW_RATINGS_BUTTON = ".-NV4KN:nth-child(2) ._0xLoFW "
                driver.find_element(By.CSS_SELECTOR, SHOW_RATINGS_BUTTON).send_keys('\n')

                # more_buttons = driver.find_elements_by_class_name("moreLink")
                # for x in range(len(more_buttons)):
                #     if more_buttons[x].is_displayed():
                #         driver.execute_script("arguments[0].click();", more_buttons[x])
                #         time.sleep(1)
                page_source = driver.page_source
            else:
                print("no rating found")
            page_source = driver.page_source

            # print(page_source)
            #extraemos los datos de la web con BS
            s = BeautifulSoup(page_source, 'lxml')

            # cogemos los datos
            PRODUCT_DIV_DATA_CLASS = "qMZa55 VHXqc_ rceRmQ _4NtqZU mIlIve"
            product_data = s.find("div", class_=PRODUCT_DIV_DATA_CLASS)

            PRODUCT_H1_NAME_CLASS = "OEhtt9 ka2E9k uMhVZi z-oVg8 pVrzNP w5w9i_ _1PY7tW _9YcI4f"
            product_name = product_data.find("h1",class_=PRODUCT_H1_NAME_CLASS).string
            # print(product_name)

            PRODUCT_IMG_IMG_CLASS = "_6uf91T z-oVg8 u-6V88 ka2E9k uMhVZi FxZV-M _2Pvyxl JT3_zV EKabf7 mo6ZnF _1RurXL mo6ZnF PZ5eVw"
            product_img = s.find("img", class_=PRODUCT_IMG_IMG_CLASS)["src"]
            # print(product_img)

            PRODUCT_BUTTON_RATING_CLASS = "kMvGAR _6-WsK3 Md_Vex Nk_Omi _MmCDa to_CKO NN8L-8 K82if3"
            product_button_rating = product_data.find("button",class_=PRODUCT_BUTTON_RATING_CLASS)
            if product_button_rating !=None:
                product_rating_rating = product_button_rating.find("div",class_="_0xLoFW FCIprz").find("div",class_="_0xLoFW")["aria-label"].split("/")[0]
                # print("product_rating_rating: " + product_rating_rating)
                product_rating_rating = float(product_rating_rating)

            PRODUCT_DIV_RATINGS_CLASS = "DvypSJ aC4gN7 _1o06TD Rft9Ae lTABpz"
            product_ratings = s.find_all("div",class_=PRODUCT_DIV_RATINGS_CLASS)

           

            
            # Brand
            PRODUCT_SPAN_BRAND = "_7Cm1F9 ka2E9k uMhVZi dgII7d z-oVg8 pVrzNP ONArL- isiDul"
            product_brand = "Undefined"
            if(s.find("span",class_=PRODUCT_SPAN_BRAND) != None):
                product_brand = s.find("span",class_=PRODUCT_SPAN_BRAND).text
            
            # Color
            PRODUCT_SPAN_COLOR = "u-6V88 ka2E9k uMhVZi dgII7d z-oVg8 pVrzNP"
            product_color = s.find("span",class_=PRODUCT_SPAN_COLOR).text
                   
                
            #almacenamos product en la BD
            id_p = num_products  
            num_products = num_products + 1
            p = Product.objects.create(id = id_p,name = product_name, img = product_img, brand = product_brand, color= product_color)
            p.save()

            # Size
            if(hasSizes):
                PRODUCT_DIV_SIZE = "zaI4jo JT3_zV _0xLoFW _78xIQ- EJ4MLB"
                size_divs = s.find_all("div", class_= PRODUCT_DIV_SIZE)
                    
                for size_div in size_divs:
                    PRODUCT_DIV_SIZE_CLOTHING = "_7Cm1F9 ka2E9k uMhVZi dgII7d z-oVg8 pVrzNP"
                    PRODUCT_DIV_SIZE_SHOES = "_7Cm1F9 ka2E9k uMhVZi dgII7d z-oVg8 D--idb"

                    if(size_div.find("span",class_=PRODUCT_DIV_SIZE_CLOTHING) != None):
                        # Tallas de formato XS,S,M,L,XL
                        product_size = size_div.find("span",class_=PRODUCT_DIV_SIZE_CLOTHING).text
                        product_type = "Clothing"
                    elif(size_div.find("span",class_=PRODUCT_DIV_SIZE_SHOES) != None):
                        # Tallas de formato 36-40-41-47
                        product_size = size_div.find("span",class_=PRODUCT_DIV_SIZE_SHOES).text
                        product_type = "Shoes"
                    #almacenamos size en la BD
                    if product_size not in dict_s:
                        id_s = num_sizes
                        # print(print("user_id:" + str(num_users)))
                        s = Size.objects.create(id = id_s, size=product_size, product_type = product_type)
                        s.save()
                        # id_u = num_users
                        dict_s[product_size]=s
                        num_sizes = num_sizes + 1 
                    
                    # añadimos size a product
                    p.sizes.add(dict_s[product_size])

            dict_p[id_p] = p

            for product_rating in product_ratings:
                
                PRODUCT_H5_RATINGS_CLIENT_CLASS = "ZcZXP0 ka2E9k uMhVZi z-oVg8 pVrzNP"
                product_rating_client = product_rating.find("h5",class_=PRODUCT_H5_RATINGS_CLIENT_CLASS).string
                user_name = product_rating_client
                # print("user_name: " + product_rating_client)

                #almacenamos user en la BD
                if user_name not in dict_u:
                    id_u = num_users
                    # print(print("user_id:" + str(num_users)))
                    u = UserInformation.objects.create(id = id_u, name=product_rating_client)
                    # id_u = num_users
                    dict_u[user_name]=u
                    num_users = num_users + 1 

                #almacenamos rating en la BD
                id_r = num_ratings
                r = Rating.objects.create(id = id_r, user = dict_u[user_name], product = dict_p[id_p], rating = product_rating_rating)
                dict_r[user_name] = r  
                num_ratings = num_ratings + 1

            # user=u[int(rip[0].strip())], film=m[int(rip[1].strip())], rating=int(rip[2].strip()),

            id_r = num_ratings
            r = Rating.objects.create(id = id_r, user = dict_u["Test Person"], product = dict_p[id_p], rating = product_rating_rating)
            dict_r["Test Person"] = r  
            num_ratings = num_ratings + 1

    return (num_products,num_users,num_ratings)
        
   
        
#carga los datos desde la web en la BD
def carga(request):
 
    if request.method=='POST':
        if 'Aceptar' in request.POST:  
            num_products, num_users, num_ratings = populateDB()
            mensaje="Se han almacenado: " + str(num_products) +" products " + str(num_users) +" users "  + str(num_ratings) +" ratings " 
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
    users=UserInformation.objects.all()
    ratings=Rating.objects.all()
    return render(request,'products.html', {'products':products,'users':users,'ratings':ratings})

#muestra la lista de películas agrupadas por paises
def list_products_top_rated(request):
    products=Product.objects.all().order_by('rating')
    return render(request,'productstoprated.html', {'products':products})

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

# SISTEMAS DE RECOMENDACION
# Funcion que carga en el diccionario Prefs todas las puntuaciones de usuarios a peliculas. Tambien carga el diccionario inverso y la matriz de similitud entre items
# Serializa los resultados en dataRS.dat
def loadDict():
    print("Loading dict...")
    Prefs={}   # matriz de usuarios y puntuaciones a cada a items
    shelf = shelve.open("dataRS.dat")
    ratings = Rating.objects.all()
    for ra in ratings:
        user = int(ra.user.id)
        product = int(ra.product.id)
        rating = float(ra.rating)
        Prefs.setdefault(user, {})
        Prefs[user][product] = rating
    shelf['Prefs']=Prefs
    shelf['ItemsPrefs']=transformPrefs(Prefs)
    shelf['SimItems']=calculateSimilarItems(Prefs, n=10)
    shelf.close()
    

def loadRS(request):
    loadDict()
    return render(request,'loadRS.html')

# APARTADO A
def recommendedProductsUser(request):
    if request.method=='GET':
        form = UserForm(request.GET, request.FILES)
        if form.is_valid():
            idUser = form.cleaned_data['id']
            print("idUser: "+ idUser)
            user = get_object_or_404(UserInformation, pk=idUser)
            shelf = shelve.open("dataRS.dat")
            Prefs = shelf['Prefs']
            shelf.close()
            rankings = getRecommendations(Prefs,int(idUser))
            print("rankings-------------- ")
            print( rankings)

            recommended = rankings[:2]
            products = []
            scores = []
            for re in recommended:
                products.append(Product.objects.get(pk=re[1]))
                scores.append(re[0])
                print("re-------------- ")
                print( re)
            print("products-------------- ")
            print( products)
            print("scores-------------- ")
            print( scores)
            items= zip(products,scores)
            
            return render(request,'recommendationItems.html', {'user': user, 'items': items})
    form = UserForm()
    return render(request,'search_user.html', {'form': form})