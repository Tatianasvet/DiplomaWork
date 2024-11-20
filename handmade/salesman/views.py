from django.shortcuts import render, redirect
from django.db.models import Q
from shop.views import Context, AbstractPaginator, AbstractCategories, AbstractCart
from shop.models import Salesman, Product, Category
from .forms import AddProductForm


class Profile(Context):
    def account_page(self, request):
        self.request = request
        if request.user.first_name:
            salesman = Salesman.objects.get(user=request.user)
            products = Product.objects.filter(salesman=salesman).order_by('-add_date')
            self.context['salesman'] = salesman
            self.context['products'] = products
            return render(request, 'account.html', self.context)
        else:
            return redirect('cart')


class SalesmanView(Context, AbstractCart, AbstractPaginator, AbstractCategories):
    def salesman_info_page(self, request):
        self.request = request
        salesman_id = self.request.GET.get('salesman_id')
        salesman = Salesman.objects.get(id=salesman_id)
        limitation = Q(moderate__exact=True)
        query = Q(salesman__exact=salesman)
        products = Product.objects.filter(query & limitation).order_by('-add_date')
        self.context['salesman'] = salesman
        self.context['products'] = products
        if not self.request.user.is_anonymous:
            self.context['select_id_list'] = self._get_select_products_id_list(self.request.user)
            self.context['like_id_list'] = self._get_like_products_id_list(self.request.user)
        return render(self.request, 'salesman_info.html', self.context)

    def salesmans_page(self, request):
        self.request = request
        limitation = Q(moderate__exact=True)
        priorities = [Salesman.objects.filter(limitation), ]
        self.context['mode'] = 'salesman'
        self.context = self._get_page_products(self.request, priorities, self.context)
        return render(self.request, 'salesmans.html', self.context)

    def add_product(self, request):
        self.request = request
        self.context['success'] = False
        if self.request.method == 'POST':
            form = AddProductForm(self.request.POST, self.request.FILES)
            if form.is_valid():
                self.__new_product()
            else:
                self.context['error_message'] = form.errors
        else:
            root_categories = Category.objects.filter(parent_category_id=None).order_by('name')
            categories = []
            for root in root_categories:
                categories += self._sub_categories_list(root, [])
            self.context['categories'] = categories
        return render(self.request, 'product_add_form.html', self.context)

    def __new_product(self):
        user = self.request.user
        salesman = Salesman.objects.get(user=user)
        category_id = self.request.POST.get('category_id')
        category = Category.objects.get(id=category_id)
        Product.objects.create(salesman=salesman,
                               name=self.request.POST.get('name'),
                               description=self.request.POST.get('description'),
                               main_photo=self.request.FILES['main_photo'],
                               category=category,
                               price=self.request.POST.get('price'))
        self.context['success'] = True

    def delite_consent_page(self, request):
        self.request = request
        object_type = self.request.GET.get('object_type')
        target_id = self.request.GET.get('target_id')
        self.context['consent'] = False
        self.context['object_type'] = object_type
        self.context['target_id'] = request.GET.get('target_id')
        if object_type == 'salesman':
            salesman = Salesman.objects.get(id=target_id)
            self.context['question'] = f'Вы уверены, что хотите удалить все данные о мастере {salesman.user.first_name}?'
            if self.request.method == 'POST':
                if self.request.POST.get('answer') == 'yes':
                    salesman.delete()
                    return redirect('home')
                return redirect('account')
        elif object_type == 'product':
            product = Product.objects.get(id=target_id)
            self.context['question'] = f'Вы уверены, что хотите удалить товар {product.name}?'
            if self.request.method == 'POST':
                if self.request.POST.get('answer') == 'yes':
                    product.delete()
                return redirect('account')
        return render(self.request, 'consent_page.html', self.context)