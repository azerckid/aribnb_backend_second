from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Custom user model based on Django's default implementation."""

    def __str__(self) -> str:
        return self.username
