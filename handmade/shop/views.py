from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import SignUpForm, LoginForm
from .models import *


def start_page(request):
    categories = Category.objects.all()
    context = {'user': request.user,
               'categories': categories,
               'parent_categories_id': _get_parent_categories_id(categories)}
    return render(request, 'index.html', context)


def _get_parent_categories_id(categories):
    parent_categories_id = []
    for check_category in categories:
        for category in categories:
            if check_category.id == category.parent_category_id:
                parent_categories_id.append(check_category.id)
                break
    return parent_categories_id


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
    category_id = request.GET.get('category_id')
    context = {}
    if category_id:
        context['category'] = category = Category.objects.get(id=category_id)
        context['way'] = _category_way(category_id)
        context['categories'] = categories = _sub_categories_list(category, [])
        context['parent_categories_id'] = _get_parent_categories_id(categories)
        context['products'] = _get_products_by_categories_list(categories)
    else:
        context['category'] = False
        context['products'] = Product.objects.all().order_by('-add_date')
        context['categories'] = categories = Category.objects.all()
        context['parent_categories_id'] = _get_parent_categories_id(categories)
    context['photos'] = ProductPhoto.objects.filter(number=1)
    return render(request, 'products.html', context)


def _sub_categories_list(parent_category, category_list):
    category_list.append(parent_category)
    for sub_category in Category.objects.all():
        if sub_category.parent_category_id == parent_category.id:
            category_list = _sub_categories_list(sub_category, category_list)
    return category_list


def _get_products_by_categories_list(categories_list):
    result = []
    for category in categories_list:
        products = Product.objects.filter(category=category)
        for product in products:
            result.append(product)
    return result


def _category_way(category_id):
    category = Category.objects.get(id=category_id)
    way = [category,]
    while category.parent_category_id:
        category = Category.objects.get(id=category.parent_category_id)
        way.append(category)
    way.reverse()
    return way


def _get_product_photos(product_list):
    result = []
    for product in product_list:
        result.append(ProductPhoto.objects.get(product=product, number=1))
    return result


def product_info(request):
    product_id = request.GET.get('product_id')
    product = Product.objects.get(id=product_id)
    photos = ProductPhoto.objects.filter(product=product).order_by('number')
    context = {'salesman': product.salesman,
               'product': product,
               'photos': photos}
    return render(request, 'product_info.html', context)


def salesmans_page(request):
    salesmans = Salesman.objects.all().order_by('name')
    context = {'salesmans': salesmans}
    return render(request, 'salesmans.html', context)


def salesman_info_page(request):
    salesman_id = request.GET.get('salesman_id')
    salesman = Salesman.objects.get(id=salesman_id)
    products = Product.objects.filter(salesman=salesman).order_by('-add_date')
    photos = []
    for product in products:
        photos.append(ProductPhoto.objects.get(product=product, number=1))
    context = {'salesman': salesman,
               'products': products,
               'photos': photos}
    return render(request, 'salesman_info.html', context)


def about_page(request):
    return render(request, 'about.html')


def faq_page(request):
    return render(request, 'dummy.html')


def conditions_page(request):
    return render(request, 'dummy.html')


def payment_page(request):
    return render(request, 'dummy.html')
