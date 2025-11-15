from django.urls import path

from .views import (
    Wishlists,
    WishlistDetail,
    WishlistToggle,
    WishlistExperienceToggle,
)


urlpatterns = [
    path("", Wishlists.as_view()),
    path("<int:pk>", WishlistDetail.as_view()),
    path("<int:pk>/rooms/<int:room_pk>", WishlistToggle.as_view()),
    path(
        "<int:pk>/experiences/<int:experience_pk>",
        WishlistExperienceToggle.as_view(),
    ),
]

