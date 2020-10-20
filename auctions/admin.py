from django.contrib import admin
from .models import User, Listing, Bid, Comment

class ListingAdmin(admin.ModelAdmin):
    list_display = ("title", "price", 'created_by', 'closed')
class BidAdmin(admin.ModelAdmin):
    list_display = ('created_by', "listing", "bid")
class CommentAdmin(admin.ModelAdmin):
    list_display = ("created_by", "listing", "comment")

# Register your models here.
admin.site.register(User)
admin.site.register(Listing, ListingAdmin)
admin.site.register(Bid, BidAdmin)
admin.site.register(Comment, CommentAdmin)