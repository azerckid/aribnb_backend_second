from rest_framework import serializers

from users.serializers import TinyUserSerializer
from .models import Experience, Perk


class PerkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Perk
        fields = "__all__"


class ExperienceListSerializer(serializers.ModelSerializer):

    host = TinyUserSerializer(read_only=True)

    class Meta:
        model = Experience
        fields = (
            "pk",
            "name",
            "country",
            "city",
            "price",
            "host",
            "duration",
        )


class ExperienceDetailSerializer(serializers.ModelSerializer):

    host = TinyUserSerializer(read_only=True)
    perks = PerkSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Experience
        fields = "__all__"


class ExperienceCreateUpdateSerializer(serializers.ModelSerializer):

    perks = serializers.PrimaryKeyRelatedField(
        queryset=Perk.objects.all(),
        many=True,
        required=False,
    )

    class Meta:
        model = Experience
        fields = (
            "name",
            "country",
            "city",
            "price",
            "address",
            "start",
            "end",
            "duration",
            "description",
            "perks",
            "category",
        )

    def create(self, validated_data):
        perks = validated_data.pop("perks", [])
        experience = Experience.objects.create(**validated_data)
        if perks:
            experience.perks.set(perks)
        return experience

    def update(self, instance, validated_data):
        perks = validated_data.pop("perks", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if perks is not None:
            instance.perks.set(perks)
        return instance

