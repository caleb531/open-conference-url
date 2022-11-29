#!/usr/bin/env python3

import os
import types
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
                return_value = func(*args, **kwargs)
                if isinstance(return_value, types.GeneratorType):
                    yield from return_value
                else:
                    return return_value
            finally:
                os.environ[key] = ''
        return wrapper

    return decorator
