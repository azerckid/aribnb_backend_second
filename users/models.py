from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model based on Django's default implementation."""

    first_name = models.CharField(
        max_length=150,
        editable=False,
        blank=True,
        default="",
    )
    last_name = models.CharField(
        max_length=150,
        editable=False,
        blank=True,
        default="",
    )
    name = models.CharField(max_length=150, default="")
    is_host = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.username
