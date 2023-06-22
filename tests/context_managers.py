#!/usr/bin/env python3

import os
from contextlib import contextmanager


@contextmanager
def use_env_context(key, value):
    # Setting only a single environment variable at a time ensures that
    # this decorator can be used multiple times on the same function
    orig_value = os.environ.get(key, '')
    os.environ[key] = value
    try:
        yield
    finally:
        os.environ[key] = orig_value
