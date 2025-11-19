from rest_framework import serializers
from .models import Amenity, Room, Bed
from users.serializers import TinyUserSerializer
from reviews.serializers import ReviewSerializer
from categories.serializers import CategorySerializer
from medias.serializers import PhotoSerializer
from wishlists.models import Wishlist

class AmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Amenity
        fields = (
            "pk",
            "name",
            "description",
        )

class BedSerializer(serializers.ModelSerializer):

    class Meta:
        model = Bed
        fields = (
            "pk",
            "name",
            "bed_type",
            "capacity",
        )

class RoomDetailSerializer(serializers.ModelSerializer):

    pk = serializers.IntegerField(read_only=True)
    id = serializers.IntegerField(read_only=True)
    owner = TinyUserSerializer(read_only=True)
    amenities = AmenitySerializer(
        read_only=True,
        many=True,
    )
    category = CategorySerializer(
        read_only=True,
    )
    rating = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    photos = PhotoSerializer(many=True, read_only=True)
    bed_list = BedSerializer(many=True, read_only=True)

    class Meta:
        model = Room
        fields = [
            "id",
            "pk",
            "name",
            "country",
            "city",
            "address",
            "price",
            "rooms",
            "toilets",
            "beds",
            "description",
            "pet_friendly",
            "kind",
            "category",
            "amenities",
            "rating",
            "is_owner",
            "is_liked",
            "photos",
            "bed_list",
            "owner",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "pk",
            "rating",
            "is_owner",
            "is_liked",
            "photos",
            "bed_list",
            "owner",
            "created_at",
            "updated_at",
        ]

    def get_rating(self, room):
        return room.rating()

    def get_is_owner(self, room):
        request = self.context["request"]
        if not request.user.is_authenticated:
            return False
        return room.owner == request.user

    def get_is_liked(self, room):
        request = self.context["request"]
        if not request.user.is_authenticated:
            return False
        return Wishlist.objects.filter(
            user=request.user,
            rooms__pk=room.pk,
        ).exists()

class RoomListSerializer(serializers.ModelSerializer):

    rating = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()
    photos = PhotoSerializer(many=True, read_only=True)

    class Meta:
        model = Room
        fields = (
            "pk",
            "name",
            "country",
            "city",
            "price",
            "rating",
            "is_owner",
            "photos",
        )

    def get_rating(self, room):
        return room.rating()

    def get_is_owner(self, room):
        request = self.context["request"]
        if not request.user.is_authenticated:
            return False
        return room.owner == request.user
