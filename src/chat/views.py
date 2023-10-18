from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from chat.decorators import chat_membership
from chat.selectors import get_user_chats
from chat.services import chats_list


# TODO: Update tests
@require_http_methods(["GET"])
@login_required
def index(request):
    """
    Main view that renders chats list with no opened chat room.
    """
    chat_rooms = get_user_chats(request.user)
    chats_info = chats_list(chat_rooms, request.user)

    return render(
        request,
        "chat/index.html",
        {"chat_rooms": chat_rooms, "chats_info": chats_info},
    )


# TODO: Update tests
@require_http_methods(["GET"])
@login_required
@chat_membership
def room(request, room_id: str):
    chat_rooms = get_user_chats(request.user)
    chats_info = chats_list(chat_rooms, request.user, room_id)

    return render(
        request,
        "chat/room.html",
        {
            "room_id": room_id,
            "username": request.user.username,
            "chat_rooms": chat_rooms,
            "chats_info": chats_info,
        },
    )
