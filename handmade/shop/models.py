from django.contrib.auth.models import User
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


def category_choice():
    res = {}
    id_list = Category.objects.values('id')
    for id_dict in id_list:
        res[id_dict['id']] = Category.objects.get(id=id_dict['id']).name
    return res


class Category(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    parent_category_id = models.PositiveSmallIntegerField(choices=category_choice, null=True, blank=True)

    def __str__(self):
        return self.name


class Salesman(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = PhoneNumberField()
    photo = models.ImageField(upload_to="static/salesmans_photo")
    likes = models.ManyToManyField(User, related_name='likes', null=True, blank=True)
    description = models.TextField()
    categories = models.ManyToManyField(Category, related_name='categories')
    signup_date = models.DateTimeField(auto_now_add=True)
    moderate = models.BooleanField(default=False)

    def __str__(self):
        return self.name


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
    likes = models.ManyToManyField(User, related_name='like', null=True, blank=True)
    select = models.ManyToManyField(User, related_name='select', null=True, blank=True)
    add_date = models.DateTimeField(auto_now_add=True)
    moderate = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class ProductPhoto(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to="static/product_photo")
    number = models.PositiveSmallIntegerField(default=1)
    moderate = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.product.name}_photo_{self.number}'


class SalesmanScore(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    salesman = models.ForeignKey(Salesman, on_delete=models.CASCADE)
    score = models.PositiveSmallIntegerField()


class ProductScore(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    score = models.PositiveSmallIntegerField()


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    text = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    is_moderate = models.BooleanField(default=False)
