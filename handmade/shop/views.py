from django.shortcuts import render, redirect
from django.db.models import Q, Count
from .models import *


PRODUCT_PER_PAGE_COUNT = 8


class Context:
    context = {}
    request = None

    def _set_context(self):
        pass


class AbstractPaginator:
    """
    Context fields:
        1. Content:
            'page' <--
        2. Auxiliary data
            'current_page_number' <--
            'has_previous' <--
            'previous_page_number' <--
            'has_next' <--
            'next_page_number' <--
            'page_range' <--
            -->'min_price'
            -->'max_price'
    """
    paginator = None
    page = None
    page_number = None

    def _get_page_products(self, request, priorities, context, flip=False):
        self.__set_page_number(request)
        if not flip:
            objects = self.__delete_duplicates(priorities)
            self.paginator = Paginator(objects, PRODUCT_PER_PAGE_COUNT)
        self.page = self.paginator.page(self.page_number)
        context = self.__context_manager(context)
        return context

    def __context_manager(self, context):
        context['page'] = self.page
        context['current_page_number'] = self.page_number
        context['has_previous'] = self.page.has_previous()
        if self.page.has_previous():
            context['previous_page_number'] = self.page.previous_page_number()
        context['has_next'] = self.page.has_next()
        if self.page.has_next():
            context['next_page_number'] = self.page.next_page_number()
        context['page_range'] = self.paginator.get_elided_page_range(number=self.page_number, on_each_side=2, on_ends=1)
        return context

    def __set_page_number(self, request):
        try:
            if request.method == 'GET':
                self.page_number = int(request.GET.get('page'))
            elif request.method == 'POST':
                self.page_number = int(request.POST.get('page'))
        except TypeError:
            flip = request.GET.get('flip') == 'true'
            if self.page_number is None or not flip:
                self.page_number = 1


    def __delete_duplicates(self, priorities):
        id_list = []
        result = []
        for original_set in priorities:
            for iter_object in original_set:
                if iter_object.id not in id_list:
                    result.append(iter_object)
                    id_list.append(iter_object.id)
        return result

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

    MOST_POPULAR_PRODUCTS_COUNT = 8
    NOW_VIEW_PRODUCTS_COUNT = 8
    NEWEST_PRODUCTS_COUNT = 8

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
        return products[:self.MOST_POPULAR_PRODUCTS_COUNT]

    def __now_view_products(self):
        products = Product.objects.filter(self.limitation).annotate(select_count=Count('select')).order_by('-select_count', '-add_date')
        return products[:self.NOW_VIEW_PRODUCTS_COUNT]

    def __newest_products(self):
        products = Product.objects.filter(self.limitation).order_by('-add_date')
        return products[:self.NEWEST_PRODUCTS_COUNT]
