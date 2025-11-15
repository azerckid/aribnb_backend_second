from rest_framework import serializers

from .models import User
from bookings.models import Booking


class TinyUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "name",
            "avatar",
            "username",
        )


class PrivateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = (
            "password",
            "is_superuser",
            "id",
            "is_staff",
            "is_active",
            "first_name",
            "last_name",
            "groups",
            "user_permissions",
        )


class UserProfileSerializer(PrivateUserSerializer):

    reviews = serializers.SerializerMethodField()
    visited_cities = serializers.SerializerMethodField()

    class Meta(PrivateUserSerializer.Meta):
        exclude = PrivateUserSerializer.Meta.exclude

    def get_visited_cities(self, user):
        if not hasattr(user, "bookings"):
            bookings = Booking.objects.filter(user=user).select_related(
                "room",
                "experience",
            )
        else:
            bookings = user.bookings.all()
        cities = []
        seen = set()
        for booking in bookings:
            destination = None
            if booking.room and booking.room.city:
                destination = booking.room.city
            elif booking.experience and booking.experience.city:
                destination = booking.experience.city
            if destination and destination not in seen:
                seen.add(destination)
                cities.append(destination)
        return cities

    def get_reviews(self, user):
        from reviews.serializers import ReviewSerializer

        reviews = user.reviews.all()
        serializer = ReviewSerializer(reviews, many=True)
        return serializer.data

