from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.db.models import Q
from .forms import SignUpForm, SalesmanSignUpForm,  LoginForm, AddProductForm, ChangeSalesmanInfoForm
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


def search(request):
    if request.method == 'POST':
        search_mode = request.POST.get('mode')
        query = request.POST.get('search').lower()
        context = {}
        if search_mode == 'product':
            lookup = Q(name__icontains=query) | Q(description__icontains=query)
            query_categories = Category.objects.filter(lookup)
            lookup = lookup | Q(category__in=query_categories)
            products = Product.objects.filter(lookup)
            min_price = request.POST.get('min_price')
            max_price = request.POST.get('max_price')
            if min_price:
                products.filter(price__gte=min_price)
            if max_price:
                products.filter(price__lte=max_price)
            context['products'] = products.order_by('-add_date')
            context['category'] = False
            context['categories'] = categories = Category.objects.all()
            context['parent_categories_id'] = _get_parent_categories_id(categories)
            return render(request, 'products.html', context)
        elif search_mode == 'salesman':

            users = User.objects.filter(first_name__contains=query)
            print(users)
            lookup = Q(description__contains=query) | Q(user__in=users)
            salesmans = Salesman.objects.filter(lookup)
            print(salesmans)
            context['salesmans'] = salesmans
            return render(request, 'salesmans.html', context)


def signup_page(request):
    context = {}
    if request.method == 'POST':
        if request.GET.get('salesman') == 'true':
            user_form = SignUpForm(request.POST)
            salesman_form = SalesmanSignUpForm(request.POST, request.FILES)
            if user_form.is_valid():
                if salesman_form.is_valid():
                    user = user_form.save()
                    login(request, user)
                    Salesman.objects.create(user=user,
                                            phone=request.POST.get('phone'),
                                            photo=request.FILES['photo'],
                                            description=request.POST.get('description'))
                    return redirect('home')
                else:
                    context['error_message'] = salesman_form.errors
            else:
                context['error_message'] = user_form.errors
        else:
            form = SignUpForm(request.POST)
            if form.is_valid():
                user = form.save()
                login(request, user)
                return redirect('home')
            else:
                context['error_message'] = form.errors
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
                context['error_message'] = form.errors
        else:
            context['error_message'] = form.errors
    return render(request, 'login.html', context)


def do_logout(request):
    logout(request)
    return redirect('home')


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


def product_info(request):
    product_id = request.GET.get('product_id')
    product = Product.objects.get(id=product_id)
    context = {'salesman': product.salesman,
               'product': product}
    return render(request, 'product_info.html', context)


def salesmans_page(request):
    salesmans = Salesman.objects.all()
    context = {'salesmans': salesmans}
    return render(request, 'salesmans.html', context)


def salesman_info_page(request):
    salesman_id = request.GET.get('salesman_id')
    salesman = Salesman.objects.get(id=salesman_id)
    products = Product.objects.filter(salesman=salesman).order_by('-add_date')
    context = {'salesman': salesman,
               'products': products}
    return render(request, 'salesman_info.html', context)


def account_page(request):
    if request.user.first_name:
        salesman = Salesman.objects.get(user=request.user)
        products = Product.objects.filter(salesman=salesman).order_by('-add_date')
        context = {'salesman': salesman,
                   'products': products}
        return render(request, 'account.html', context)
    else:
        return redirect('cart')


def product_add_form(request):
    context = {'success': False}
    if request.method == 'POST':
        form = AddProductForm(request.POST, request.FILES)
        if form.is_valid():
            user = request.user
            salesman = Salesman.objects.get(user=user)
            category_id = request.POST.get('category_id')
            category = Category.objects.get(id=category_id)
            Product.objects.create(salesman=salesman,
                                   name=request.POST.get('name'),
                                   description=request.POST.get('description'),
                                   main_photo=request.FILES['main_photo'],
                                   category=category,
                                   price=request.POST.get('price'))
            context['success'] = True
        else:
            context['error_message'] = form.errors
    else:
        root_categories = Category.objects.filter(parent_category_id=None)
        categories = []
        for root in root_categories:
            categories += _sub_categories_list(root, [])
        context['categories'] = categories
    return render(request, 'product_add_form.html', context)


def change_personal_info(request):
    salesman = Salesman.objects.get(user=request.user)
    context = {'salesman': salesman}
    if request.method == 'POST':
        form = ChangeSalesmanInfoForm(request.POST)
        if form.is_valid():
            first_name = request.POST.get('first_name')
            if first_name:
                salesman.user.first_name = first_name
            if 'photo' not in request.POST.keys():
                salesman.photo = request.FILES['photo']
            description = request.POST.get('description')
            if description:
                salesman.description = description
            phone = request.POST.get('phone')
            if phone:
                salesman.phone = phone
            email = request.POST.get('email')
            if email:
                salesman.user.email = email
            salesman.user.save()
            salesman.save()
            return redirect('account')
        else:
            context['error_message'] = form.errors
    return render(request, 'change_personal_info.html', context)


def delite_consent_page(request):
    object_type = request.GET.get('object_type')
    target_id = request.GET.get('target_id')
    context = {'consent': False,
               'object_type': object_type,
               'target_id': request.GET.get('target_id')}
    if object_type == 'salesman':
        salesman = Salesman.objects.get(id=target_id)
        context['question'] = f'Вы уверены, что хотите удалить все данные о мастере {salesman.user.first_name}?'
        if request.method == 'POST':
            if request.POST.get('answer') == 'yes':
                salesman.delete()
                return redirect('home')
            return redirect('account')
    elif object_type == 'product':
        product = Product.objects.get(id=target_id)
        context['question'] = f'Вы уверены, что хотите удалить товар {product.name}?'
        if request.method == 'POST':
            if request.POST.get('answer') == 'yes':
                product.delete()
            return redirect('account')
    return render(request, 'consent_page.html', context)


def about_page(request):
    return render(request, 'about.html')


def faq_page(request):
    return render(request, 'dummy.html')


def conditions_page(request):
    return render(request, 'dummy.html')


def payment_page(request):
    return render(request, 'dummy.html')
