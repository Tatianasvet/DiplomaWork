from django.shortcuts import render, redirect
from shop.models import Product


class Update:
    def _update_page(self, request):
        back_patch = request.GET.get('back_path')
        if back_patch is not None:
            return redirect(back_patch)
        else:
            return redirect(request.META['HTTP_REFERER'])


class Cart:
    def cart_page(self, request):
        if request.user.is_anonymous:
            return redirect('login')
        products = Product.objects.filter(select=request.user)
        context = {'products': products}
        return render(request, 'cart.html', context)


class Select(Update):
    def add_to_cart(self, request):
        user = request.user
        product_id = request.GET.get('product_id')
        product = Product.objects.get(id=product_id)
        product.select.add(user)
        product.save()
        return self._update_page(request)

    def del_from_cart(self, request):
        user = request.user
        product_id = request.GET.get('product_id')
        product = Product.objects.get(id=product_id)
        product.select.remove(user)
        return self._update_page(request)


class Like(Update):
    def like(self, request):
        user = request.user
        product_id = request.GET.get('product_id')
        product = Product.objects.get(id=product_id)
        product.likes.add(user)
        product.save()
        return self._update_page(request)

    def dislike(self, request):
        user = request.user
        product_id = request.GET.get('product_id')
        product = Product.objects.get(id=product_id)
        product.likes.remove(user)
        return self._update_page(request)
