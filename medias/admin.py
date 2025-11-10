from django.contrib import admin

from .models import Photo, Video


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ("__str__", "created_at", "updated_at")
    search_fields = ("description", "room__name", "experience__name")


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ("__str__", "created_at", "updated_at")
    search_fields = ("experience__name",)

