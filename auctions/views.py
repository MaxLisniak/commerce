from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.db.models.fields import CharField
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.forms import ModelForm, fields, models
from django.core.validators import MaxLengthValidator

from .models import Category, Listing, User, Comment, Bid


def index(request):
    listings = Listing.objects.all()
    listings_with_bids = []
    for listing in listings:
        bid = Bid.objects.filter(listing=listing).order_by("-value").first()
        if bid:
            pair = (listing, bid.value)
        else:
            pair = (listing, listing.starting_price)
        listings_with_bids.append(pair)
    return render(request, "auctions/index.html", {
        "listings": listings_with_bids,
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

# class NewListingForm(forms.Form):
#     title = forms.CharField(max_length=64)
#     description = forms.CharField(max_length=1000)
#     starting_bid = forms.IntegerField()
#     photo = forms.CharField(max_length=1000)
#     category = forms.ModelChoiceField(queryset=Category.objects.all())
class NewListingForm(ModelForm):
    class Meta:
        model = Listing
        fields = ["title", "description", "starting_price", "photo", "category"]


def new_listing(request):
    if request.method == "POST":
        form = NewListingForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.owner = request.user
            listing.save()
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/new_listing.html",{
                "form": form 
            })
    else:
        form = NewListingForm()
        return render(request, "auctions/new_listing.html",{
            "form": form 
        })