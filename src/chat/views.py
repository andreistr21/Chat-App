from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from chat.decorators import chat_membership
from chat.forms import ChatRoomForm, ChatRoomMembersForm
from chat.selectors import get_room, get_user_chats
from chat.services import chats_list


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


@require_http_methods(["GET"])
@login_required
@chat_membership
def room(request, room_id: str):
    chat_rooms = get_user_chats(request.user)
    chats_info = chats_list(chat_rooms, request.user, room_id)
    room_name = next(filter(lambda tuple: tuple[0] == room_id, chats_info))[1]

    return render(
        request,
        "chat/room.html",
        {
            "room_id": room_id,
            "username": request.user.username,
            "chat_rooms": chat_rooms,
            "chats_info": chats_info,
            "room_name": room_name,
        },
    )


@require_http_methods(["GET", "POST"])
@login_required
def create_room(request):
    """
    View for room creation.
    """
    if request.method == "GET":
        chat_room_form = ChatRoomForm(request=request)
    elif request.method == "POST":
        chat_room_form = ChatRoomForm(request.POST, request=request)
        if chat_room_form.is_valid():
            new_room = chat_room_form.save()

            return redirect(reverse("chat:room", args=(new_room.id,)))

    return render(
        request, "chat/create_room.html", {"chat_room_form": chat_room_form}
    )


# TODO: Add tests
@require_http_methods(["GET", "POST"])
@login_required
@chat_membership
def add_members(request, room_id: str):
    if request.method == "GET":
        chat_room_members_form = ChatRoomMembersForm()
    elif request.method == "POST":
        room = get_room(room_id)
        if room is None:
            return redirect(reverse("chat:index"))

        chat_room_members_form = ChatRoomMembersForm(request.POST)
        if chat_room_members_form.is_valid():
            chat_room_members_form.update_members(room)

            return redirect(reverse("chat:room", args=(room.id,)))

    return render(
        request,
        "chat/add_members.html",
        {"chat_room_members_form": chat_room_members_form},
    )
