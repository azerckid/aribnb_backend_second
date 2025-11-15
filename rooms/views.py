from django.conf import settings
from django.utils import timezone
from django.db import transaction
import calendar
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.exceptions import (
    NotFound,
    ParseError,
    PermissionDenied,
)
from .models import Amenity, Room, Bed
from categories.models import Category
from bookings.models import Booking
from .serializers import (
    AmenitySerializer,
    RoomListSerializer,
    RoomDetailSerializer,
    BedSerializer,
)
from reviews.serializers import ReviewSerializer
from medias.serializers import PhotoSerializer
from bookings.serializers import (
    PublicBookingSerializer,
    CreateRoomBookingSerializer,
)

class Amenities(APIView):
    def get(self, request):
        all_amenities = Amenity.objects.all()
        serializer = AmenitySerializer(all_amenities, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AmenitySerializer(data=request.data)
        if serializer.is_valid():
            amenity = serializer.save()
            return Response(
                AmenitySerializer(amenity).data,
            )
        else:
            return Response(serializer.errors)

class AmenityDetail(APIView):
    def get_object(self, pk):
        try:
            return Amenity.objects.get(pk=pk)
        except Amenity.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        amenity = self.get_object(pk)
        serializer = AmenitySerializer(amenity)
        return Response(serializer.data)

    def put(self, request, pk):
        amenity = self.get_object(pk)
        serializer = AmenitySerializer(
            amenity,
            data=request.data,
            partial=True,
        )
        if serializer.is_valid():
            updated_amenity = serializer.save()
            return Response(
                AmenitySerializer(updated_amenity).data,
            )
        else:
            return Response(serializer.errors)

    def delete(self, request, pk):
        amenity = self.get_object(pk)
        amenity.delete()
        return Response(status=HTTP_204_NO_CONTENT)

class Rooms(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        all_rooms = Room.objects.all()
        serializer = RoomListSerializer(
            all_rooms,
            many=True,
            context={"request": request},
        )
        return Response(serializer.data)

    def post(self, request):
        serializer = RoomDetailSerializer(
            data=request.data,
            context={"request": request},
        )
        if serializer.is_valid():
            category_pk = request.data.get("category")
            if not category_pk:
                raise ParseError("Category is required.")
            try:
                category = Category.objects.get(pk=category_pk)
                if category.kind == Category.CategoryKindChoices.EXPERIENCES:
                    raise ParseError("The category kind should be 'rooms'")
            except Category.DoesNotExist:
                raise ParseError("Category not found")
            try:
                with transaction.atomic():
                    room = serializer.save(
                        owner=request.user,
                        category=category,
                    )
                    amenities = request.data.get("amenities")
                    for amenity_pk in amenities:
                        amenity = Amenity.objects.get(pk=amenity_pk)
                        room.amenities.add(amenity)
                    serializer = RoomDetailSerializer(
                        room,
                        context={"request": request},
                    )
                    return Response(serializer.data)
            except Exception:
                raise ParseError("Amenity not found")
        else:
            return Response(serializer.errors)

class RoomDetail(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_object(self, pk):
        try:
            return Room.objects.get(pk=pk)
        except Room.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        room = self.get_object(pk)
        serializer = RoomDetailSerializer(
            room,
            context={"request": request},
        )
        return Response(serializer.data)

    def put(self, request, pk):
        room = self.get_object(pk)
        if room.owner != request.user:
            raise PermissionDenied
        serializer = RoomDetailSerializer(
            room,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        if serializer.is_valid():
            category_pk = request.data.get("category")
            if category_pk:
                try:
                    category = Category.objects.get(pk=category_pk)
                    if category.kind == Category.CategoryKindChoices.EXPERIENCES:
                        raise ParseError("The category kind should be 'rooms'")
                except Category.DoesNotExist:
                    raise ParseError("Category not found")
            else:
                category = room.category
            try:
                with transaction.atomic():
                    room = serializer.save(
                        category=category,
                    )
                    amenities = request.data.get("amenities")
                    if amenities is not None:
                        room.amenities.clear()
                        for amenity_pk in amenities:
                            amenity = Amenity.objects.get(pk=amenity_pk)
                            room.amenities.add(amenity)
                    serializer = RoomDetailSerializer(
                        room,
                        context={"request": request},
                    )
                    return Response(serializer.data)
            except Exception:
                raise ParseError("Amenity not found")
        else:
            return Response(serializer.errors)

    def delete(self, request, pk):
        room = self.get_object(pk)
        if room.owner != request.user:
            raise PermissionDenied
        room.delete()
        return Response(status=HTTP_204_NO_CONTENT)

class RoomReviews(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try:
            return Room.objects.get(pk=pk)
        except Room.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        try:
            page = request.query_params.get("page", 1)
            page = int(page)
        except ValueError:
            page = 1
        page_size = settings.PAGE_SIZE
        start = (page - 1) * page_size
        end = start + page_size
        room = self.get_object(pk)
        serializer = ReviewSerializer(
            room.reviews.all()[start:end],
            many=True,
        )
        return Response(serializer.data)

    def post(self, request, pk):
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            review = serializer.save(
                user=request.user,
                room=self.get_object(pk),
            )
            serializer = ReviewSerializer(review)
            return Response(serializer.data)

class RoomPhotos(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try:
            return Room.objects.get(pk=pk)
        except Room.DoesNotExist:
            raise NotFound

    def post(self, request, pk):
        room = self.get_object(pk)
        if request.user != room.owner:
            raise PermissionDenied
        serializer = PhotoSerializer(data=request.data)
        if serializer.is_valid():
            photo = serializer.save(room=room)
            serializer = PhotoSerializer(photo)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)

class RoomBookings(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try:
            return Room.objects.get(pk=pk)
        except Room.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        room = self.get_object(pk)
        try:
            year = int(request.query_params.get("year", timezone.localdate().year))
            month = int(request.query_params.get("month", timezone.localdate().month))
        except ValueError:
            raise ParseError("year and month must be integers")
        if month < 1 or month > 12:
            raise ParseError("month must be between 1 and 12")
        _, last_day = calendar.monthrange(year, month)
        start_date = timezone.datetime(year, month, 1).date()
        end_date = timezone.datetime(year, month, last_day).date()
        bookings = Booking.objects.filter(
            room=room,
            kind=Booking.BookingKindChoices.ROOM,
            check_in__gte=start_date,
            check_in__lte=end_date,
        ).order_by("check_in")
        try:
            page = int(request.query_params.get("page", 1))
            if page < 1:
                raise ValueError
        except ValueError:
            raise ParseError("page must be a positive integer")
        page_size = settings.PAGE_SIZE
        start = (page - 1) * page_size
        end = start + page_size
        serializer = PublicBookingSerializer(
            bookings[start:end],
            many=True,
        )
        return Response(serializer.data)

    def post(self, request, pk):
        room = self.get_object(pk)
        serializer = CreateRoomBookingSerializer(data=request.data)
        if serializer.is_valid():
            check_in = serializer.validated_data["check_in"]
            check_out = serializer.validated_data["check_out"]
            existing = Booking.objects.filter(
                room=room,
                kind=Booking.BookingKindChoices.ROOM,
                check_in__lt=check_out,
                check_out__gt=check_in,
            ).exists()
            if existing:
                raise ParseError("Those dates are already booked.")
            bed_conflict = Booking.objects.filter(
                bed__room=room,
                kind=Booking.BookingKindChoices.BED,
                check_in__lt=check_out,
                check_out__gt=check_in,
            ).exists()
            if bed_conflict:
                raise ParseError("Some beds are already booked during those dates.")
            booking = serializer.save(
                room=room,
                user=request.user,
                kind=Booking.BookingKindChoices.ROOM,
            )
            return Response(
                PublicBookingSerializer(booking).data,
                status=201,
            )
        return Response(serializer.errors)

class RoomBeds(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_room(self, pk):
        try:
            return Room.objects.get(pk=pk)
        except Room.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        room = self.get_room(pk)
        beds = room.beds.all()
        bed_type = request.query_params.get("type")
        if bed_type:
            beds = beds.filter(bed_type=bed_type)
        serializer = BedSerializer(
            beds,
            many=True,
        )
        return Response(serializer.data)

    def post(self, request, pk):
        room = self.get_room(pk)
        if room.owner != request.user:
            raise PermissionDenied
        serializer = BedSerializer(data=request.data)
        if serializer.is_valid():
            bed = serializer.save(room=room)
            return Response(
                BedSerializer(bed).data,
                status=201,
            )
        return Response(serializer.errors)

class BedDetail(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, room_pk, bed_pk):
        try:
            return Bed.objects.get(pk=bed_pk, room_id=room_pk)
        except Bed.DoesNotExist:
            raise NotFound

    def get(self, request, pk, bed_pk):
        bed = self.get_object(pk, bed_pk)
        serializer = BedSerializer(bed)
        return Response(serializer.data)

    def put(self, request, pk, bed_pk):
        bed = self.get_object(pk, bed_pk)
        if bed.room.owner != request.user:
            raise PermissionDenied
        serializer = BedSerializer(
            bed,
            data=request.data,
            partial=True,
        )
        if serializer.is_valid():
            updated = serializer.save()
            return Response(BedSerializer(updated).data)
        return Response(serializer.errors)

    def delete(self, request, pk, bed_pk):
        bed = self.get_object(pk, bed_pk)
        if bed.room.owner != request.user:
            raise PermissionDenied
        bed.delete()
        return Response(status=HTTP_204_NO_CONTENT)

class BedBookings(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_bed(self, room_pk, bed_pk):
        try:
            return Bed.objects.get(pk=bed_pk, room_id=room_pk)
        except Bed.DoesNotExist:
            raise NotFound

    def get(self, request, pk, bed_pk):
        bed = self.get_bed(pk, bed_pk)
        try:
            year = int(request.query_params.get("year", timezone.localdate().year))
            month = int(request.query_params.get("month", timezone.localdate().month))
        except ValueError:
            raise ParseError("year and month must be integers")
        if month < 1 or month > 12:
            raise ParseError("month must be between 1 and 12")
        _, last_day = calendar.monthrange(year, month)
        start_date = timezone.datetime(year, month, 1).date()
        end_date = timezone.datetime(year, month, last_day).date()
        bookings = Booking.objects.filter(
            bed=bed,
            kind=Booking.BookingKindChoices.BED,
            check_in__gte=start_date,
            check_in__lte=end_date,
        ).order_by("check_in")
        try:
            page = int(request.query_params.get("page", 1))
            if page < 1:
                raise ValueError
        except ValueError:
            raise ParseError("page must be a positive integer")
        page_size = settings.PAGE_SIZE
        start = (page - 1) * page_size
        end = start + page_size
        serializer = PublicBookingSerializer(
            bookings[start:end],
            many=True,
        )
        return Response(serializer.data)

    def post(self, request, pk, bed_pk):
        bed = self.get_bed(pk, bed_pk)
        serializer = CreateRoomBookingSerializer(data=request.data)
        if serializer.is_valid():
            check_in = serializer.validated_data["check_in"]
            check_out = serializer.validated_data["check_out"]
            guests = serializer.validated_data["guests"]
            if guests > bed.capacity:
                raise ParseError("Guest count exceeds bed capacity.")
            room_conflict = Booking.objects.filter(
                room=bed.room,
                kind=Booking.BookingKindChoices.ROOM,
                check_in__lt=check_out,
                check_out__gt=check_in,
            ).exists()
            if room_conflict:
                raise ParseError("The whole room is booked for those dates.")
            bed_conflict = Booking.objects.filter(
                bed=bed,
                kind=Booking.BookingKindChoices.BED,
                check_in__lt=check_out,
                check_out__gt=check_in,
            ).exists()
            if bed_conflict:
                raise ParseError("This bed is already booked for those dates.")
            booking = serializer.save(
                bed=bed,
                room=bed.room,
                user=request.user,
                kind=Booking.BookingKindChoices.BED,
            )
            return Response(
                PublicBookingSerializer(booking).data,
                status=201,
            )
        return Response(serializer.errors)
