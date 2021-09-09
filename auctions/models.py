from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.fields.related import ForeignKey


class User(AbstractUser):
    pass

class Category(models.Model):
    name = models.CharField(max_length=32)

class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=1000)
    starting_bid = models.IntegerField()
    photo = models.CharField(max_length=1000)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, related_name="listings", null=True)
    owner = models.ForeignKey(User,related_name="listings", on_delete=models.CASCADE)

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="comments", null=True)
    text = models.CharField(max_length=500)
    datetime = models.DateTimeField

class Bid(models.Model):
    value = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
