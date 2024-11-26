from django.shortcuts import render
from django.db.models import Q
from shop.views import AbstractPaginator, AbstractCart, AbstractCategories
from shop.models import Product, Category


class Context:
    context = {}
    request = None

    def _set_context(self):
        pass


class ProductView(Context, AbstractCart, AbstractCategories, AbstractPaginator):

    def _set_context(self):
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

    def product_info(self, request):
        self.request = request
        self._set_context()
        product_id = request.GET.get('product_id')
        product = Product.objects.get(id=product_id)
        self.context['salesman'] = product.salesman
        self.context['product'] = product
        return render(self.request, 'product_info.html', self.context)

    def products_page(self, request):
        self.request = request
        self._set_context()
        self.context['back_path'] = 'products'
        category_id = request.GET.get('category_id')
        limitation = self._get_search_limitations()
        flip = self.request.GET.get('flip')
        if flip == 'true':
            self.context = self._get_page_products(self.request, [], self.context, flip=True)
        else:
            if category_id:
                self.context['category'] = category = Category.objects.get(id=category_id)
                self.context['way'] = self._category_way(category_id)
                self.context['categories'] = categories = self._sub_categories_list(category, [])
                self.context['parent_categories_id'] = self._get_parent_categories_id(categories)
                priorities = self._get_products_by_categories_list(categories, limitation)
                products = sum(priorities, [])
            else:
                self.context['category'] = False
                products = Product.objects.filter(limitation).order_by('-add_date')
                self.context['categories'] = categories = Category.objects.all()
                self.context['parent_categories_id'] = self._get_parent_categories_id(categories)
            self.context = self._get_page_products(self.request, products, self.context)
        return render(self.request, 'products.html', self.context)
