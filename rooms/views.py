from django.conf import settings
from django.utils import timezone
from django.db import transaction
import calendar
from datetime import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import (
    NotFound,
    ParseError,
    PermissionDenied,
)
from config.authentication import NoCSRFSessionAuthentication, JWTAuthentication
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
from reviews.models import Review
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
    authentication_classes = [NoCSRFSessionAuthentication, TokenAuthentication, JWTAuthentication]

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
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception:
                raise ParseError("Amenity not found")
        else:
            return Response(serializer.errors)

class RoomDetail(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly]
    authentication_classes = [NoCSRFSessionAuthentication, TokenAuthentication, JWTAuthentication]
    
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
    authentication_classes = [NoCSRFSessionAuthentication, TokenAuthentication, JWTAuthentication]

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
        else:
            return Response(serializer.errors)

class ReviewReply(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly]
    authentication_classes = [NoCSRFSessionAuthentication, TokenAuthentication, JWTAuthentication]

    def get_room(self, pk):
        try:
            return Room.objects.get(pk=pk)
        except Room.DoesNotExist:
            raise NotFound

    def get_review(self, review_pk, room):
        try:
            review = Review.objects.get(pk=review_pk, room=room)
            return review
        except Review.DoesNotExist:
            raise NotFound

    def post(self, request, pk, review_pk):
        room = self.get_room(pk)
        review = self.get_review(review_pk, room)
        
        reply_text = request.data.get("reply")
        if not reply_text:
            raise ParseError("reply is required.")
        
        review.reply = reply_text
        review.reply_user = request.user
        review.reply_created_at = timezone.now()
        review.save()
        
        serializer = ReviewSerializer(review)
        return Response(serializer.data)

