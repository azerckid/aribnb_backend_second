from django.contrib import admin

from .models import Experience, Perk


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "start", "end", "created_at")
    search_fields = ("name", "address")
    list_filter = ("country", "city", "host", "category", "created_at")


@admin.register(Perk)
class PerkAdmin(admin.ModelAdmin):
    list_display = ("name", "details", "explanation")
    search_fields = ("name",)

