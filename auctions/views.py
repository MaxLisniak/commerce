from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.db.models.fields import CharField, IntegerField, URLField
from django.forms.forms import Form
from django.forms.widgets import NumberInput, Select, TextInput, Textarea, URLInput
from django.http import HttpResponse, HttpResponseRedirect, request
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.forms import ModelForm, fields, models
from django.core.validators import MaxLengthValidator
from django.contrib.auth.decorators import login_required

from datetime import datetime

from .models import Category, Listing, Notification, User, Comment, Bid


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

class UserForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].required = True
        self.fields['email'].required = True
        self.fields['password'].required = True

    class Meta:
        model = User
        fields = ["username", "email", "password"]
        widgets = {
            'username': forms.TextInput(attrs={'autocomplete': 'off',
            "class": "form-input"}),
            'email': forms.EmailInput(attrs={'autocomplete': 'off',
            "class": "form-input"}),
            'password': forms.PasswordInput(attrs={'class': "form-input"})
        }
        help_texts = {
            'username': None,
        }

def register(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            confirmation = request.POST["confirmation"]
            if request.POST["password"] != confirmation:
                return render(request, "auctions/register.html", {
                    "message": "Passwords must match.",
                    "form": form
                })
        # Attempt to create new user
            try:
                # user = User.objects.create_user(username, email, password)
                user = form.save()
            except IntegrityError:
                return render(request, "auctions/register.html", {
                    "message": "Username already taken.",
                    "form": form
                })
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        return render(request, "auctions/register.html", {
            "form": form,
        })
    else:
        return render(request, "auctions/register.html", {
            "form": UserForm()
        })

class NewListingForm(ModelForm):
    class Meta:
        model = Listing
        fields = ["title", "description", "starting_price", "photo", "category"]
        widgets = {
            'title': TextInput(attrs={'autocomplete': 'off', 
                                      "class": "form-input"}),
            'description': Textarea(attrs={'autocomplete': 'off', 
                                           "class": "form-input area", 
                                           }),
            'starting_price': NumberInput(attrs={'autocomplete': 'off', 
                                                 "class": "form-input"}),
            'photo': URLInput(attrs={'autocomplete': 'off', 
                                     "class": "form-input"}),
            'category': Select(attrs={"class": "form-input"})
        } 

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
            'listing': forms.HiddenInput(),
            'value': NumberInput(attrs={'autocomplete': 'off'})
            }

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ["text", "user", "listing", "datetime"]
        widgets = {
            'user': forms.HiddenInput(),
            'listing': forms.HiddenInput(),
            'datetime': forms.HiddenInput(),
            'text': Textarea(attrs={'autocomplete': 'off'})
            }

def listing(request, id):
    try:
        listing = Listing.objects.get(pk=id)
    except Listing.DoesNotExist:
        return render(request, "auctions/404.html")
    comments = Comment.objects.filter(listing=listing).order_by("-datetime").all()
    if request.method == "POST":
        if 'place_bid' in request.POST:
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
                    "comment_form": CommentForm(),
                    "bids": listing.bids.order_by('-value').all(),
                    "comments": comments,
                })
        if 'comment' in request.POST:
            comment_data = {
                "text": request.POST.get("text"),
                "user": request.user,
                "listing": listing,
                "datetime": datetime.now(),
            }
            comment_form = CommentForm(comment_data)
            if comment_form.is_valid():
                comment_form.save()
                return HttpResponseRedirect(reverse('listing', args=[id]))
            else:
                return render(request, "auctions/listing.html", {
                    "listing": listing,
                    "form": BidForm(),
                    "comment_form": comment_form,
                    "bids": listing.bids.order_by('-value').all(),
                    "comments": comments,
                })
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "form": BidForm(),
        "comment_form": CommentForm(),
        "bids": listing.bids.order_by('-value').all(),
        "comments": comments,
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
        notification_text = f"Congratulations! You won the bid '{listing}'!"
        notification = Notification(user=listing.highest_bid().user, 
                    text=notification_text, 
                    datetime=datetime.now(),
                    url=reverse('listing', args=[listing.id]),
                    )
        notification.save()
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
@login_required
def watchlist(request):
    return render(request, "auctions/watchlist.html",{
        "listings": request.user.watchlist.all()
    })

@login_required
def notifications(request):
    user = request.user
    notifications = user.notifications.order_by("-datetime").all()
    return render(request, "auctions/notifications.html",{
        "notifications": notifications,
    })

@login_required
def notification(request, id):
    try:
        notification = Notification.objects.get(pk=id)
    except Notification.DoesNotExist:
        return render(request, "auctions/404.html")
    if notification.user != request.user:
        return render(request, "auctions/forbidden.html")
    notification.seen = True
    notification.save()
    return HttpResponseRedirect(notification.url)

@login_required
def my_listings(request):
    user = request.user
    return render(request, "auctions/my_listings.html", {
        "listings": user.listings.order_by("active").order_by("-datetime").all()
    })

@login_required
def my_bids(request):
    user = request.user
    return render(request, "auctions/my_bids.html", {
        "bids": user.bids.order_by("-datetime").all()
    })