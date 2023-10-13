from functools import wraps

from django.conf import settings
from django.shortcuts import redirect, resolve_url


def anonymous_required(
    view_func, redirect_url: str = settings.ANONYMOUS_REDIRECT_URL
):
    """
    This decorator ensures that an user is not logged in, redirects if
    otherwise.
    
    Parameters:
        - redirect_url: URL pattern or name could be passed.
    """

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        return redirect(resolve_url(redirect_url))

    return wrapper
