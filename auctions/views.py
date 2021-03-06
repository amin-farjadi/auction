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
        "listings": Listing.objects.filter(closed=False),
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
    return redirect(reverse("index"))


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


@login_required(login_url="/login")
def create_listing(request):
    
    # create listing and redirect to index
    if request.method == "POST":
        form = CreateListing(request.POST, request.FILES)
        if form.is_valid():
            form = form.save(commit=False)
            form.created_by = request.user
            form.save()
            return redirect(reverse('index'))

        request.session['form_info'] = request.POST, request.FILES
        return redirect(reverse('create_listing'))

    # load page (with form error)
    else:
        form_info = request.session.pop('form_info', None)
        if form_info is None: form = CreateListing()
        else: form = CreateListing(form_info[0], form_info[1])

        return render(request, "auctions/create_listing.html", {'form': form})


def listing(request,listing_id):
    """get listing information"""
    # when listing with that id exists 
    try:
        listing = Listing.objects.get(id=listing_id)

        bid_error = request.session.pop('bid_error', None)

        context = {
            'listing': listing,
            'bids': listing.bids.all(),
            'comments': listing.comments.all(),
            'comment_form': comment_form(request, listing),
            'bid_form': bid_form(request, listing),
            'bid_error': bid_error,
            'wishlist_form_name': wishlist_form(request, listing)[1],
            'wishlist_form_text': wishlist_form(request, listing)[0],
            'listing_closed': close_auction(request, listing)[0],
            'auction_winner': close_auction(request, listing)[1]
        }
        
        # when nothing is get
        if request.method=="GET":
            return render(request, "auctions/listing.html", context)

        return redirect(reverse('listing', kwargs={'listing_id': listing_id}))

    
    # when listing does not exist
    except Listing.DoesNotExist:
        return render(request, "auctions/error.html", {'message': 'Such listing does not exist'})




def watchlist_page(request, username):
    if not request.user.username == username:
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/watchlist.html",{
            "watchlist": request.user.watchlists.all()
        })


def categories(request):
    return render(request, "auctions/categories.html",{
        'categories': Listing.objects.order_by('category').values('category').distinct()
    })


def category(request, category):
    listings = Listing.objects.filter(category=category, closed=False)
    if listings.count() != 0: 
        return render(request, "auctions/category.html",{
        'listings': listings,
        'category': category
        })
    else:
        return render(request, "auctions/error.html", {'message': 'No active listing under this category'})