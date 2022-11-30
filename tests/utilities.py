#!/usr/bin/env python3

import os
import sys
import types
from functools import wraps
from io import StringIO
from unittest.mock import patch


def redirect_stdout(func):
    """Temporarily redirects stdout to new Unicode output stream"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        original_stdout = sys.stdout
        out = StringIO()
        try:
            sys.stdout = out
            return func(out, *args, **kwargs)
        finally:
            sys.stdout = original_stdout
    return wrapper


# Derived from: <https://gist.github.com/LeoHuckvale/8f50f8f2a6235512827b>
def use_env(key, value):
    """
    Sets an environment variable for only the lifetime of the given function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Setting only a single environment variable at a time ensures that
            # this decorator can be used multiple times on the same function
            os.environ[key] = value
            try:
                return_value = func(*args, **kwargs)
                if isinstance(return_value, types.GeneratorType):
                    yield from return_value
                else:
                    return return_value
            finally:
                os.environ[key] = ''
        return wrapper

    return decorator


def use_events(event_dicts):
    """
    Sets the current list of raw event blobs to use in ocu.list_events
    """
    def decorator(func):
        @patch('ocu.list_events.get_event_blobs', return_value=event_dicts)
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper

    return decorator
