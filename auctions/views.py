from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.forms import widgets
from django.forms.widgets import HiddenInput
from django.http import HttpResponse, HttpResponseRedirect
from django.http import request
from django.shortcuts import redirect, render
from django.urls import reverse
from .models import Comment, User, Listing
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


def create_listing(request):
    # create listing and redirect to index
    if request.method == "POST" and request.user.is_authenticated:
        form = CreateListing(request.POST, request.FILES)
        if form.is_valid:
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



def listing(request,listing_id):
    ## get listing information
    # when listing with that id exists 
    try:
        listing = Listing.objects.get(id=listing_id)

        ## if comment is being added
        if request.method == "POST":
            form_comment = AddComment(request.POST)
            form_comment = form_comment.save(commit=False)
            form_comment.listing = listing
            if True:
                form_comment.save()
                # get bid info
                bids = listing.bids.all()
                # get comments
                comments = listing.comments.all()
                # add comment form
                form_comment = AddComment()
                # pass on to listing.html
                return render(request, "auctions/listing.html",{
                    "listing": listing,
                    "bids": bids,
                    "comments": comments,
                    "form": form_comment,

                   })


        ## if no comment is being added

        # get bid info
        bids = listing.bids.all()
        # get comments
        comments = listing.comments.all()
        # add comment form
        form_comment = AddComment()
        # pass on to listing.html
        return render(request, "auctions/listing.html",{
            "listing": listing,
            "bids": bids,
            "comments": comments,
            "form": form_comment,
        })
    
    # when listing does not exist
    except Listing.DoesNotExist:
        return render(request, "auctions/listing.html",{
            "listing": None,
        })