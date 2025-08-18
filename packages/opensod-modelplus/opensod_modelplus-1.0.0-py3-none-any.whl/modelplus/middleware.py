"""Middleware for current user. Taken from ai-django-core."""

from threading import local

from django.contrib.auth.models import AbstractBaseUser
from django.http import HttpRequest

_user = local()


class CurrentUserMiddleware:
    """
    Middleware to store request's user into global thread-safe variable.

    Must be introduced after
    `django.contrib.auth.middleware.AuthenticationMiddleware`.
    """

    def process_request(self, request: HttpRequest) -> None:
        """Store user from request into _user variable."""
        _user.value = request.user

    @staticmethod
    def get_current_user() -> AbstractBaseUser | int | None:
        """Get current user."""
        return _user.value if hasattr(_user, "value") else None
