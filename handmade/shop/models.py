from django.core.paginator import Paginator
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):

    def __str__(self):
        return self.username


def id_category_choice():
    res = {}
    id_list = Category.objects.values('id')
    for id_dict in id_list:
        res[id_dict['id']] = Category.objects.get(id=id_dict['id']).name
    return res


class Category(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    parent_category_id = models.PositiveIntegerField(choices=id_category_choice, null=True, blank=True)

    def __str__(self):
        return self.name


class Salesman(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    phone = PhoneNumberField()
    photo = models.ImageField(upload_to="static/salesmans_photo")
    likes = models.ManyToManyField(CustomUser, related_name='likes', blank=True)
    description = models.TextField()
    categories = models.ManyToManyField(Category, related_name='categories', blank=True)
    signup_date = models.DateTimeField(auto_now_add=True)
    moderate = models.BooleanField(default=False)

    def __str__(self):
        return self.user.first_name


class Recommendations(models.Model):
    salesman = models.ForeignKey(Salesman,
                                 on_delete=models.CASCADE,
                                 related_name='salesman')
    recommendation = models.OneToOneField(Salesman,
                                          on_delete=models.CASCADE,
                                          related_name='recommendation',
                                          null=True)


class Links(models.Model):
    link = models.URLField()
    label = models.CharField(max_length=50)
    person = models.ForeignKey(Salesman, on_delete=models.CASCADE)


class Product(models.Model):
    salesman = models.ForeignKey(Salesman, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    price = models.PositiveIntegerField(default=1)
    main_photo = models.ImageField(upload_to="static/product_photo", null=True, blank=True)
    likes = models.ManyToManyField(CustomUser, related_name='like', blank=True)
    select = models.ManyToManyField(CustomUser, related_name='select', blank=True)
    add_date = models.DateTimeField(auto_now_add=True)
    moderate = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class SalesmanScore(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    salesman = models.ForeignKey(Salesman, on_delete=models.CASCADE)
    score = models.PositiveSmallIntegerField()


class ProductScore(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    score = models.PositiveSmallIntegerField()


class Review(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    text = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    moderate = models.BooleanField(default=False)

