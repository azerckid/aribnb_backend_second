from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from common.models import CommonModel
from django.conf import settings


class Review(CommonModel):
    """Review from a user to a room or experience."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    room = models.ForeignKey(
        "rooms.Room",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    experience = models.ForeignKey(
        "experiences.Experience",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    payload = models.TextField()
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    def __str__(self) -> str:
        target = self.room or self.experience
        return f"{self.user} → {target} ({self.rating}⭐️)"

