from rest_framework import serializers

from .models import Booking


class PublicBookingSerializer(serializers.ModelSerializer):

    price = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = (
            "pk",
            "check_in",
            "check_out",
            "experience_time",
            "guests",
            "price",
        )

    def get_price(self, booking):
        if booking.room:
            return booking.room.price
        if booking.experience:
            return booking.experience.price
        return None

