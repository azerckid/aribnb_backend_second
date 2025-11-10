from django.contrib import admin

from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("__str__", "rating", "payload", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("user__username", "room__name", "experience__name")
 
