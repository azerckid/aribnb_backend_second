from django.db import models

from common.models import CommonModel


class ChattingRoom(CommonModel):
    """Chat room containing one or more users."""

    users = models.ManyToManyField("users.User", related_name="chat_rooms")

    def __str__(self) -> str:
        return f"Room #{self.pk} with {self.users.count()} users"


class Message(CommonModel):
    """Individual message sent inside a chat room."""

    text = models.TextField()
    user = models.ForeignKey(
        "users.User",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="messages",
    )
    room = models.ForeignKey(
        ChattingRoom,
        on_delete=models.CASCADE,
        related_name="messages",
    )

    def __str__(self) -> str:
        author = self.user or "Anonymous"
        return f"{author}: {self.text[:20]}"

