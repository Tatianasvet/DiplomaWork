from django.contrib import admin
from shop.models import Salesman


@admin.register(Salesman)
class SalesmanAdmin(admin.ModelAdmin):
    search_fields = ["user__first_name", "user__username"]
    list_display = ["user__first_name", "moderate", "user__username", "user__email", "phone", "signup_date"]
    sortable_by = ["user__first_name", "signup_date"]
    list_filter = ["moderate"]
    fields = ["user", "phone", "photo", "description", "moderate"]
