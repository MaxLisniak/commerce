from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.fields.related import ForeignKey


class User(AbstractUser):
    pass

class Category(models.Model):
    name = models.CharField(max_length=32)

    def __str__(self):
        return f"Category: {self.name}"

class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=1000)
    starting_bid = models.IntegerField()
    photo = models.CharField(max_length=1000)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, related_name="listings", null=True, blank=True)
    owner = models.ForeignKey(User,related_name="listings", on_delete=models.CASCADE)

    def __str__(self):
        return f"Listing: {self.title} by {self.owner}"

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="comments", null=True)
    text = models.CharField(max_length=500)
    datetime = models.DateTimeField
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")

    def __str__(self):
        return f"Comment: {self.user}: {self.text[0:10]} at {self.listing}"

class Bid(models.Model):
    value = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")

    def __str__(self):
        return f"Bid: {self.value} by {self.user} at {self.listing}"