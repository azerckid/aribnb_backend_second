from django.db import models
from cloudinary.models import CloudinaryField
import cloudinary.uploader

from common.models import CommonModel


class Photo(CommonModel):
    """Photo files for rooms or experiences."""

    file = CloudinaryField('image')
    description = models.CharField(max_length=140)
    room = models.ForeignKey(
        "rooms.Room",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="photos",
    )
    experience = models.ForeignKey(
        "experiences.Experience",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="photos",
    )

    def __str__(self) -> str:
        target = self.room or self.experience
        return f"Photo for {target}"

    def delete(self, *args, **kwargs):
        """Django 모델 삭제 시 Cloudinary에서도 이미지 삭제"""
        if self.file:
            try:
                # Cloudinary에서 이미지 삭제
                cloudinary.uploader.destroy(self.file.public_id)
            except Exception:
                # Cloudinary 삭제 실패해도 Django 모델은 삭제
                pass
        # Django 모델 인스턴스 삭제
        super().delete(*args, **kwargs)


class Video(CommonModel):
    """Video files for experiences."""

    file = models.URLField()
    experience = models.OneToOneField(
        "experiences.Experience",
        on_delete=models.CASCADE,
        related_name="videos",
    )

    def __str__(self) -> str:
        return f"Video for {self.experience}"

