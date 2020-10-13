from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.deletion import CASCADE
from django.db.models.fields import DateTimeField
from datetime import datetime


class User(AbstractUser):
    # watchlist
    pass

class Listing(models.Model):
    # picture
    pic = models.ImageField()
    # name
    name = models.CharField(max_length=100)
    # price
    price = models.DecimalField(max_digits=10, decimal_places=2)
    # date and time created
    date_time = DateTimeField(auto_now_add=True)
    # object name
    def __str__(self):
        return f"{self.id}: {self.name}"
    #---join with other tables---#
    # watchlist
    # bid
    # commment

class Bid(models.Model):
    # relationship to Listing
    listing = models.ForeignKey(Listing, on_delete=CASCADE, related_name="bids")
    # bid value
    bid = models.DecimalField(max_digits=5, decimal_places=2)
    # object name
    def __str__(self):
        return f"{self.bid}"


class Comment(models.Model):
    pass