class RoomPhotos(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly]
    authentication_classes = [NoCSRFSessionAuthentication, TokenAuthentication, JWTAuthentication]

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
    authentication_classes = [NoCSRFSessionAuthentication, TokenAuthentication, JWTAuthentication]

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
        serializer = CreateRoomBookingSerializer(
            data=request.data,
            context={"room": room},
        )
        if serializer.is_valid():
            check_in = serializer.validated_data["check_in"]
            check_out = serializer.validated_data["check_out"]
            guests = serializer.validated_data.get("guests", 1)
            
            # Calculate total booked guests during the date range
            # Count both ROOM and BED bookings that overlap with the requested dates
            overlapping_room_bookings = Booking.objects.filter(
                room=room,
                kind=Booking.BookingKindChoices.ROOM,
                check_in__lt=check_out,
                check_out__gt=check_in,
            )
            overlapping_bed_bookings = Booking.objects.filter(
                bed__room=room,
                kind=Booking.BookingKindChoices.BED,
                check_in__lt=check_out,
                check_out__gt=check_in,
            )
            # Sum guests from both room and bed bookings
            total_booked_guests = (
                sum(booking.guests for booking in overlapping_room_bookings) +
                sum(booking.guests for booking in overlapping_bed_bookings)
            )
            
            # Calculate room capacity from number of beds
            bed_count = room.bed_list.count()
            room_capacity = bed_count if bed_count > 0 else room.beds
            
            if room_capacity == 0:
                return Response(
                    {
                        "error": "NO_BEDS_CONFIGURED",
                        "message": "Room has no beds configured.",
                        "details": {}
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check if requested guests + already booked guests exceed capacity
            if total_booked_guests + guests > room_capacity:
                available_beds = room_capacity - total_booked_guests
                return Response(
                    {
                        "error": "INSUFFICIENT_BEDS",
                        "message": f"Not enough beds available. Requested {guests} guest(s), but only {available_beds} bed(s) available during those dates.",
                        "details": {
                            "requested_guests": guests,
                            "total_booked_guests": total_booked_guests,
                            "room_capacity": room_capacity,
                            "available_beds": available_beds,
                            "check_in": check_in.strftime("%Y-%m-%d"),
                            "check_out": check_out.strftime("%Y-%m-%d"),
                        }
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
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
    authentication_classes = [NoCSRFSessionAuthentication, TokenAuthentication, JWTAuthentication]

    def get_room(self, pk):
        try:
            return Room.objects.get(pk=pk)
        except Room.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        room = self.get_room(pk)
        beds = room.bed_list.all()
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
    authentication_classes = [NoCSRFSessionAuthentication, TokenAuthentication, JWTAuthentication]

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
    authentication_classes = [NoCSRFSessionAuthentication, TokenAuthentication, JWTAuthentication]

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
        serializer = CreateRoomBookingSerializer(
            data=request.data,
            context={
                "room": bed.room,
                "bed": bed,
            },
        )
        if serializer.is_valid():
            check_in = serializer.validated_data["check_in"]
            check_out = serializer.validated_data["check_out"]
            guests = serializer.validated_data["guests"]
            # Each bed can only accommodate 1 guest
            if guests > 1:
                raise ParseError("Each bed can only accommodate 1 guest.")
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

class RoomBookingsCheck(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_room(self, pk):
        try:
            return Room.objects.get(pk=pk)
        except Room.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        room = self.get_room(pk)
        check_in = request.query_params.get("check_in")
        check_out = request.query_params.get("check_out")
        guests = request.query_params.get("guests")
        
        # Check date conflicts if dates are provided
        if check_in and check_out:
            try:
                check_in_date = datetime.strptime(check_in, "%Y-%m-%d").date()
                check_out_date = datetime.strptime(check_out, "%Y-%m-%d").date()
                if check_out_date <= check_in_date:
                    return Response(
                        {
                            "available": False,
                            "reason": "INVALID_DATES",
                            "message": "Check out must be after check in.",
                            "details": {
                                "check_in": check_in,
                                "check_out": check_out,
                            }
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Calculate total booked guests during the date range
                # Count both ROOM and BED bookings that overlap with the requested dates
                overlapping_room_bookings = Booking.objects.filter(
                    room=room,
                    kind=Booking.BookingKindChoices.ROOM,
                    check_in__lt=check_out_date,
                    check_out__gt=check_in_date,
                )
                overlapping_bed_bookings = Booking.objects.filter(
                    bed__room=room,
                    kind=Booking.BookingKindChoices.BED,
                    check_in__lt=check_out_date,
                    check_out__gt=check_in_date,
                )
                # Sum guests from both room and bed bookings
                total_booked_guests = (
                    sum(booking.guests for booking in overlapping_room_bookings) +
                    sum(booking.guests for booking in overlapping_bed_bookings)
                )
                
                # Calculate room capacity from number of beds
                bed_count = room.bed_list.count()
                room_capacity = bed_count if bed_count > 0 else room.beds
                
                if room_capacity > 0:
                    # Get requested guests (default to 1)
                    requested_guests = int(guests) if guests else 1
                    
                    # Check if requested guests + already booked guests exceed capacity
                    if total_booked_guests + requested_guests > room_capacity:
                        available_beds = room_capacity - total_booked_guests
                        return Response(
                            {
                                "available": False,
                                "reason": "INSUFFICIENT_BEDS",
                                "message": f"Not enough beds available. Requested {requested_guests} guest(s), but only {available_beds} bed(s) available during those dates.",
                                "details": {
                                    "requested_guests": requested_guests,
                                    "total_booked_guests": total_booked_guests,
                                    "room_capacity": room_capacity,
                                    "available_beds": available_beds,
                                    "check_in": check_in,
                                    "check_out": check_out,
                                }
                            },
                            status=status.HTTP_400_BAD_REQUEST
                        )
            except ValueError as e:
                return Response(
                    {
                        "available": False,
                        "reason": "INVALID_DATE_FORMAT",
                        "message": "Invalid date format. Use YYYY-MM-DD.",
                        "details": {
                            "check_in": check_in,
                            "check_out": check_out,
                        }
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Check guest capacity (default to 1 if not provided)
        if guests:
            try:
                guests = int(guests)
            except ValueError:
                return Response(
                    {
                        "available": False,
                        "reason": "INVALID_GUESTS",
                        "message": "guests must be an integer.",
                        "details": {
                            "guests": guests,
                        }
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            guests = 1  # Default to 1 guest if not provided
        
        # Calculate room capacity from number of beds (each bed accommodates 1 guest)
        bed_count = room.bed_list.count()
        # Debug: Check both bed_list and room.beds field
        if bed_count == 0:
            # Try using room.beds field as fallback
            if room.beds > 0:
                room_capacity = room.beds
            else:
                return Response(
                    {
                        "available": False,
                        "reason": "NO_BEDS_CONFIGURED",
                        "message": f"Room has no beds configured.",
                        "details": {
                            "bed_list_count": bed_count,
                            "room_beds_field": room.beds,
                        }
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            room_capacity = bed_count
        if guests > room_capacity:
            return Response(
                {
                    "available": False,
                    "reason": "EXCEEDS_CAPACITY",
                    "message": f"Guest count ({guests}) exceeds room capacity ({room_capacity}).",
                    "details": {
                        "requested_guests": guests,
                        "room_capacity": room_capacity,
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(
            {"available": True, "message": "Booking is available for the specified dates and guests."},
            status=status.HTTP_200_OK
        )

class RoomBookingStatus(APIView):
    """Get booking status for a date range - returns detailed booking information."""
    
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_room(self, pk):
        try:
            return Room.objects.get(pk=pk)
        except Room.DoesNotExist:
            raise NotFound
    
    def get(self, request, pk):
        room = self.get_room(pk)
        check_in = request.query_params.get("check_in")
        check_out = request.query_params.get("check_out")
        
        if not check_in or not check_out:
            return Response(
                {
                    "error": "MISSING_PARAMETERS",
                    "message": "check_in and check_out parameters are required.",
                    "details": {}
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            check_in_date = datetime.strptime(check_in, "%Y-%m-%d").date()
            check_out_date = datetime.strptime(check_out, "%Y-%m-%d").date()
            if check_out_date <= check_in_date:
                return Response(
                    {
                        "error": "INVALID_DATES",
                        "message": "Check out must be after check in.",
                        "details": {
                            "check_in": check_in,
                            "check_out": check_out,
                        }
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        except ValueError:
            return Response(
                {
                    "error": "INVALID_DATE_FORMAT",
                    "message": "Invalid date format. Use YYYY-MM-DD.",
                    "details": {
                        "check_in": check_in,
                        "check_out": check_out,
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Calculate room capacity
        bed_count = room.bed_list.count()
        room_capacity = bed_count if bed_count > 0 else room.beds
        
        # Get all bookings that overlap with the requested date range
        overlapping_room_bookings = Booking.objects.filter(
            room=room,
            kind=Booking.BookingKindChoices.ROOM,
            check_in__lt=check_out_date,
            check_out__gt=check_in_date,
        )
        overlapping_bed_bookings = Booking.objects.filter(
            bed__room=room,
            kind=Booking.BookingKindChoices.BED,
            check_in__lt=check_out_date,
            check_out__gt=check_in_date,
        )
        
        # Calculate total booked guests
        total_booked_guests = (
            sum(booking.guests for booking in overlapping_room_bookings) +
            sum(booking.guests for booking in overlapping_bed_bookings)
        )
        
        # Calculate available beds
        available_beds = max(0, room_capacity - total_booked_guests)
        
        # Serialize bookings for frontend display
        room_bookings_serializer = PublicBookingSerializer(
            overlapping_room_bookings, many=True
        )
        bed_bookings_serializer = PublicBookingSerializer(
            overlapping_bed_bookings, many=True
        )
        
        return Response(
            {
                "room_id": room.pk,
                "room_name": room.name,
                "check_in": check_in,
                "check_out": check_out,
                "room_capacity": room_capacity,
                "total_booked_guests": total_booked_guests,
                "available_beds": available_beds,
                "bookings": {
                    "room_bookings": room_bookings_serializer.data,
                    "bed_bookings": bed_bookings_serializer.data,
                },
                "summary": {
                    "total_bookings": overlapping_room_bookings.count() + overlapping_bed_bookings.count(),
                    "occupancy_rate": round((total_booked_guests / room_capacity * 100) if room_capacity > 0 else 0, 2),
                }
            },
            status=status.HTTP_200_OK
        )

class BedBookingsCheck(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_bed(self, room_pk, bed_pk):
        try:
            return Bed.objects.get(pk=bed_pk, room_id=room_pk)
        except Bed.DoesNotExist:
            raise NotFound

    def get(self, request, pk, bed_pk):
        bed = self.get_bed(pk, bed_pk)
        check_in = request.query_params.get("check_in")
        check_out = request.query_params.get("check_out")
        guests = request.query_params.get("guests")
        
        # Check date conflicts if dates are provided
        if check_in and check_out:
            try:
                check_in_date = datetime.strptime(check_in, "%Y-%m-%d").date()
                check_out_date = datetime.strptime(check_out, "%Y-%m-%d").date()
                if check_out_date <= check_in_date:
                    raise ParseError("Check out must be after check in.")
                
                # Check if the whole room is booked
                room_conflict = Booking.objects.filter(
                    room=bed.room,
                    kind=Booking.BookingKindChoices.ROOM,
                    check_in__lt=check_out_date,
                    check_out__gt=check_in_date,
                ).exists()
                if room_conflict:
                    raise ParseError("The whole room is booked for those dates.")
                
                # Check if this specific bed is booked
                bed_conflict = Booking.objects.filter(
                    bed=bed,
                    kind=Booking.BookingKindChoices.BED,
                    check_in__lt=check_out_date,
                    check_out__gt=check_in_date,
                ).exists()
                if bed_conflict:
                    raise ParseError("This bed is already booked for those dates.")
            except ValueError:
                raise ParseError("Invalid date format. Use YYYY-MM-DD.")
        
        # Check guest capacity (default to 1 if not provided)
        if guests:
            try:
                guests = int(guests)
            except ValueError:
                return Response(
                    {
                        "available": False,
                        "reason": "INVALID_GUESTS",
                        "message": "guests must be an integer.",
                        "details": {
                            "guests": guests,
                        }
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            guests = 1  # Default to 1 guest if not provided
        
        # Each bed can only accommodate 1 guest
        if guests > 1:
            raise ParseError("Each bed can only accommodate 1 guest.")
        
        return Response(
            {"available": True, "message": "Booking is available for the specified dates and guests."},
            status=status.HTTP_200_OK
        )