"""
Utility functions for the app.
"""

import typing
from django.contrib.auth import get_user_model as _get_user_model
from core.models import User


def get_user_model():
    """Return the user model that is active in this project."""

    return typing.cast(User, _get_user_model())
