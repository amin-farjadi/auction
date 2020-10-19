from django.forms import widgets
from .models import Bid, Comment, User, Listing, Category
from django import forms
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal


# Form for creating a listing
class CreateListing(forms.ModelForm):
    """Form for Listing model
    Args:
        
    """
    class Meta:
        model = Listing
        fields = ['title', 'price', 'description', 'image']


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


class AddBid(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.min_bid = kwargs.pop('min_bid', 0.01)
        super(AddBid, self).__init__(*args, **kwargs)

    class Meta:
        model = Bid
        fields = ['bid']

    def clean(self):
        bid = self.cleaned_data.get('bid')
        if bid <= self.min_bid:
            self.add_error('bid', 'Bid must be higher than {:.2f}'.format(self.min_bid))


# Adding bid function
def bid_form(request,listing):
    """ form for adding bids to a listing"""
    if request.method=="POST" and request.POST.__contains__("add_bid"):
        if listing.bids.exists():
            max_bid = listing.bids.all().aggregate(models.Max('bid'))
            max_bid = max(listing.price, max_bid['bid__max'])
        else:
            max_bid = listing.price

        form_bid = AddBid( request.POST, min_bid=max_bid)

        if form_bid.is_valid():
            instance = form_bid.save(commit=False)
            instance.listing=listing
            instance.created_by = request.user
            instance.save() 
        else:
            request.session['bid_error'] = form_bid.errors.get('bid')[0]

        return form_bid    

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
            return "+ Add to watchlist", "add_wishlist"
        else:
            return "- Remove from watchlist", "rm_wishlist"


def close_auction(request, listing):
    """ function checking if auction is closed, if so who is the winning user"""
    if request.method=="POST" and request.POST.__contains__("close_listing"):
        listing.closed = True
        listing.save()

    if listing.closed:
        max_bid = listing.bids.all().aggregate(models.Max('bid'))
        max_bid = max_bid['bid__max']
        if max_bid is None:
            auction_winner = None
        else:
            winning_bid = listing.bids.get(bid=max_bid)
            auction_winner = winning_bid.created_by

        return listing.closed, auction_winner

    else:
        return listing.closed, None