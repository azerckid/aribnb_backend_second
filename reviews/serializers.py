from rest_framework import serializers

from users.serializers import TinyUserSerializer
from .models import Review


class ReviewSerializer(serializers.ModelSerializer):

    user = TinyUserSerializer(read_only=True)
    reply_user = TinyUserSerializer(read_only=True)

    class Meta:
        model = Review
        fields = (
            "pk",
            "user",
            "payload",
            "rating",
            "created_at",
            "updated_at",
            "reply",
            "reply_user",
            "reply_created_at",
        )

