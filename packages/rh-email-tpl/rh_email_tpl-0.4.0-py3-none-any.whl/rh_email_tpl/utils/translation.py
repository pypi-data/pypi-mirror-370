from functools import wraps

from django.utils import translation


def custom_translation_override(language):
    """
    Custom decorator which re-implements translation.override in a recursion-safe way.
    :param language: language-code string
    :return: function wrapped with translation.override context manager
    """

    def wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            with translation.override(language):
                return func(*args, **kwargs)

        return inner

    return wrapper
