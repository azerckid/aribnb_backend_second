from django.contrib import admin
from .models import House

# Register your models here.
@admin.register(House)
class HouseAdmin(admin.ModelAdmin):
    fields = (
        "name",
        "address",
        ("price_per_night", "pets_allowed"),
        "description",
        ("latitude", "longitude"),
        ("created_at", "updated_at"),
    )
    readonly_fields = ("created_at", "updated_at")

    list_display = ("name", "price_per_night", "address", "pets_allowed")
    list_filter = ("price_per_night", "pets_allowed")
    search_fields = ("name", "address")
    ordering = ("-price_per_night",)
    list_display_links = ("name", "address")
    list_editable = ("price_per_night", "pets_allowed")
   