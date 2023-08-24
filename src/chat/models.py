from django.db import models
from django.conf import settings


class Message(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="author",
        on_delete=models.CASCADE,
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Message"
        verbose_name_plural = "Messages"

    def __str__(self):
        return self.author.username
