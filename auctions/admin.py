from django.contrib import admin
from .models import User, Listing, Bid, Comment, Category


class BidAdmin(admin.ModelAdmin):
    list_display = ("id", "bid", "listing")


# Register your models here.
admin.site.register(User)
admin.site.register(Listing)
admin.site.register(Bid, BidAdmin)
admin.site.register(Comment)
admin.site.register(Category)