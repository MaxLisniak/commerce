from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.db.models.fields import CharField
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.forms import ModelForm, fields, models
from django.core.validators import MaxLengthValidator
from django.contrib.auth.decorators import login_required

from datetime import datetime

from .models import Category, Listing, User, Comment, Bid


def index(request):
    listings = Listing.objects.filter(active=True).order_by("-datetime").all()
    return render(request, "auctions/index.html", {
        "listings": listings,
    })


def login_view(request):
    next = request.POST.get('next', request.GET.get('next', '/'))
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            if next:
               return HttpResponseRedirect(next) 
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password.",
                "next": next,
            })
    else:
        return render(request, "auctions/login.html", {
            "next": next,
        })


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

class NewListingForm(ModelForm):
    class Meta:
        model = Listing
        fields = ["title", "description", "starting_price", "photo", "category"]

@login_required
def new_listing(request):
    if request.method == "POST":
        form = NewListingForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.owner = request.user
            listing.datetime = datetime.now()
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

class BidForm(ModelForm):
    class Meta:
        model = Bid
        fields = ["value", "user", "listing"]
        widgets = {
            'user': forms.HiddenInput(),
            'listing': forms.HiddenInput()}

def listing(request, id):
    try:
        listing = Listing.objects.get(pk=id)
    except Listing.DoesNotExist:
        return render(request, "auctions/404.html")
    if request.method == "POST":
        data = {
            "value": request.POST.get("value"),
            "user": request.user,
            "listing": listing,
        }
        form = BidForm(data)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('listing', args=[id]))
        else:
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "form": form,
                "bids": listing.bids.order_by('-value').all()
            })
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "form": BidForm(),
        "bids": listing.bids.order_by('-value').all()
    })

@login_required
def watch(request, id):
    try:
        listing = Listing.objects.get(pk=id)
    except Listing.DoesNotExist:
        return render(request, "auctions/404.html")
    next = request.GET.get("next")
    user = request.user
    user.watchlist.add(listing)
    user.save()
    if next:
        return HttpResponseRedirect(next)
    return HttpResponseRedirect(reverse('listing', args=[id]))

@login_required
def unwatch(request, id):
    try:
        listing = Listing.objects.get(pk=id)
    except Listing.DoesNotExist:
        return render(request, "auctions/404.html")
    next = request.GET.get("next")
    user = request.user
    user.watchlist.remove(listing)
    user.save()
    if next:
        return HttpResponseRedirect(next)
    return HttpResponseRedirect(reverse('listing', args=[id]))

@login_required
def deactivate(request, id):
    try:
        listing = Listing.objects.get(pk=id)
    except Listing.DoesNotExist:
        return render(request, "auctions/404.html")
    if not listing.active:
        return render(request, "auctions/forbidden.html")
    user = request.user
    if user == listing.owner:
        listing.active = False
        listing.save()
        return HttpResponseRedirect(reverse('listing', args=[id]))
    else:
        return render(request, "auctions/forbidden.html")

def categories(request):
    categories = Category.objects.all()
    return render(request, "auctions/categories.html", {
        "categories": categories,
    })

def category(request, name):
    category = Category.objects.filter(name=name).first()
    if not category:
        return render(request, "auctions/404.html")
    else:
        return render(request, "auctions/category.html", {
            "listings": category.listings.filter(active=True).order_by("-datetime").all(),
            "category": category,
        })
def watchlist(request):
    return render(request, "auctions/watchlist.html",{
        "listings": request.user.watchlist.all()
    })