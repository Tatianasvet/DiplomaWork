from django.shortcuts import render
from .models import *


def start_page(request):
    return render(request, 'index.html')


def login_page(request):
    return render(request, 'login.html')


def cart_page(request):
    return render(request, 'cart.html')


def contact_page(request):
    return render(request, 'contact.html')


def reviews_page(request):
    return render(request, 'reviews.html')


def checkout_page(request):
    return render(request, 'checkout.html')


def products_page(request):
    return render(request, 'products.html')


def salesmans_page(request):
    return render(request, 'salesmans.html')


def about_page(request):
    return render(request, 'about.html')
