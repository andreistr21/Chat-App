from functools import wraps

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, resolve_url

from chat.models import ChatRoom
from chat.selectors import get_room


def chat_membership(view_func):
    """
    Decorator for views that checks that the room exists and the user belongs
    to it, redirecting to the chats list page if necessary.
    """

    @wraps(view_func)
    def wrapper(
        request, room_id: str, *args, **kwargs
    ) -> HttpResponseRedirect:
        if (
            isinstance(room_obj := get_room(room_id), ChatRoom)
            and room_obj.members.filter(id=request.user.id).exists()
        ):
            return view_func(request, room_id, *args, **kwargs)
        
        return redirect(resolve_url(settings.CHATS_URL), permanent=False)

    return wrapper
