#!/usr/bin/env python3

import os
from functools import wraps


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
                return func(*args, **kwargs)
            finally:
                os.environ[key] = ''
        return wrapper

    return decorator
