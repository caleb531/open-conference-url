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


# Derived from: <https://gist.github.com/LeoHuckvale/8f50f8f2a6235512827b> and
# <https://stackoverflow.com/questions/64622473/can-you-write-a-python-decorator-that-works-for-generator-functions-and-normal-f>
def use_env(key, value):
    """
    Sets an environment variable for only the lifetime of the given function;
    this decorator works for both functions and generators
    """
    def decorator(func):
        @wraps(func)
        def function_wrapper(*args, **kwargs):
            orig_value = os.environ.get(key, '')
            os.environ[key] = value
            try:
                return_value = func(*args, **kwargs)
            finally:
                os.environ[key] = orig_value
            return return_value

        @wraps(func)
        def generator_wrapper(*args, **kwargs):
            orig_value = os.environ.get(key, '')
            os.environ[key] = value
            try:
                return_value = yield from func(*args, **kwargs)
            finally:
                os.environ[key] = orig_value
            return return_value
        return generator_wrapper if inspect.isgeneratorfunction(func) else function_wrapper

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
