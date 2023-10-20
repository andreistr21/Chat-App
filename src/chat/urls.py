from django.urls import path

from chat import views

app_name = "chat"
urlpatterns = [
    path("", views.index, name="index"),
    path("<uuid:room_id>/", views.room, name="room"),
    path("create/", views.create_room, name="create_room"),
]
