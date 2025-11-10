from django.contrib import admin

from .models import Wishlist


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "created_at", "updated_at")
    search_fields = ("name", "user__username")
    filter_horizontal = ("rooms", "experiences")

