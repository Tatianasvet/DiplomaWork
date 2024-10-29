from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class Category(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    # block_categories – это id обобщающей категории, 0 если её нет
    block_categories = models.IntegerField()


class User(models.Model):
    user_name = models.CharField(max_length=50)
    email = models.EmailField()
    password_hash = models.TextField()
    favourites_category = models.ManyToManyField(Category, related_name='favourites')


class Salesman(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = PhoneNumberField()
    photo = models.ImageField()
    logo_image = models.ImageField()
    likes = models.ManyToManyField(User, related_name='likes')
    description = models.TextField()
    categories = models.ManyToManyField(Category, related_name='categories')
    moderate = models.BooleanField(default=False)


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
    likes = models.ManyToManyField(User, related_name='like')
    select = models.ManyToManyField(User, related_name='select')
    category = models.ManyToManyField(Category)
    moderate = models.BooleanField(default=False)


class ProductPhoto(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    photo = models.ImageField()
    moderate = models.BooleanField(default=False)


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
    is_moderate = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)
