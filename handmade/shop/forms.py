from .models import Product
from django import forms


class AddProductForm(forms.Form):

    class Meta:
        model = Product
        fields = ('name', 'description', 'categories', 'price', 'main_photo')
