from django.contrib import admin
from .models import *


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "parent_category_id", "product_count"]
    sortable_by = ["name", "parent_category_id", "product_count"]
    search_fields = ["name"]

    def product_count(self, obj):
        return Product.objects.filter(category=obj).count()


@admin.register(Salesman)
class SalesmanAdmin(admin.ModelAdmin):
    search_fields = ["user__first_name", "user__username"]
    list_display = ["user__first_name", "moderate", "user__username", "user__email", "phone", "signup_date"]
    sortable_by = ["user__first_name", "signup_date"]
    list_filter = ["moderate"]
    fields = ["user", "phone", "photo", "description", "moderate"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    search_fields = ["name", "category__name"]
    list_display = ["name", "moderate", "price", "likes_count", "category__name", "salesman__user__first_name", "add_date"]
    sortable_by = ["name", "price", "likes_count", "category__name", "salesman__user__first_name", "add_date"]
    list_filter = ["moderate"]
    fields = ["salesman", "name", "category", "price", "description", "main_photo", "moderate"]

    def likes_count(self, obj):
        return obj.likes.count()
