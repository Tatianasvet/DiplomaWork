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
    path('about/', about_page, name='about'),
    path('cart/', cart_page, name='cart'),
    path('contact/', contact_page, name='contact'),
    path('reviews/', reviews_page, name='reviews'),
    path('signup/', signup_page, name='signup'),
    path('login/', login_page, name='login'),
    path('logout', do_logout, name='logout'),
    path('products/', products_page, name='products'),
    path('salesmans/', salesmans_page, name='salesmans'),
    path('faq/', faq_page, name='faq'),
    path('conditions/', conditions_page, name='conditions'),
    path('payment/', payment_page, name='payment'),
]
