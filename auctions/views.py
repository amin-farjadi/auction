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
from .models import Bid, Comment, User, Listing, Category
from django import forms
from django.db.models import Max

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

    # def __init__(self, *args, **kwargs):
    #     user_id = kwargs.pop('user_id','')
    #     super(CreateListing, self).__init__(*args, **kwargs)
    #     self.fields['created_by'] = forms.ModelChoiceField(queryset=User.objects.filter(pk=user_id), widget=forms.HiddenInput())


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


# Form for adding comment
class AddComment(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['comment']

# Adding comment function
def comment_form(request,listing):
    """ form for adding comments to a listing """
    if request.method=="POST" and request.POST.__contains__("add_comment"):
        form_comment = AddComment(request.POST)
        if form_comment.is_valid():
            form_comment = form_comment.save(commit=False)
            form_comment.listing = listing
            form_comment.created_by = request.user
            form_comment.save()  
    return AddComment()

# Form for adding bid
class AddBid(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['bid']

# Adding bid function
def bid_form(request,listing):
    """ form for adding bids to a listing"""
    if request.method=="POST" and request.POST.__contains__("add_bid"):
        form_bid = AddBid(request.POST)

        if form_bid.is_valid():
            form_bid = form_bid.save(commit=False)
            form_bid.listing=listing
            form_bid.created_by = request.user
            #---obtaining max bid on listing
            bid = form_bid.bid              
            max_bid = listing.bids.all().aggregate(Max('bid'))
            max_bid = max_bid['bid__max']
            # if the listing does not have a bid
            if max_bid is None: max_bid = 0
            #---
            # if bid is high enough, save bid
            if bid > max(listing.price, max_bid):  
                form_bid.save()

            # if bid is not high enough
            else:
                pass
        
        # if form is not valid 
        else:
            pass

    return AddBid()

# Adding to Wishlist function
def wishlist_form(request, listing):
    """ Function (form) for adding interested user to listing (for an authenticated user) """

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


def close_auction(request, listing):
    """ function checking if auction is closed, if so who is the winning user"""
    if request.method=="POST" and request.POST.__contains__("close_listing"):
        listing.closed = True
        listing.save()

    if listing.closed:
        max_bid = listing.bids.all().aggregate(Max('bid'))
        max_bid = max_bid['bid__max']
        if max_bid is None:
            auction_winner = None
        else:
            winning_bid = listing.bids.get(bid=max_bid)
            auction_winner = winning_bid.created_by

        return listing.closed, auction_winner

    else:
        return listing.closed, None



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