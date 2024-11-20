from django.shortcuts import render, redirect
from django.db.models import Q, Count
from .models import *


PRODUCT_PER_PAGE_COUNT = 8


class Context:
    context = {}
    request = None


class AbstractPaginator:
    paginator = None
    page = None
    page_number = None

    def _get_page_products(self, request, priorities, context):
        self.page_number = self.__page_number(request)
        objects = self.__delete_duplicates(priorities)
        self.paginator = Paginator(objects, PRODUCT_PER_PAGE_COUNT)
        self.page = self.paginator.page(self.page_number)
        context = self.__context_manager(request, context)
        return context

    def __context_manager(self, request, context):
        context['page'] = self.page
        context['current_page_number'] = self.page_number
        context['has_previous'] = self.page.has_previous()
        if self.page.has_previous():
            context['previous_page_number'] = self.page.previous_page_number()
        context['has_next'] = self.page.has_next()
        if self.page.has_next():
            context['next_page_number'] = self.page.next_page_number()
        context['page_range'] = self.paginator.get_elided_page_range(number=self.page_number, on_each_side=2, on_ends=1)
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
                context['search_response'] = f'По запросу \"{query}\" найдено {self.paginator.count} товаров'
            elif search_mode == 'salesman' and query != '':
                context['search_response'] = f'По запросу \"{query}\" найдено {self.paginator.count} мастеров'
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

    def __page_number(self, request):
        try:
            if request.method == 'GET':
                page_number = int(request.GET.get('page'))
            elif request.method == 'POST':
                page_number = int(request.POST.get('page'))
        except TypeError:
            page_number = 1
        return page_number

    def __delete_duplicates(self, priorities):
        id_list = []
        result = []
        for original_set in priorities:
            for iter_object in original_set:
                if iter_object.id not in id_list:
                    result.append(iter_object)
                    id_list.append(iter_object.id)
        return result


class AbstractSearch:
    def _get_search_limitations(self, request):
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

    def _sub_categories_list(self, parent_category, category_list) -> list:
        category_list.append(parent_category)
        for sub_category in Category.objects.all():
            if sub_category.parent_category_id == parent_category.id:
                category_list = self._sub_categories_list(sub_category, category_list)
        return category_list

    def _category_way(self, category_id):
        category = Category.objects.get(id=category_id)
        way = [category, ]
        while category.parent_category_id:
            category = Category.objects.get(id=category.parent_category_id)
            way.append(category)
        way.reverse()
        return way

    def _get_products_by_categories_list(self, categories_list, limitation):
        result = []
        for category in categories_list:
            result.append(Product.objects.filter(Q(category__exact=category) & limitation).order_by('-add_date'))
        return result


class Home(Context, AbstractCategories, AbstractCart, AbstractPaginator):
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



