from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.deletion import CASCADE
from django.db.models.fields import CharField, DateTimeField
from datetime import datetime
import os
from django.conf import settings

class User(AbstractUser):
    # watchlist
    pass


class Listing(models.Model):
    # picture
    image = models.ImageField(upload_to = 'images',
        #default=os.path.join(settings.MEDIA_ROOT, 'images/default.jpg'),
        blank=True,
        null=True
    )
    # title
    title = models.CharField(max_length=100)
    # price
    price = models.DecimalField(max_digits=10, decimal_places=2)
    # description
    description = models.CharField(max_length=3000, blank=True, null=True)
    # date and time created
    date_time = DateTimeField(auto_now_add=True)
    # object title
    def __str__(self):
        return f"{self.id}: {self.title}"
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
    # relationship to Listing
    listing = models.ForeignKey(Listing, on_delete=CASCADE, related_name="comments")
    # comment 
    comment = CharField(max_length=500)
    # object name
    def __str__(self) -> str:
        return f"{self.id}: comment on {self.listing}"