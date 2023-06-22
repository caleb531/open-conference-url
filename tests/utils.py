#!/usr/bin/env python3

import os
import sys
from contextlib import contextmanager
from io import StringIO
from unittest.mock import patch


@contextmanager
def redirect_stdout(fn):
    """Temporarily redirects stdout to new Unicode output stream"""
    original_stdout = sys.stdout
    out = StringIO()
    try:
        sys.stdout = out
        yield
    finally:
        sys.stdout = original_stdout


@contextmanager
def use_env(key, value):
    # Setting only a single environment variable at a time ensures that this
    # context manager can be used multiple times on the same function
    orig_value = os.environ.get(key, '')
    os.environ[key] = value
    try:
        yield
    finally:
        os.environ[key] = orig_value


@contextmanager
def use_event_dicts(event_dicts):
    """
    Sets the current list of raw event dicts to use in ocu.list_events
    """
    with patch('ocu.calendar.calendar.get_event_dicts',
               return_value=event_dicts):
        yield
