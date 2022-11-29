#!/usr/bin/env python3

import os
from contextlib import contextmanager


@contextmanager
def use_env(key, value):
    """
    Sets an environment variable for only the lifetime of the given function
    """
    os.environ[key] = value
    try:
        yield
    finally:
        os.environ[key] = ''
