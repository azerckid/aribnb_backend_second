from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import calendar
from rest_framework.views import APIView
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.exceptions import (
    NotFound,
    ParseError,
    PermissionDenied,
    NotAuthenticated,
)

from bookings.models import Booking
from bookings.serializers import (
    PublicBookingSerializer,
    CreateExperienceBookingSerializer,
)
from .models import Experience, Perk
from . import serializers
from reviews.models import Review
from reviews.serializers import ReviewSerializer


class Perks(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        all_perks = Perk.objects.all()
        serializer = serializers.PerkSerializer(all_perks, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = serializers.PerkSerializer(data=request.data)
        if serializer.is_valid():
            perk = serializer.save()
            return Response(
                serializers.PerkSerializer(perk).data,
                status=201,
            )
        return Response(serializer.errors, status=400)


class PerkDetail(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try:
            return Perk.objects.get(pk=pk)
        except Perk.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        perk = self.get_object(pk)
        serializer = serializers.PerkSerializer(perk)
        return Response(serializer.data)

    def put(self, request, pk):
        perk = self.get_object(pk)
        serializer = serializers.PerkSerializer(
            perk,
            data=request.data,
            partial=True,
        )
        if serializer.is_valid():
            updated_perk = serializer.save()
            return Response(
                serializers.PerkSerializer(updated_perk).data,
            )
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        perk = self.get_object(pk)
        perk.delete()
        return Response(status=HTTP_204_NO_CONTENT)


class Experiences(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        experiences = Experience.objects.all()
        serializer = serializers.ExperienceListSerializer(experiences, many=True)
        return Response(serializer.data)

    def post(self, request):
        if not request.user.is_authenticated:
            raise NotAuthenticated
        if not request.user.is_host:
            raise PermissionDenied("Only hosts can create experiences.")
        serializer = serializers.ExperienceCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            category = serializer.validated_data.get("category")
            if category and category.kind != category.CategoryKindChoices.EXPERIENCES:
                raise ParseError("The category kind should be 'experiences'.")
            experience = serializer.save(host=request.user)
            return Response(
                serializers.ExperienceDetailSerializer(experience).data,
                status=201,
            )
        return Response(serializer.errors, status=400)


class ExperienceDetail(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try:
            return Experience.objects.get(pk=pk)
        except Experience.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        experience = self.get_object(pk)
        serializer = serializers.ExperienceDetailSerializer(experience)
        return Response(serializer.data)

    def put(self, request, pk):
        experience = self.get_object(pk)
        if experience.host != request.user:
            raise PermissionDenied
        serializer = serializers.ExperienceCreateUpdateSerializer(
            experience,
            data=request.data,
            partial=True,
        )
        if serializer.is_valid():
            category = serializer.validated_data.get("category")
            if category and category.kind != category.CategoryKindChoices.EXPERIENCES:
                raise ParseError("The category kind should be 'experiences'.")
            updated = serializer.save()
            return Response(
                serializers.ExperienceDetailSerializer(updated).data,
            )
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        experience = self.get_object(pk)
        if experience.host != request.user:
            raise PermissionDenied
        experience.delete()
        return Response(status=HTTP_204_NO_CONTENT)


class ExperiencePerks(APIView):

    def get(self, request, pk):
        try:
            experience = Experience.objects.get(pk=pk)
        except Experience.DoesNotExist:
            raise NotFound
        serializer = serializers.PerkSerializer(
            experience.perks.all(),
            many=True,
        )
        return Response(serializer.data)


class ExperienceReviews(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_experience(self, pk):
        try:
            return Experience.objects.get(pk=pk)
        except Experience.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        experience = self.get_experience(pk)
        reviews = Review.objects.filter(
            experience=experience,
        ).select_related("user")
        try:
            page = int(request.query_params.get("page", 1))
            if page < 1:
                raise ValueError
        except ValueError:
            raise ParseError("page must be a positive integer.")
        page_size = getattr(settings, "PAGE_SIZE", 3)
        start = (page - 1) * page_size
        end = start + page_size
        serializer = ReviewSerializer(
            reviews[start:end],
            many=True,
        )
        return Response(serializer.data)

    def post(self, request, pk):
        if not request.user.is_authenticated:
            raise NotAuthenticated
        experience = self.get_experience(pk)
        has_booking = Booking.objects.filter(
            user=request.user,
            experience=experience,
            kind=Booking.BookingKindChoices.EXPERIENCE,
        ).exists()
        if not has_booking:
            raise PermissionDenied("You can review experiences only after booking.")
        already = Review.objects.filter(
            user=request.user,
            experience=experience,
        ).exists()
        if already:
            raise ParseError("You have already reviewed this experience.")
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            review = serializer.save(
                user=request.user,
                experience=experience,
            )
            return Response(
                ReviewSerializer(review).data,
                status=201,
            )
        return Response(serializer.errors, status=400)


class ExperienceBookings(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try:
            return Experience.objects.get(pk=pk)
        except Experience.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        experience = self.get_object(pk)
        try:
            year = int(request.query_params.get("year", timezone.localdate().year))
            month = int(request.query_params.get("month", timezone.localdate().month))
        except ValueError:
            raise ParseError("year and month must be integers.")
        if month < 1 or month > 12:
            raise ParseError("month must be between 1 and 12.")
        _, last_day = calendar.monthrange(year, month)
        start_date = timezone.datetime(year, month, 1).date()
        end_date = timezone.datetime(year, month, last_day).date()
        bookings = Booking.objects.filter(
            experience=experience,
            kind=Booking.BookingKindChoices.EXPERIENCE,
            experience_time__date__gte=start_date,
            experience_time__date__lte=end_date,
        ).order_by("experience_time")
        try:
            page = int(request.query_params.get("page", 1))
            if page < 1:
                raise ValueError
        except ValueError:
            raise ParseError("page must be a positive integer.")
        page_size = getattr(settings, "PAGE_SIZE", 3)
        start = (page - 1) * page_size
        end = start + page_size
        serializer = PublicBookingSerializer(
            bookings[start:end],
            many=True,
        )
        return Response(serializer.data)

    def post(self, request, pk):
        if not request.user.is_authenticated:
            raise NotAuthenticated
        experience = self.get_object(pk)
        if experience.host == request.user:
            raise PermissionDenied("Hosts cannot book their own experiences.")
        serializer = CreateExperienceBookingSerializer(
            data=request.data,
            context={"experience": experience},
        )
        if serializer.is_valid():
            duration_minutes = experience.duration
            start_time = serializer.validated_data["experience_time"]
            slot_end = start_time + timedelta(minutes=duration_minutes)
            booking = serializer.save(
                experience=experience,
                user=request.user,
                kind=Booking.BookingKindChoices.EXPERIENCE,
                experience_end=slot_end,
            )
            return Response(
                PublicBookingSerializer(booking).data,
                status=201,
            )
        return Response(serializer.errors, status=400)


class ExperienceBookingDetail(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, experience_pk, booking_pk):
        try:
            return Booking.objects.get(
                pk=booking_pk,
                experience_id=experience_pk,
                kind=Booking.BookingKindChoices.EXPERIENCE,
            )
        except Booking.DoesNotExist:
            raise NotFound

    def get(self, request, pk, booking_pk):
        booking = self.get_object(pk, booking_pk)
        serializer = PublicBookingSerializer(booking)
        return Response(serializer.data)

    def put(self, request, pk, booking_pk):
        booking = self.get_object(pk, booking_pk)
        if booking.user != request.user:
            raise PermissionDenied
        serializer = CreateExperienceBookingSerializer(
            booking,
            data=request.data,
            context={"experience": booking.experience},
            partial=True,
        )
        if serializer.is_valid():
            new_start = serializer.validated_data.get(
                "experience_time",
                booking.experience_time,
            )
            duration_minutes = booking.experience.duration
            slot_end = new_start + timedelta(minutes=duration_minutes)
            updated = serializer.save(experience_end=slot_end)
            return Response(PublicBookingSerializer(updated).data)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk, booking_pk):
        booking = self.get_object(pk, booking_pk)
        if booking.user != request.user and booking.experience.host != request.user:
            raise PermissionDenied
        booking.delete()
        return Response(status=HTTP_204_NO_CONTENT)

