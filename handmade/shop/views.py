from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import SignUpForm, LoginForm
from .models import *


def start_page(request):
    context = {'user': request.user}
    return render(request, 'index.html', context)


def signup_page(request):
    context = {}
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
        else:
            context['error_message'] = form.error_messages
    return render(request, 'signup.html', context)


def login_page(request):
    form = LoginForm(data=request.POST or None)
    context = {}
    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                context['error_message'] = 'Неверный логин или пароль'
        else:
            context['error_message'] = form.error_messages
    return render(request, 'login.html', context)


def do_logout(request):
    logout(request)
    context = {'user': request.user}
    return render(request, 'index.html', context)


def cart_page(request):
    return render(request, 'cart.html')


def contact_page(request):
    return render(request, 'contact.html')


def reviews_page(request):
    return render(request, 'reviews.html')


def checkout_page(request):
    return render(request, 'checkout.html')


def products_page(request):
    products = Product.objects.all()
    photos = ProductPhoto.objects.all()
    context = {'products': products,
               'photos': photos}
    return render(request, 'products.html', context)


def salesmans_page(request):
    return render(request, 'dummy.html')


def about_page(request):
    return render(request, 'about.html')


def faq_page(request):
    return render(request, 'dummy.html')


def conditions_page(request):
    return render(request, 'dummy.html')


def payment_page(request):
    return render(request, 'dummy.html')
