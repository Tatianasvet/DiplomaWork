from django.shortcuts import render
from shop.views import Context, AbstractPaginator, AbstractSearch, AbstractCart, AbstractCategories
from shop.models import Product, Category


class ProductView(Context, AbstractSearch, AbstractCart, AbstractCategories, AbstractPaginator):
    def product_info(self, request):
        self.request = request
        product_id = request.GET.get('product_id')
        product = Product.objects.get(id=product_id)
        self.context['salesman'] = product.salesman,
        self.context['product'] = product
        return render(self.request, 'product_info.html', self.context)

    def products_page(self, request):
        self.request = request
        category_id = request.GET.get('category_id')
        limitation = self._get_search_limitations(self.request)
        if not request.user.is_anonymous:
            self.context['select_id_list'] = self._get_select_products_id_list(self.request.user)
            self.context['like_id_list'] = self._get_like_products_id_list(self.request.user)
        if category_id:
            self.context['category'] = category = Category.objects.get(id=category_id)
            self.context['way'] = self._category_way(category_id)
            self.context['categories'] = categories = self._sub_categories_list(category, [])
            self.context['parent_categories_id'] = self._get_parent_categories_id(categories)
            priorities = self._get_products_by_categories_list(categories, limitation)
        else:
            self.context['category'] = False
            priorities = [Product.objects.filter(limitation).order_by('-add_date'), ]
            self.context['categories'] = categories = Category.objects.all()
            self.context['parent_categories_id'] = self._get_parent_categories_id(categories)
        self.context = self._get_page_products(self.request, priorities, self.context)
        return render(self.request, 'products.html', self.context)
