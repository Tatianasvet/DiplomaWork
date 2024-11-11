from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Salesman
from django import forms


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Обязательное поле. Введите действующий email.')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class SalesmanSignUpForm(forms.Form):
    phone = forms.CharField(max_length=15, required=True)
    photo = forms.ImageField(required=True)
    description = forms.Textarea()

    class Meta:
        model = Salesman
        fields = ('phone', 'photo', 'description')


class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Имя пользователя')
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)
