from django.contrib import admin

from .models import Review


class WordFilter(admin.SimpleListFilter):
    title = "Filter by words!"
    parameter_name = "word"

    def lookups(self, request, model_admin):
        return [
            ("good", "Good"),
            ("great", "Great"),
            ("awesome", "Awesome"),
        ]

    def queryset(self, request, reviews):
        word = self.value()
        if word:
            return reviews.filter(payload__contains=word)
        return reviews


class RatingQualityFilter(admin.SimpleListFilter):
    title = "Review quality"
    parameter_name = "quality"

    def lookups(self, request, model_admin):
        return [
            ("good", "Good (≥ 3★)"),
            ("bad", "Bad (< 3★)"),
        ]

    def queryset(self, request, reviews):
        quality = self.value()
        if quality == "good":
            return reviews.filter(rating__gte=3)
        if quality == "bad":
            return reviews.filter(rating__lt=3)
        return reviews


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("__str__", "rating", "payload", "created_at")
    list_filter = (
        WordFilter,
        RatingQualityFilter,
        "rating",
        "user__is_host",
        "room__category",
        "room__pet_friendly",
        "created_at",
    )
    search_fields = ("user__username", "room__name", "experience__name")
 
