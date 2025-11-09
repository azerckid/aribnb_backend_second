from django.db import models

# Create your models here.
class House(models.Model):
    """
    House model
    """

    name = models.CharField(max_length=140)
    description = models.TextField()
    price_per_night = models.PositiveIntegerField(
        verbose_name="Price per night",
        help_text="Positive numbers only",
    )
    pets_allowed = models.BooleanField(
        verbose_name="Pets allowed?",
        default=True,
        help_text="Does this house allow pets?",
    )
    address = models.CharField(max_length=140)
    latitude = models.FloatField()
    longitude = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name