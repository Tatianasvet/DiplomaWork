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

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', start_page, name='home'),
    path('search/', search, name='search'),
    path('about/', about_page, name='about'),
    path('cart/', cart_page, name='cart'),
    path('contact/', contact_page, name='contact'),
    path('reviews/', reviews_page, name='reviews'),
    path('signup/', signup_page, name='signup'),
    path('login/', login_page, name='login'),
    path('logout', do_logout, name='logout'),
    path('products/', products_page, name='products'),
    path('product_info/', product_info, name='product_info'),
    path('salesmans/', salesmans_page, name='salesmans'),
    path('salesman_info/', salesman_info_page, name='salesman_info'),
    path('account/', account_page, name='account'),
    path('product_add_form/', product_add_form, name='product_add_form'),
    path('change_personal_info/', change_personal_info, name='change_personal_info'),
    path('delite_consent/', delite_consent_page, name='delite_consent'),
    path('faq/', faq_page, name='faq'),
    path('conditions/', conditions_page, name='conditions'),
    path('payment/', payment_page, name='payment'),
]
