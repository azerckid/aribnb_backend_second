from django.utils import timezone
from datetime import timedelta
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

    def validate(self, data):
        check_in = data["check_in"]
        check_out = data["check_out"]
        if check_out <= check_in:
            raise serializers.ValidationError(
                "Check out must be after check in."
            )
        room = self.context.get("room")
        bed = self.context.get("bed")
        if room:
            overlaps = Booking.objects.filter(
                room=room,
                kind=Booking.BookingKindChoices.ROOM,
                check_in__lt=check_out,
                check_out__gt=check_in,
            ).exists()
            if overlaps:
                raise serializers.ValidationError(
                    "Those dates are already taken for this room."
                )
            if bed:
                room_full = Booking.objects.filter(
                    room=room,
                    kind=Booking.BookingKindChoices.ROOM,
                    check_in__lt=check_out,
                    check_out__gt=check_in,
                ).exists()
                if room_full:
                    raise serializers.ValidationError(
                        "The whole room is booked for those dates."
                    )
                bed_conflict = Booking.objects.filter(
                    bed=bed,
                    kind=Booking.BookingKindChoices.BED,
                    check_in__lt=check_out,
                    check_out__gt=check_in,
                ).exists()
                if bed_conflict:
                    raise serializers.ValidationError(
                        "This bed is already booked for those dates."
                    )
        return data

class CreateExperienceBookingSerializer(serializers.ModelSerializer):

    experience_time = serializers.DateTimeField()

    class Meta:
        model = Booking
        fields = (
            "experience_time",
            "guests",
        )

    def validate_experience_time(self, value):
        now = timezone.now()
        if value <= now:
            raise serializers.ValidationError("Can't book in the past!")
        return value

    def validate(self, data):
        experience = self.context.get("experience")
        if not experience:
            raise serializers.ValidationError("Experience context is required.")
        experience_time = data.get("experience_time")
        if experience_time:
            duration_minutes = getattr(experience, "duration", 60)
            slot_end = experience_time + timedelta(minutes=duration_minutes)
            # ensure slot within experience schedule
            start_time = experience_time.time()
            end_time = slot_end.time()
            if start_time < experience.start or start_time >= experience.end:
                raise serializers.ValidationError("Start time outside experience schedule.")
            if slot_end.date() != experience_time.date() or end_time > experience.end:
                raise serializers.ValidationError("Slot exceeds available schedule.")
            conflicts = Booking.objects.filter(
                experience=experience,
                kind=Booking.BookingKindChoices.EXPERIENCE,
                experience_time__lt=slot_end,
                experience_end__gt=experience_time,
            ).exists()
            if conflicts:
                raise serializers.ValidationError("This slot is already booked.")
        return data


class PublicBookingSerializer(serializers.ModelSerializer):

    price = serializers.SerializerMethodField()
    bed = serializers.SerializerMethodField()
    experience_end = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Booking
        fields = (
            "pk",
            "check_in",
            "check_out",
            "experience_time",
            "experience_end",
            "guests",
            "bed",
            "price",
        )

    def get_price(self, booking):
        if booking.room:
            return booking.room.price
        if booking.experience:
            return booking.experience.price
        return None

    def get_bed(self, booking):
        if not booking.bed:
            return None
        return {
            "pk": booking.bed.pk,
            "name": booking.bed.name,
            "bed_type": booking.bed.bed_type,
            "room": booking.bed.room.pk,
        }

