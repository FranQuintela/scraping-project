#encoding:utf-8
from django.db import models
from django.core.validators import MinValueValidator,MaxValueValidator,URLValidator

class UserInformation(models.Model):
    name = models.TextField(verbose_name='Name')
    
    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.TextField(verbose_name='Name')
    img = models.TextField(verbose_name='Image', default="https://www.syncron.com/wp-content/uploads/2017/03/img-placeholder.png")
    # tituloOriginal = models.TextField(verbose_name='Título Original')
    # fechaEstreno = models.DateField(verbose_name='Fecha de Estreno')
    # pais = models.ForeignKey(Pais,on_delete=models.SET_NULL, null=True)
    # director = models.ForeignKey(Director,on_delete=models.SET_NULL, null=True)
    # generos = models.ManyToManyField(Genero)

    def __str__(self):
        return self.name
    
class Rating(models.Model):

    user = models.ForeignKey(UserInformation, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rateDate = models.DateField(null=True, blank=True)
    rating = models.FloatField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    def __str__(self):
        return str(self.rating)