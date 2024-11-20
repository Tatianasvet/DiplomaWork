from django.shortcuts import render, redirect
from shop.views import Context, AbstractPaginator, AbstractCart, AbstractCategories, AbstractSearch
from django.db.models import Q
from shop.models import CustomUser, Category, Product, Salesman


class Search(Context, AbstractSearch, AbstractCart, AbstractCategories, AbstractPaginator):
    limitation = Q(moderate__exact=True)
    lookup_list = []
    query, sub_query_1, sub_query_2 = None, None, None

    def search(self, request):
        self.request = request
        if self.request.method == 'POST':
            search_mode = self.request.POST.get('mode')
            self.context['mode'] = search_mode
            self.limitation = self._get_search_limitations(self.request)
            self.__create_queries()
            if self.query == '':
                return redirect('products')
            if search_mode == 'product':
                self.__product_search()
                return render(self.request, 'products.html', self.context)
            elif search_mode == 'salesman':

                return render(self.request, 'salesmans.html', self.context)
        else:
            return redirect('products')

    def __product_search(self):
        self.__create_product_lookup()
        priorities = self.__get_product_priorities()
        self.context['category'] = False
        self.context['min_price'] = self.request.POST.get('min_price')
        self.context['max_price'] = self.request.POST.get('max_price')
        self.context = self._get_page_products(self.request, priorities, self.context)
        if not self.request.user.is_anonymous:
            self.context['select_id_list'] = self._get_select_products_id_list(self.request.user)
            self.context['like_id_list'] = self._get_like_products_id_list(self.request.user)
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
