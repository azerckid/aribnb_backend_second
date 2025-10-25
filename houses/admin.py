from django.contrib import admin
from .models import House

# Register your models here.
@admin.register(House)
class HouseAdmin(admin.ModelAdmin):
    
    list_display = ('name', 'price_per_night', 'pet_friendly', 'address', 'latitude', 'longitude')
    list_filter = ('pet_friendly',)
    search_fields = ('name', 'address')
    ordering = ('-price_per_night',)
    list_per_page = 10
    list_display_links = ('name', 'price_per_night')
   