from rest_framework import serializers

from .models import Experience, Perk


class PerkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Perk
        fields = "__all__"


class ExperienceListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Experience
        fields = (
            "pk",
            "name",
            "country",
            "city",
            "price",
        )

