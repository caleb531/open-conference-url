#!/usr/bin/env python3

import unittest
from unittest.mock import Mock

from ocu.calendars.base_calendar import BaseCalendar

case = unittest.TestCase()


def test_base_calendar_not_instantiable():
    """Should not be able to instantiate a BaseCalendar object by itself"""
    with case.assertRaises(TypeError):
        BaseCalendar()


def test_get_event_dicts_not_implemented():
    """
    Should require the BaseCalendar.get_event_dicts() method to be implemented
    by any subclass of BaseCalendar
    """
    with case.assertRaises(NotImplementedError):
        BaseCalendar.get_event_dicts(Mock())
