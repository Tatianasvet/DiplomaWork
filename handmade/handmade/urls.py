"""
URL configuration for handmade project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from shop.views import *
from registration.views import Signup, Login, Change
from info.views import Info, Contact
from review.views import Review
from cart.views import Cart, Select, Like
from salesman.views import Profile
from shop.views import Home, Search

urlpatterns = [
    # admin
    path('admin/', admin.site.urls),
    # info
    path('about/', Info().about_page, name='about'),
    path('faq/', Info().faq_page, name='faq'),
    path('conditions/', Info().conditions_page, name='conditions'),
    path('payment/', Info().payment_page, name='payment'),
    path('contact/', Contact().contact_page, name='contact'),
    # registration
    path('signup/', Signup().signup_page, name='signup'),
    path('login/', Login().log_in_page, name='login'),
    path('logout', Login().log_out, name='logout'),
    path('change_personal_info/', Change().change_salesman_info, name='change_personal_info'),
    # review
    path('reviews/', Review().reviews_page, name='reviews'),
    # cart
    path('cart/', Cart().cart_page, name='cart'),
    path('add_to_cart/', Select().add_to_cart, name='add_to_cart'),
    path('del_from_cart/', Select().del_from_cart, name='del_from_cart'),
    path('like/', Like().like, name='like'),
    path('dislike', Like().dislike, name='dislike'),
    # salesman
    path('account/', Profile().account_page, name='account'),
    # shop
    path('', Home().start_page, name='home'),
    path('search/', Search().search, name='search'),


    path('products/', products_page, name='products'),
    path('product_info/', product_info, name='product_info'),
    path('salesmans/', salesmans_page, name='salesmans'),
    path('salesman_info/', salesman_info_page, name='salesman_info'),
    path('product_add_form/', product_add_form, name='product_add_form'),
    path('delite_consent/', delite_consent_page, name='delite_consent'),
]
