from django.conf import settings
import pytest
from django.contrib.auth.views import LogoutView
from django.test import Client
from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
def test_url_name(user_client: Client):
    """
    Tests url for used view with URL name.
    """
    response = user_client.get(reverse("users:logout"))

    assertRedirects(response, reverse(settings.LOGOUT_REDIRECT_URL))  # type: ignore
    assert response.resolver_match.func.view_class == LogoutView  # type: ignore


@pytest.mark.django_db
def test_url_pattern(user_client: Client):
    """
    Tests url for used view with URL pattern.
    """
    response = user_client.get("/en/users/logout/")

    assertRedirects(response, reverse(settings.LOGOUT_REDIRECT_URL))  # type: ignore
    assert response.resolver_match.func.view_class == LogoutView  # type: ignore
