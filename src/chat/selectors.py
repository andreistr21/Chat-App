from chat.models import Message
from django.db.models import QuerySet


def last_20_messages() -> QuerySet[Message]:
    return Message.objects.order_by("-timestamp").all()[:20][::-1]
