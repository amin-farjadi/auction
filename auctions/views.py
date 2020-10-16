from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.db.utils import Error
from django.forms import widgets
from django.forms.widgets import HiddenInput
from django.http import HttpResponse, HttpResponseRedirect
from django.http import request
from django.shortcuts import redirect, render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .forms import *

def index(request):
    return render(request, "auctions/index.html",{
        "listings": Listing.objects.all(),
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


#@login_required(login_url="/login")
def create_listing(request):
    # create listing and redirect to index
    if request.method == "POST" and request.user.is_authenticated:
        form = CreateListing(request.POST, request.FILES)
        if form.is_valid():
            form = form.save(commit=False)
            form.created_by = request.user
            form.save()
            return render(request, "auctions/create_listing.html",{
                'form': form,
                'submitted': True
            })
        # form = CreateListing(request.POST, request.FILES, user_id=request.user.pk)
        # if form.is_valid():
        #     form.save()
        #     return render(request, "auctions/create_listing.html",{
        #         'form': form,
        #         'submitted': True
        #     })
        # else: 
        #     return render(request, "auctions/create_listing.html",{
        #         'form': form,
        #         'submitted': False
        #     })

    # present form to be filled in
    elif (request.method == "GET" and request.user.is_authenticated):
        form = CreateListing()
        return render(request, "auctions/create_listing.html",{
            'form': form,
            'submitted': False
        })
    
    else:
        return render(request, "auctions/login.html",{
            "message": "You must be logged in to create a listing."
        })


def listing(request,listing_id):
    """get listing information"""
    # when listing with that id exists 
    try:
        listing = Listing.objects.get(id=listing_id)

        context = {
            'listing': listing,
            'bids': listing.bids.all(),
            'comments': listing.comments.all(),
            'comment_form': comment_form(request, listing),
            'bid_form': bid_form(request, listing),
            'wishlist_form_name': wishlist_form(request, listing)[1],
            'wishlist_form_text': wishlist_form(request, listing)[0],
            'listing_closed': close_auction(request, listing)[0],
            'auction_winner': close_auction(request, listing)[1]
        }
        #

        # when nothing is posted
        if not request.method=="POST":
            return render(request, "auctions/listing.html", context)

        return HttpResponseRedirect(reverse('listing', kwargs={'listing_id': listing_id}))
    
    # when listing does not exist
    except Listing.DoesNotExist:
        return render(request, "auctions/listing.html",{
            "listing": None,
        })


def watchlist_page(request, username):
    if not request.user.username == username:
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/watchlist.html",{
            "watchlist": request.user.watchlists.all()
        })


def categories(request):
    return render(request, "auctions/categories.html",{
        'categories': Category.objects.all()
    })


def category(request, category):
    try:
     category = Category.objects.get(category=category)
     return render(request, "auctions/category.html",{
        'listings': category.listings.all()
     })

    except Category.DoesNotExist:
        return HttpResponse('This category does not exist')