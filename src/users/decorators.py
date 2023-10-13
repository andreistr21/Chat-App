from functools import wraps

from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse


# TODO: Add tests
def anonymous_required(
    view_func, redirect_url=settings.ANONYMOUS_REDIRECT_URL
):
    """
    This decorator ensures that an user is not logged in, redirects if
    otherwise.
    """

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        return redirect(reverse(redirect_url))

    return wrapper
