from django.shortcuts import render
from django.contrib.auth.decorators import login_required


def index(request):
    return render(request, "chat/index.html")


# TODO: add decorator to check room existence and membership
@login_required
def room(request, room_id):
    return render(
        request,
        "chat/room.html",
        {"room_id": room_id, "username": request.user.username},
    )
