from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.forms import widgets
from django.forms.widgets import HiddenInput
from django.http import HttpResponse, HttpResponseRedirect
from django.http import request
from django.shortcuts import redirect, render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import Bid, Comment, User, Listing, Category
from django import forms


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

# Form for creating a listing
class CreateListing(forms.ModelForm):
    """Form for Listing model
    Args:
        
    """
    class Meta:
        model = Listing
        fields = ['title', 'price', 'description', 'image']


#@login_required(login_url="/login")
def create_listing(request):
    # create listing and redirect to index
    if request.method == "POST" and request.user.is_authenticated:
        form = CreateListing(request.POST, request.FILES)
        form = form.save(commit=False)
        form.created_by = request.user
        form.save()
        return render(request, "auctions/create_listing.html",{
            'form': form,
            'submitted': True
        })

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


# Form for adding comment
class AddComment(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['comment']

# Form for adding bid
class AddBid(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['bid']


def listing(request,listing_id):
    ## get listing information
    # when listing with that id exists 
    try:
        listing = Listing.objects.get(id=listing_id)

        def comment_form(request,listing):
            """ form for adding comments to a listing """
            if request.method=="POST" and request.POST.__contains__("add_comment"):
                form_comment = AddComment(request.POST)
                form_comment = form_comment.save(commit=False)
                form_comment.listing = listing
                form_comment.save()  
            return AddComment()

        def bid_form(request,listing):
            """ form for adding bids to a listing"""
            if request.method=="POST" and request.POST.__contains__("add_bid"):
                form_bid = AddBid(request.POST)
                form_bid = form_bid.save(commit=False)
                form_bid.listing=listing
                form_bid.save()
            return AddBid()

        def wishlist_form(request, listing):
            """ form for adding interested user to listing (for an authenticated user) """

            if request.method=="POST" and request.POST.__contains__("add_wishlist"):
                listing.interested_users.add(request.user)
                listing.save()
                return "Remove from wishlist", "rm_wishlist"
    
            elif request.method=="POST" and request.POST.__contains__("rm_wishlist"):
                listing.interested_users.remove(request.user)
                listing.save()
                return "Add to wishlist", "add_wishlist"

            else:
                if not listing.interested_users.filter(username = request.user.username):
                    return "Add to wishlist", "add_wishlist"
                else:
                    return "Remove from wishlist", "rm_wishlist"


        context = {
            'listing': listing,
            'bids': listing.bids.all(),
            'comments': listing.comments.all(),
            'comment_form': comment_form(request, listing),
            'bid_form': bid_form(request, listing),
            'wishlist_form_name': wishlist_form(request, listing)[1],
            'wishlist_form_text': wishlist_form(request, listing)[0],
            'listing_closed': listing.closed
        }

        # closing listing
        if request.method=="POST" and request.POST.__contains__("close_listing"):
            listing.closed = True
            listing.save()

        if listing.closed:
            context['bid_form'] = None
    

        # when nothing is posted
        if not request.method=="POST":
            return render(request, "auctions/listing.html", context)

        return HttpResponseRedirect(reverse('listing', kwargs={'listing_id': listing_id}))

    
    # when listing does not exist
    except Listing.DoesNotExist:
        return render(request, "auctions/listing.html",{
            "listing": None,
        })