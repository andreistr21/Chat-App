import pytest
from django.contrib.auth.models import AnonymousUser, User
from django.test.client import RequestFactory
from django.urls import reverse

from chat.views import index


@pytest.mark.django_db
def test_access_allowed(rf: RequestFactory, user: User):
    """
    Tests index view with authenticated user.
    """
    request = rf.get(reverse("chat:index"))
    request.user = user

    response = index(request)

    assert response.status_code == 200


def test_access_denied(rf: RequestFactory):
    """
    Tests index view with anonymous user.
    """
    request = rf.get(reverse("chat:index"))
    request.user = AnonymousUser()

    response = index(request)

    assert response.status_code == 302
