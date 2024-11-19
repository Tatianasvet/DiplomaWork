from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import SignUpForm, CustomUserChangeForm
from shop.models import CustomUser


class CustomUserAdmin(UserAdmin):
    add_form = SignUpForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ["username", "email", "first_name", "is_staff", "is_superuser"]

admin.site.register(CustomUser, CustomUserAdmin)
