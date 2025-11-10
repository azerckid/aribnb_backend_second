from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from common.models import CommonModel


class Review(CommonModel):
    """Review from a user to a room or experience."""

    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
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

