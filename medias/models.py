from django.db import models

from common.models import CommonModel


class Photo(CommonModel):
    """Photo files for rooms or experiences."""

    file = models.URLField()
    description = models.CharField(max_length=140)
    room = models.ForeignKey(
        "rooms.Room",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="photos",
    )
    experience = models.ForeignKey(
        "experiences.Experience",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="photos",
    )

    def __str__(self) -> str:
        target = self.room or self.experience
        return f"Photo for {target}"


class Video(CommonModel):
    """Video files for experiences."""

    file = models.URLField()
    experience = models.OneToOneField(
        "experiences.Experience",
        on_delete=models.CASCADE,
        related_name="videos",
    )

    def __str__(self) -> str:
        return f"Video for {self.experience}"

