from django.contrib import admin

from .models import Amenity, Room, Bed


@admin.action(description="Set all prices to zero")
def reset_prices(model_admin, request, rooms):
    for room in rooms.all():
        room.price = 0
        room.save()


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    actions = (reset_prices,)
    list_display = (
        "name",
        "price",
        "kind",
        "total_amenities",
        "rating",
        "owner",
        "created_at",
    )
    list_filter = (
        "country",
        "city",
        "pet_friendly",
        "kind",
        "amenities",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "name",
        "^price",
        "=owner__username",
        "address",
    )
    ordering = ("-created_at",)
    filter_horizontal = ("amenities",)


@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")
    search_fields = ("name",)


@admin.register(Bed)
class BedAdmin(admin.ModelAdmin):
    list_display = ("name", "room", "bed_type", "capacity", "created_at")
    list_filter = ("bed_type", "room__name")
    search_fields = ("name", "room__name")