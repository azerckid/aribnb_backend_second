from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from .models import Photo


class PhotoSerializer(ModelSerializer):

    class Meta:
        model = Photo
        fields = (
            "pk",
            "file",
            "description",
        )

    def to_representation(self, instance):
        """출력 시 file 필드를 전체 Cloudinary URL로 변환"""
        representation = super().to_representation(instance)
        if instance.file:
            # CloudinaryField의 전체 URL 반환
            representation['file'] = str(instance.file.url) if hasattr(instance.file, 'url') else str(instance.file)
        return representation

