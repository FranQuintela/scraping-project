# -*- encoding: utf-8 -*-
from django import forms
from main.models import Product, Size

class TypeForm(forms.Form):
    # id = forms.CharField(label='User ID')
    # lista=[(g.id,g.nombre) for g in Genero.objects.all()]
    # list=[(s.product_type,s.product_type) for s in Size.objects.order_by('product_type').values_list('product_type', flat=True) ]
    list=[(type,type) for type in Size.objects.order_by('product_type').values_list('product_type', flat=True).distinct() ]
    type = forms.ChoiceField(label="Select product_type", choices=list)
    
class PriceForm(forms.Form):
    price_interval = forms.CharField(label='Price Interval')

class UserForm(forms.Form):
    id = forms.CharField(label='User ID')