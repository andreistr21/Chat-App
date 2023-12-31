import uuid

from django.conf import settings
from django.db import models


class ChatRoom(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="admin",
        on_delete=models.CASCADE,
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="chat_rooms"
    )

    room_name = models.CharField(max_length=255, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Chat room"
        verbose_name_plural = "Chat rooms"

    def __str__(self) -> str:
        return self.room_name or str(self.id)


class Message(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="author",
        on_delete=models.CASCADE,
    )
    room = models.ForeignKey(
        ChatRoom, related_name="message", on_delete=models.CASCADE
    )
    unread_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="unread_messages"
    )

    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Message"
        verbose_name_plural = "Messages"

    def __str__(self) -> str:
        return f"{self.author.username}: {self.content[:100]}"
