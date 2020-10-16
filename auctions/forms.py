from .models import Bid, Comment, User, Listing, Category
from django import forms
from django.db.models import Max

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