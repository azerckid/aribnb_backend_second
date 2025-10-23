from django.db import models

# Create your models here.
class House(models.Model):
    """
    House model
    """
    name = models.CharField(max_length=255)
    description = models.TextField()
    price_per_night = models.PositiveIntegerField()
    pet_friendly = models.BooleanField(default=True)
    address = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)