from django.shortcuts import render, redirect
from django.db.models import Q, Count
from .forms import AddProductForm
from .models import *


PRODUCT_PER_PAGE_COUNT = 8


class Context:
    context = {}
    request = None


class AbstractCategories:
    def _all_categories(self):
        return Category.objects.all().order_by('name')

    def _get_parent_categories_id(self, categories):
        parent_categories_id = []
        for check_category in categories:
            for category in categories:
                if check_category.id == category.parent_category_id:
                    parent_categories_id.append(check_category.id)
                    break
        return parent_categories_id


class AbstractCart:
    def _get_select_products_id_list(self, user):
        select_products = Product.objects.filter(select=user)
        id_list = []
        for product in select_products:
            id_list.append(product.id)
        return id_list

    def _get_like_products_id_list(self, user):
        like_products = Product.objects.filter(likes=user)
        id_list = []
        for product in like_products:
            id_list.append(product.id)
        return id_list


class Home(Context, AbstractCategories, AbstractCart):
    limitation = Q(moderate__exact=True)
    categories = None

    def start_page(self, request):
        self.request = request
        self.categories = self._all_categories()
        self.context['user'] = self.request.user
        self.context['categories'] = self.categories
        self.context['parent_categories_id'] = self._get_parent_categories_id(self.categories)
        self.context['popular_products'] = self.__most_popular_products()
        self.context['now_view_products'] = self.__now_view_products()
        self.context['newest_products'] = self.__newest_products()
        if not self.request.user.is_anonymous:
            self.context['select_id_list'] = self._get_select_products_id_list(self.request.user)
            self.context['like_id_list'] = self._get_like_products_id_list(self.request.user)
        return render(request, 'index.html', self.context)

    def __most_popular_products(self):
        products = Product.objects.filter(self.limitation).annotate(like_count=Count('likes')).order_by('-like_count', '-add_date')
        return products[:8]

    def __now_view_products(self):
        products = Product.objects.filter(self.limitation).annotate(select_count=Count('select')).order_by('-select_count', '-add_date')
        return products[:8]

    def __newest_products(self):
        products = Product.objects.filter(self.limitation).order_by('-add_date')
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
            # контекст
            context = {'mode': search_mode,
                       'category': False,
                       'min_price': request.POST.get('min_price'),
                       'max_price': request.POST.get('max_price')}
            context = _get_page_products(request, priorities, context)
            if not request.user.is_anonymous:
                context['select_id_list'] = _get_select_products_id_list(request.user)
                context['like_id_list'] = _get_like_products_id_list(request.user)
            context['categories'] = categories = Category.objects.all()
            context['search_query'] = query
            context['parent_categories_id'] = _get_parent_categories_id(categories)
            return render(request, 'products.html', context)
        elif search_mode == 'salesman':
            user_lookup = Q(first_name__icontains=query) | Q(first_name__icontains=sub_query_1) | Q(first_name__icontains=sub_query_2)
            users = CustomUser.objects.filter(user_lookup)
            lookup1 = Q(user__in=users)
            lookup2 = Q(description__icontains=query) | Q(description__icontains=sub_query_1) | Q(description__icontains=sub_query_2)
            priorities = [Salesman.objects.filter(lookup1 & limitation),
                          Salesman.objects.filter(lookup2 & limitation)]
            context = {'mode': search_mode,
                       'search_query': query}
            context = _get_page_products(request, priorities, context)
            return render(request, 'salesmans.html', context)
    else:
        return products_page(request)


