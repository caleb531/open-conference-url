#!/usr/bin/env python3

import json
import sys
from functools import wraps
from io import StringIO
from unittest.mock import patch

from tests.context_managers import use_env_context


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
            with use_env_context(key, value):
                return func(*args, **kwargs)
        return wrapper

    return decorator


def use_event_dicts(event_dicts):
    """
    Sets the current list of raw event dicts to use in ocu.list_events
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with patch('subprocess.check_output',
                       return_value=json.dumps(event_dicts).encode('utf-8')):
                return func(*args, event_dicts, **kwargs)
        return wrapper

    return decorator
