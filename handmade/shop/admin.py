from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import SignUpForm, CustomUserChangeForm
from .models import *


class CustomUserAdmin(UserAdmin):
    add_form = SignUpForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ["username", "email", "first_name", "is_staff", "is_superuser"]

admin.site.register(CustomUser, CustomUserAdmin)


admin.site.register(Category)
admin.site.register(Salesman)
admin.site.register(Recommendations)
admin.site.register(Links)
admin.site.register(Product)
admin.site.register(SalesmanScore)
admin.site.register(ProductScore)
admin.site.register(Review)
