from django.db.models import fields
from django.forms import widgets
from .models import Bid, Comment, User, Listing, Category
from django import forms
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal


class AddBid(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.min_bid = kwargs.pop('min_bid', 0.01)
        self.listing = kwargs.pop('listing', '')
        self.created_by = kwargs.pop('created_by', '')
        super(AddBid, self).__init__(*args, **kwargs)

    class Meta:
        model = Bid
        fields = ['bid']



    def clean(self):
        bid = self.cleaned_data.get('bid')
        #self.cleaned_data.update({'listing': self.listing, 'created_by': self.created_by})
        self.fields.update(listing=self.listing)
        self.fields.update(created_by=self.user)
        if bid <= max(self.min_bid, self.listing.price):
            self.add_error('bid', 'Not good')      


