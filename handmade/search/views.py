from django.shortcuts import render, redirect
from shop.views import AbstractPaginator, AbstractCart, AbstractCategories
from django.db.models import Q
from shop.models import CustomUser, Category, Product, Salesman


class Context:
    context = {}
    request = None

    def _set_context(self):
        pass


class Search(Context, AbstractCart, AbstractCategories, AbstractPaginator):
    """
    Class for search products and salesmans

    Context fields:
        1. Content:
            ... paginator fields
        2. Auxiliary data
            -->'mode' -- 'product' / 'salesman'
            'back_patch' = 'search'
            -->'search_query'
            'category' = False
            -->'min_price'
            -->'max_price'
            'select_id_list' <--
            'like_id_list' <--
            'categories' = all categories
            'parent_categories_id' <== all parent categories id
            ... paginator fields
    """
    limitation = Q(moderate__exact=True)
    lookup_list = []
    query, sub_query_1, sub_query_2 = None, None, None

    def _set_context(self):
        self.context['back_path'] = 'search'
        self.context['category'] = False
        if not self.request.user.is_anonymous:
            self.context['select_id_list'] = self._get_select_products_id_list(self.request.user)
            self.context['like_id_list'] = self._get_like_products_id_list(self.request.user)
        new_min_price = self.request.GET.get('change_min_price')
        if new_min_price and new_min_price != 'None' and new_min_price != '':
            self.context['min_price'] = new_min_price
        new_max_price = self.request.GET.get('change_max_price')
        if new_max_price and new_max_price != 'None' and new_max_price != '':
            self.context['max_price'] = new_max_price
        reset = self.request.GET.get('reset')
        if reset and reset != 'None' and reset != '':
            if 'min_price' in self.context.keys():
                self.context.pop('min_price')
            if 'max_price' in self.context.keys():
                self.context.pop('max_price')

    def _get_search_limitations(self):
        limitation = Q(moderate__exact=True)
        if 'min_price' in self.context.keys():
            min_price = self.context['min_price']
            if min_price and min_price != 'None' and min_price != '':
                limitation = limitation & Q(price__gte=int(min_price))
        if 'max_price' in self.context.keys():
            max_price = self.context['max_price']
            if max_price and max_price != 'None' and max_price != '':
                limitation = limitation & Q(price__lte=int(max_price))
        return limitation

    def search(self, request):
        self.request = request
        self._set_context()
        self.limitation = self._get_search_limitations()
        if self.request.method == 'POST':
            search_mode = self.request.POST.get('mode')
            self.context['mode'] = search_mode
            self.__create_queries()
            if self.query == '':
                return redirect('products')
            self.context['back_patch'] = 'search'
            self.__variable_search()
            return self.__render_result()
        else:
            if self.paginator is not None:
                flip = self.request.GET.get('flip')
                if flip == 'true':
                    self.context = self._get_page_products(self.request, [], self.context, flip=True)
                else:
                    self.__variable_search()
                return self.__render_result()
            else:
                return redirect('products')

    def __variable_search(self):
        if self.context['mode'] == 'product':
            self.__product_search()
        elif self.context['mode'] == 'salesman':
            self.__salesman_search()

    def __render_result(self):
        query = self.context['search_query']
        if self.context['mode'] == 'product':
            self.context['search_response'] = f'По запросу \"{query}\" найдено {self.paginator.count} товаров'
            return render(self.request, 'products.html', self.context)
        elif self.context['mode'] == 'salesman':
            self.context['search_response'] = f'По запросу \"{query}\" найдено {self.paginator.count} мастеров'
            return render(self.request, 'salesmans.html', self.context)
        else:
            return redirect('products')

    def __product_search(self):
        self.__create_product_lookup()
        priorities = self.__get_product_priorities()
        self.context['category'] = False
        self.context = self._get_page_products(self.request, priorities, self.context)
        self.context['categories'] = categories = Category.objects.all()
        self.context['parent_categories_id'] = self._get_parent_categories_id(categories)

    def __salesman_search(self):
        self.__create_salesman_lookup()
        priorities = self.__get_salesman_priorities()
        self.context = self._get_page_products(self.request, priorities, self.context)

    def __create_queries(self):
        self.query = self.request.POST.get('search')
        self.context['search_query'] = self.query
        self.sub_query_1 = self.query.lower()
        self.sub_query_2 = self.query.upper()
        if len(self.query) > 3:
            self.sub_query_2 = self.query[1:]

    def __create_product_lookup(self):
        lookup1 = Q(name=self.query)
        lookup2 = (Q(name__icontains=self.query) |
                   Q(name__icontains=self.sub_query_1) |
                   Q(name__icontains=self.sub_query_2))
        lookup3 = (Q(description__icontains=self.query) |
                   Q(description__icontains=self.sub_query_1) |
                   Q(description__icontains=self.sub_query_2))
        query_categories_1 = Category.objects.filter(lookup2)
        lookup4 = Q(category__in=query_categories_1)
        query_categories_2 = Category.objects.filter(lookup3)
        lookup5 = Q(category__in=query_categories_2)
        self.lookup_list = [lookup1, lookup2, lookup3, lookup4, lookup5]

    def __create_salesman_lookup(self):
        user_lookup = (Q(first_name__icontains=self.query) |
                       Q(first_name__icontains=self.sub_query_1) |
                       Q(first_name__icontains=self.sub_query_2))
        users = CustomUser.objects.filter(user_lookup)
        lookup1 = Q(user__in=users)
        lookup2 = (Q(description__icontains=self.query) |
                   Q(description__icontains=self.sub_query_1) |
                   Q(description__icontains=self.sub_query_2))
        self.lookup_list = [lookup1, lookup2]

    def __get_product_priorities(self):
        priorities = []
        for lookup in self.lookup_list:
            priorities.append(Product.objects.filter(lookup & self.limitation).order_by('-add_date'))
        return priorities

    def __get_salesman_priorities(self):
        priorities = []
        for lookup in self.lookup_list:
            priorities.append(Salesman.objects.filter(lookup & self.limitation).order_by('-add_date'))
        return priorities
