from django.contrib.auth.views import LoginView
from django.test import Client
from django.urls import reverse


def test_url_name(client: Client):
    """
    Tests url for used view with URL name.
    """
    response = client.get(reverse("users:login"))

    assert response.status_code == 200
    assert response.resolver_match.func.view_class == LoginView  # type: ignore


def test_url_pattern(client: Client):
    """
    Tests url for used view with URL pattern.
    """
    response = client.get("/en/users/login/")

    assert response.status_code == 200
    assert response.resolver_match.func.view_class == LoginView  # type: ignore
