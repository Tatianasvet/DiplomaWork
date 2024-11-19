from django.shortcuts import render, redirect
from shop.models import Salesman, Product


class Context:
    context = {}
    request = None


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

