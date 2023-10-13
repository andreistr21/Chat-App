from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from users.decorators import anonymous_required
from users.views import RegistrationView

app_name = "users"
urlpatterns = [
    path(
        "login/",
        anonymous_required(
            LoginView.as_view(template_name="users/login.html")
        ),
        name="login",
    ),
    path(
        "register/",
        anonymous_required(RegistrationView.as_view()),
        name="register",
    ),
    path(
        "logout/",
        login_required(LogoutView.as_view(template_name=None)),
        name="logout",
    ),
]
