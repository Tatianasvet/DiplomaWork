from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Salesman, Product
from django import forms


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Обязательное поле. Введите действующий email.')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class SalesmanSignUpForm(forms.Form):
    phone = forms.CharField(max_length=15, required=True)
    photo = forms.ImageField(required=True)
    description = forms.TextInput()

    class Meta:
        model = Salesman
        fields = ('phone', 'photo', 'description')


class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Имя пользователя')
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)


class AddProductForm(forms.Form):
    name = forms.CharField(max_length=200, required=True)
    description = forms.TextInput()
    categories = forms.SelectMultiple()
    price = forms.IntegerField(min_value=1, required=True)
    main_photo = forms.ImageField(required=True)

    class Meta:
        model = Product
        fields = ('name', 'description', 'categories', 'price', 'main_photo')


class ChangeSalesmanInfoForm(forms.Form):
    first_name = forms.CharField(max_length=200, required=False)
    photo = forms.ImageField(required=False)
    description = forms.TextInput()
    phone = forms.CharField(max_length=15, required=False)
    email = forms.EmailField(max_length=254, required=False)


