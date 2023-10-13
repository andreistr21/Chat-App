from django.test import Client
from django.urls import reverse

from users.views import RegistrationView


def test_url_name(client: Client):
    """
    Tests url for used view with URL name.
    """
    response = client.get(reverse("users:register"))

    assert response.status_code == 200
    assert response.resolver_match.func.view_class == RegistrationView  # type: ignore


def test_url_pattern(client: Client):
    """
    Tests url for used view with URL pattern.
    """
    response = client.get("/en/users/register/")

    assert response.status_code == 200
    assert response.resolver_match.func.view_class == RegistrationView  # type: ignore
