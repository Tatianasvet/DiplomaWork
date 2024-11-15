from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.db.models import Q, Count
from .forms import SignUpForm, SalesmanSignUpForm,  LoginForm, AddProductForm, ChangeSalesmanInfoForm
from .models import *


def start_page(request):
    limitation = Q(moderate__exact=True)
    categories = Category.objects.all()
    context = {'user': request.user,
               'categories': categories,
               'parent_categories_id': _get_parent_categories_id(categories),
               'select_id_list': _get_select_products_id_list(request.user),
               'like_id_list': _get_like_products_id_list(request.user),
               'popular_products': _most_popular_products(limitation)}
    return render(request, 'index.html', context)


def _most_popular_products(limitation):
    products = Product.objects.filter(limitation).annotate(like_count=Count('likes')).order_by('-like_count', '-add_date')
    return products[:8]


def _last_selected_products(limitation):
    products = Product.objects.filter(limitation).order_by('-select_time')
    return products[:8]


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
        limitation = _get_search_limitations(request)
        query = request.POST.get('search')
        if query == '':
            return products_page(request)
        sub_query_1 = query.lower()
        sub_query_2 = query.upper()
        if len(query) > 3:
            sub_query_2 = query[1:]
        if search_mode == 'product':
            # Приоритеты поиска
            lookup1 = Q(name=query)
            lookup2 = Q(name__icontains=query) | Q(name__icontains=sub_query_1) | Q(name__icontains=sub_query_2)
            lookup3 = Q(description__icontains=query) | Q(description__icontains=sub_query_1) | Q(description__icontains=sub_query_2)
            query_categories_1 = Category.objects.filter(lookup2)
            lookup4 = Q(category__in=query_categories_1)
            query_categories_2 = Category.objects.filter(lookup3)
            lookup5 = Q(category__in=query_categories_2)
            # поиск в базе данных
            priorities = []
            for lookup in [lookup1, lookup2, lookup3, lookup4, lookup5]:
                priorities.append(Product.objects.filter(lookup & limitation).order_by('-add_date'))
            clear_priorities = _delete_duplicates(priorities)
            # контекст
            context = {'priorities': clear_priorities,
                       'category': False,
                       'min_price': request.POST.get('min_price'),
                       'max_price': request.POST.get('max_price'),
                       'search_response': f'По запросу \"{query}\" найдено {_result_count(clear_priorities)} товаров'}
            context['categories'] = categories = Category.objects.all()
            context['search_query'] = query
            context['parent_categories_id'] = _get_parent_categories_id(categories)
            return render(request, 'products.html', context)
        elif search_mode == 'salesman':
            user_lookup = Q(first_name__icontains=query) | Q(first_name__icontains=sub_query_1) | Q(first_name__icontains=sub_query_2)
            users = User.objects.filter(user_lookup)
            lookup1 = Q(user__in=users)
            lookup2 = Q(description__icontains=query) | Q(description__icontains=sub_query_1) | Q(description__icontains=sub_query_2)
            priorities = [Salesman.objects.filter(lookup1 & limitation),
                          Salesman.objects.filter(lookup2 & limitation)]
            clear_priorities = _delete_duplicates(priorities)
            context = {'priorities': _delete_duplicates(priorities),
                       'search_query': query,
                       'search_response': f'По запросу \"{query}\" найдено {_result_count(clear_priorities)} мастеров'}
            return render(request, 'salesmans.html', context)
    else:
        return redirect('products')


def _delete_duplicates(priorities):
    id_list = []
    result = []
    for original_set in priorities:
        clear_set = []
        for iter_object in original_set:
            if iter_object.id not in id_list:
                clear_set.append(iter_object)
                id_list.append(iter_object.id)
        result.append(clear_set)
    return result


def _result_count(priorities):
    count = 0
    for clear_set in priorities:
        count += len(clear_set)
    return count


