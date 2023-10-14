import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse, reverse_lazy
from pytest_django.asserts import assertRedirects, assertTemplateUsed

URL = reverse_lazy("users:login")


def test_template_used(client: Client):
    response = client.get(URL)

    assertTemplateUsed(response, "users/login.html")  # type: ignore


def test_allowed_access(client: Client):
    """
    Tests if access will be allowed with anonymous user.
    """
    response = client.get(URL)

    assert response.status_code == 200


@pytest.mark.django_db
def test_denied_access(user_client: Client):
    """
    Tests if access will be denied with authenticated user.
    """
    response = user_client.get(URL)

    assertRedirects(response, reverse("chat:index"))  # type: ignore


@pytest.mark.django_db
def test_post_method(client: Client):
    """
    Tests post method of the view
    """
    username = "test-username"
    password = "test-password"
    data = {"username": username, "password": password}
    User.objects.create_user(**data)

    # Retrieves csrf token and adds it to data
    response_get = client.get(URL)
    csrf_token = response_get.context["csrf_token"]
    data["csrfmiddlewaretoken"] = str(csrf_token)

    response = client.post(URL, data, follow=True)
    a = 1
    assert response.context["user"].is_authenticated
    # Asserts that user will be redirected
    assert response.redirect_chain == [(reverse("chat:index"), 302)]
