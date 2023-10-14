import pytest
from django.test import Client
from django.urls import reverse, reverse_lazy
from pytest_django.asserts import assertRedirects, assertTemplateNotUsed

URL = reverse_lazy("users:logout")


@pytest.mark.django_db
def test_template_used(user_client: Client):
    response = user_client.get(URL)

    assertTemplateNotUsed(response, None)  # type: ignore


@pytest.mark.django_db
def test_allowed_access(user_client: Client):
    """
    Tests if access will be allowed with anonymous user.
    """
    response = user_client.get(URL)

    assertRedirects(response, reverse("users:login"))  # type: ignore


def test_denied_access(client: Client):
    """
    Tests if access will be denied with authenticated user.
    """
    response = client.get(URL)

    assertRedirects(response, reverse("users:login") + "?next=%2Fen%2Fusers%2Flogout%2F")  # type: ignore


@pytest.mark.django_db
def test_post_method(user_client: Client):
    """
    Tests post method of the view
    """
    response = user_client.post(URL)

    # Asserts that user will be redirected
    assertRedirects(response, reverse("users:login"))  # type: ignore
