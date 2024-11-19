from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from shop.models import CustomUser, Salesman
from django import forms


class SignUpForm(UserCreationForm):

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'password1', 'password2')


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model: CustomUser
        fields = ('username', 'email', 'first_name', 'password1', 'password2')


class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Имя пользователя')
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)


class SalesmanSignUpForm(forms.Form):

    class Meta:
        model = Salesman
        fields = ('phone', 'photo', 'description')


class ChangeSalesmanInfoForm(forms.Form):
    first_name = forms.CharField(max_length=200, required=False)
    photo = forms.ImageField(required=False)
    description = forms.TextInput()
    phone = forms.CharField(max_length=15, required=False)
    email = forms.EmailField(max_length=254, required=False)
