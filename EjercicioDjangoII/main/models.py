#encoding:utf-8
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.core.validators import MinValueValidator,MaxValueValidator,URLValidator

class UserInformation(models.Model):
    name = models.TextField(verbose_name='Name')
    
    def __str__(self):
        return self.name


class Size(models.Model):
    size = models.TextField(verbose_name='Size')
    product_type = models.TextField(verbose_name='Product Type')
    def __str__(self):
        return str(self.size)
        
class Product(models.Model):
    name = models.TextField(verbose_name='Name')
    img = models.TextField(verbose_name='Image', default="https://www.syncron.com/wp-content/uploads/2017/03/img-placeholder.png")
    color = models.TextField(verbose_name='Color')
    brand = models.TextField(verbose_name='Brand') 
    type = models.TextField(verbose_name='Type') 
    current_price = models.TextField(verbose_name='CurrentPrice')
    old_price = models.TextField(verbose_name='OldPrice')
    avg_rating = models.FloatField(verbose_name='AvgRating', validators=[MinValueValidator(1), MaxValueValidator(5)], default=0.0)
    url = models.TextField(verbose_name='Url', default="Undefined")

    sizes = models.ManyToManyField(Size)
    # tituloOriginal = models.TextField(verbose_name='Título Original')
    # fechaEstreno = models.DateField(verbose_name='Fecha de Estreno')
    # pais = models.ForeignKey(Pais,on_delete=models.SET_NULL, null=True)
    # director = models.ForeignKey(Director,on_delete=models.SET_NULL, null=True)
    # sizes = ArrayField(models.TextField(), null=True)

    def __str__(self):
        return self.name
    
class Rating(models.Model):

    user = models.ForeignKey(UserInformation, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rateDate = models.DateField(null=True, blank=True)
    rating = models.FloatField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    def __str__(self):
        return str(str(self.user.id) + ", "+ str(self.product.id) + ", "+ str(self.rating))
