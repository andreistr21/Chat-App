from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from chat.selectors import get_user_chats
from chat.services import chats_list


@login_required
def index(request):
    chat_rooms = get_user_chats(request.user)
    chats_info = chats_list(chat_rooms)

    return render(
        request,
        "chat/index.html",
        {"chat_rooms": chat_rooms, "chats_info": chats_info},
    )


# TODO: add decorator to check room existence and membership
@login_required
def room(request, room_id):
    return render(
        request,
        "chat/room.html",
        {"room_id": room_id, "username": request.user.username},
    )
