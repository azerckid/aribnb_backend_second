from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model based on Django's default implementation."""

    class GenderChoices(models.TextChoices):
        MALE = ("male", "Male")
        FEMALE = ("female", "Female")

    class LanguageChoices(models.TextChoices):
        KR = ("kr", "Korean")
        EN = ("en", "English")

    class CurrencyChoices(models.TextChoices):
        WON = "won", "Korean Won"
        USD = "usd", "Dollar"

    first_name = models.CharField(max_length=150, editable=False, blank=True, default="")
    last_name = models.CharField(max_length=150, editable=False, blank=True, default="")
    avatar = models.ImageField(blank=True, null=True)
    name = models.CharField(max_length=150, default="")
    is_host = models.BooleanField(default=False)
    gender = models.CharField(
        max_length=10,
        choices=GenderChoices.choices,
        blank=True,
        default=GenderChoices.MALE,
    )
    language = models.CharField(
        max_length=2,
        choices=LanguageChoices.choices,
        blank=True,
        default=LanguageChoices.KR,
    )
    currency = models.CharField(
        max_length=5,
        choices=CurrencyChoices.choices,
        blank=True,
        default=CurrencyChoices.WON,
    )


    def __str__(self) -> str:
        return self.username
