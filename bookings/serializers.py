from django.utils import timezone
from rest_framework import serializers

from .models import Booking


class CreateRoomBookingSerializer(serializers.ModelSerializer):

    check_in = serializers.DateField()
    check_out = serializers.DateField()

    class Meta:
        model = Booking
        fields = (
            "check_in",
            "check_out",
            "guests",
        )

    def validate_check_in(self, value):
        now = timezone.localdate()
        if value < now:
            raise serializers.ValidationError("Can't book in the past!")
        return value

    def validate_check_out(self, value):
        now = timezone.localdate()
        if value < now:
            raise serializers.ValidationError("Can't book in the past!")
        return value


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

