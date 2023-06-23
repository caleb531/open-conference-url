#!/usr/bin/env python3

import os
import json
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
            orig_value = os.environ.get(key, '')
            os.environ[key] = value
            try:
                return_value = func(*args, **kwargs)
                if isinstance(return_value, types.GeneratorType):
                    yield from return_value
                else:
                    return return_value
            finally:
                os.environ[key] = orig_value
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
