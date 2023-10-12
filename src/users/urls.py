from django.contrib.auth.views import LoginView
from django.urls import path

from users.views import RegistrationView

app_name = "users"
urlpatterns = [
    path(
        "login",
        LoginView.as_view(template_name="users/login.html"),
        name="login",
    ),
    path(
        "register",
        RegistrationView.as_view(),
        name="register",
    ),
]
