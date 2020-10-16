from django.contrib import admin
from .models import User, Listing, Bid, Comment, Category

class ListingAdmin(admin.ModelAdmin):
    list_display = ("title", "price", 'created_by', 'closed')
class BidAdmin(admin.ModelAdmin):
    list_display = ("id", "bid", "listing", 'created_by')


# Register your models here.
admin.site.register(User)
admin.site.register(Listing, ListingAdmin)
admin.site.register(Bid, BidAdmin)
admin.site.register(Comment)
admin.site.register(Category)