def _get_page_products(request, priorities, context):
    page_number = _page_number(request)
    objects = _delete_duplicates(priorities)
    p = Paginator(objects, PRODUCT_PER_PAGE_COUNT)
    page = p.page(page_number)
    context['page'] = page
    context['current_page_number'] = page_number
    context['has_previous'] = page.has_previous()
    if page.has_previous():
        context['previous_page_number'] = page.previous_page_number()
    context['has_next'] = page.has_next()
    if page.has_next():
        context['next_page_number'] = page.next_page_number()
    context['page_range'] = p.get_elided_page_range(number=page_number, on_each_side=2, on_ends=1)
    if request.method == 'POST':
        search_mode = request.POST.get('mode')
        query = request.POST.get('search')
        new_min_price = request.POST.get('change_min_price')
        if new_min_price:
            context['min_price'] = new_min_price
        else:
            context['min_price'] = request.POST.get('min_price')
        new_max_price = request.POST.get('change_max_price')
        if new_max_price:
            context['max_price'] = new_max_price
        else:
            context['max_price'] = request.POST.get('max_price')
        if search_mode == 'product' and query != '':
            context['search_response'] = f'По запросу \"{query}\" найдено {len(objects)} товаров'
        elif search_mode == 'salesman' and query != '':
            context['search_response'] = f'По запросу \"{query}\" найдено {len(objects)} мастеров'
    if request.method == 'GET':
        new_min_price = request.GET.get('change_min_price')
        if new_min_price:
            context['min_price'] = new_min_price
        else:
            context['min_price'] = request.GET.get('min_price')
        new_max_price = request.GET.get('change_max_price')
        if new_max_price:
            context['max_price'] = new_max_price
        else:
            context['max_price'] = request.GET.get('max_price')
    return context


def _delete_duplicates(priorities):
    id_list = []
    result = []
    for original_set in priorities:
        for iter_object in original_set:
            if iter_object.id not in id_list:
                result.append(iter_object)
                id_list.append(iter_object.id)
    return result


def _page_number(request):
    try:
        if request.method == 'GET':
            page_number = int(request.GET.get('page'))
        elif request.method == 'POST':
            page_number = int(request.POST.get('page'))
    except TypeError:
        page_number = 1
    return page_number


def _get_search_limitations(request):
    limitation = Q(moderate__exact=True)
    if request.method == 'POST':
        new_min_price = request.POST.get('change_min_price')
        new_max_price = request.POST.get('change_max_price')
        min_price = request.POST.get('min_price')
        max_price = request.POST.get('max_price')
        if new_min_price and new_min_price != 'None' and new_min_price != '':
            limitation = limitation & Q(price__gte=int(new_min_price))
        elif min_price and min_price != 'None' and min_price != '':
            limitation = limitation & Q(price__gte=int(min_price))
        if new_max_price and new_max_price != 'None' and new_max_price != '':
            limitation = limitation & Q(price__lte=int(new_max_price))
        elif max_price and max_price != 'None' and max_price != '':
            limitation = limitation & Q(price__lte=int(max_price))
    return limitation


def checkout_page(request):
    return render(request, 'checkout.html')


def products_page(request):
    category_id = request.GET.get('category_id')
    limitation = _get_search_limitations(request)
    context = {}
    if not request.user.is_anonymous:
        context['select_id_list'] = _get_select_products_id_list(request.user)
        context['like_id_list'] = _get_like_products_id_list(request.user)
    if category_id:
        context['category'] = category = Category.objects.get(id=category_id)
        context['way'] = _category_way(category_id)
        context['categories'] = categories = _sub_categories_list(category, [])
        context['parent_categories_id'] = _get_parent_categories_id(categories)
        priorities = _get_products_by_categories_list(categories, limitation)
    else:
        context['category'] = False
        priorities = [Product.objects.filter(limitation).order_by('-add_date'),]
        context['categories'] = categories = Category.objects.all()
        context['parent_categories_id'] = _get_parent_categories_id(categories)
    context = _get_page_products(request, priorities, context)
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
        result.append(Product.objects.filter(Q(category__exact=category) & limitation).order_by('-add_date'))
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
    limitation = Q(moderate__exact=True)
    priorities = [Salesman.objects.filter(limitation),]
    context = {'mode': 'salesman'}
    context = _get_page_products(request, priorities, context)
    return render(request, 'salesmans.html', context)


def salesman_info_page(request):
    salesman_id = request.GET.get('salesman_id')
    salesman = Salesman.objects.get(id=salesman_id)
    limitation = Q(moderate__exact=True)
    query = Q(salesman__exact=salesman)
    products = Product.objects.filter(query & limitation).order_by('-add_date')
    context = {'salesman': salesman,
               'products': products}
    if not request.user.is_anonymous:
        context['select_id_list'] = _get_select_products_id_list(request.user)
        context['like_id_list'] = _get_like_products_id_list(request.user)
    return render(request, 'salesman_info.html', context)


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
