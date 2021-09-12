from django.contrib.auth.models import AbstractUser
from django.core import validators
from django.db import models
from django.db.models.fields.related import ForeignKey
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from datetime import datetime

class User(AbstractUser):
    watchlist = models.ManyToManyField('Listing', blank=True, related_name="users_watching")


class Category(models.Model):
    name = models.CharField(max_length=32, unique=True)

    def __str__(self):
        return f"{self.name}"

class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=1000)
    starting_price = models.IntegerField(validators=[
        MinValueValidator(1)
    ])
    photo = models.CharField(max_length=1000)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, related_name="listings", null=True, blank=True)
    owner = models.ForeignKey(User,related_name="listings", on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    datetime = models.DateTimeField(default=datetime.now())

    def highest_bid(self):
        return self.bids.order_by("-value").first()

    def __str__(self):
        return f"{self.title}({self.description[0:32]}) by {self.owner}"

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="comments", null=True)
    text = models.CharField(max_length=500)
    datetime = models.DateTimeField
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")

    def __str__(self):
        return f"{self.user}: '{self.text[0:32]}' at {self.listing}"


class Bid(models.Model):
    value = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
        
    def clean(self):
        highest_bid = self.listing.highest_bid()
        if highest_bid:
            if self.value <= highest_bid.value:
                raise ValidationError(_('Your bid must be higher than the current one.'))
        else:
            if self.value < self.listing.starting_price:
                raise ValidationError(_('Your bid must not be lower than the starting one.'))

    def __str__(self):
        return f"{self.value} by {self.user} at {self.listing}"