def _get_search_limitations(request):
    limitation = Q(moderate__exact=True)
    if request.method == 'POST':
        min_price = request.POST.get('min_price')
        max_price = request.POST.get('max_price')
        if min_price:
            limitation = limitation & Q(price__gte=int(min_price))
        if max_price:
            limitation = limitation & Q(price__lte=int(max_price))
    return limitation


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
    products = Product.objects.filter(select=request.user)
    context = {'products': products}
    return render(request, 'cart.html', context)


def contact_page(request):
    return render(request, 'contact.html')


def reviews_page(request):
    return render(request, 'reviews.html')


def checkout_page(request):
    return render(request, 'checkout.html')


def products_page(request):
    category_id = request.GET.get('category_id')
    limitation = _get_search_limitations(request)
    context = {'select_id_list': _get_select_products_id_list(request.user),
               'like_id_list': _get_like_products_id_list(request.user)}
    if request.method == 'POST':
        context['min_price'] = request.POST.get('min_price')
        context['max_price'] = request.POST.get('max_price')
    if category_id:
        context['category'] = category = Category.objects.get(id=category_id)
        context['way'] = _category_way(category_id)
        context['categories'] = categories = _sub_categories_list(category, [])
        context['parent_categories_id'] = _get_parent_categories_id(categories)
        context['priorities'] = [_get_products_by_categories_list(categories, limitation),]
    else:
        context['category'] = False
        context['priorities'] = [Product.objects.filter(limitation).order_by('-add_date'),]
        context['categories'] = categories = Category.objects.all()
        context['parent_categories_id'] = _get_parent_categories_id(categories)
    return render(request, 'products.html', context)


def _get_select_products_id_list(user):
    select_products = Product.objects.filter(select=user)
    id_list = []
    for product in select_products:
        id_list.append(product.id)
    return id_list


def _get_like_products_id_list(user):
    like_products = Product.objects.filter(likes=user)
    id_list = []
    for product in like_products:
        id_list.append(product.id)
    return id_list


def _sub_categories_list(parent_category, category_list) -> list:
    category_list.append(parent_category)
    for sub_category in Category.objects.all():
        if sub_category.parent_category_id == parent_category.id:
            category_list = _sub_categories_list(sub_category, category_list)
    return category_list


def _get_products_by_categories_list(categories_list, limitation):
    result = []
    for category in categories_list:
        products = Product.objects.filter(Q(category__exact=category) & limitation).order_by('-add_date')
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


def add_to_cart(request):
    user = request.user
    product_id = request.GET.get('product_id')
    product = Product.objects.get(id=product_id)
    product.select.add(user)
    product.save()
    return redirect(request.META['HTTP_REFERER'])


def del_from_cart(request):
    user = request.user
    product_id = request.GET.get('product_id')
    product = Product.objects.get(id=product_id)
    product.select.remove(user)
    return redirect(request.META['HTTP_REFERER'])


def like(request):
    user = request.user
    product_id = request.GET.get('product_id')
    product = Product.objects.get(id=product_id)
    product.likes.add(user)
    product.save()
    return redirect(request.META['HTTP_REFERER'])


def dislike(request):
    user = request.user
    product_id = request.GET.get('product_id')
    product = Product.objects.get(id=product_id)
    product.likes.remove(user)
    return redirect(request.META['HTTP_REFERER'])


def product_info(request):
    product_id = request.GET.get('product_id')
    product = Product.objects.get(id=product_id)
    context = {'salesman': product.salesman,
               'product': product}
    return render(request, 'product_info.html', context)


def salesmans_page(request):
    limitation = Q(moderate__exact=True)
    salesmans = Salesman.objects.filter(limitation)
    context = {'priorities': [salesmans,]}
    return render(request, 'salesmans.html', context)


def salesman_info_page(request):
    salesman_id = request.GET.get('salesman_id')
    salesman = Salesman.objects.get(id=salesman_id)
    limitation = Q(moderate__exact=True)
    query = Q(salesman__exact=salesman)
    products = Product.objects.filter(query & limitation).order_by('-add_date')
    context = {'salesman': salesman,
               'products': products,
               'select_id_list': _get_select_products_id_list(request.user),
               'like_id_list': _get_like_products_id_list(request.user)}
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

