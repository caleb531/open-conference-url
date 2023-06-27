#!/usr/bin/env python3

import os
import os.path
import inspect
import json
import sys
from functools import wraps
from io import StringIO
from unittest.mock import patch


def redirect_stdout(func):
    """A decorator which redirects stdout to new Unicode output stream; it must
    be called without parentheses"""
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


class use_env(object):

    """
    A decorator (can also be used as a context manager) which sets an
    environment variable for only the lifetime of the given code; this utility
    works seamlessly for both functions and generators
    """

    def __init__(self, key, value):
        self.key = key
        self.value = value

    def __enter__(self):
        self.orig_value = os.environ.get(self.key, '')
        os.environ[self.key] = self.value

    def __exit__(self, type, value, traceback):
        os.environ[self.key] = self.orig_value

    # Derived from: <https://gist.github.com/LeoHuckvale/8f50f8f2a6235512827b>
    # and
    # <https://stackoverflow.com/questions/64622473/can-you-write-a-python-decorator-that-works-for-generator-functions-and-normal-f>
    def __call__(self, func):
        @wraps(func)
        def function_wrapper(*args, **kwargs):
            with self:
                return func(*args, **kwargs)

        @wraps(func)
        def generator_wrapper(*args, **kwargs):
            with self:
                return_value = yield from func(*args, **kwargs)
            return return_value

        if inspect.isgeneratorfunction(func):
            return generator_wrapper
        else:
            return function_wrapper


def use_event_dicts(event_dicts):
    """
    A decorator which sets the current list of raw event dicts to use in
    ocu.list_events
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with patch('subprocess.check_output',
                       return_value=json.dumps(event_dicts).encode('utf-8')):
                return func(*args, event_dicts, **kwargs)
        return wrapper

    return decorator


def use_icalbuddy_output(file_name):
    """
        Sets the current list of raw event dicts to use in ocu.list_events
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            file_path = os.path.join(
                'tests', 'icalbuddy_output', f'{file_name}.txt')
            with open(file_path, 'r') as file:
                file_contents = file.read()
            with patch('subprocess.check_output',
                       return_value=file_contents.encode('utf-8')):
                return func(*args, **kwargs)
        return wrapper

    return decorator
