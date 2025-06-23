#!/usr/bin/env python3

import unittest
from unittest.mock import Mock

from ocu.calendars.base_calendar import BaseCalendar


class TestBaseCalendar(unittest.TestCase):
    def test_base_calendar_not_instantiable(self):
        """Should not be able to instantiate a BaseCalendar object by itself"""
        with self.assertRaises(TypeError):
            BaseCalendar()  # type: ignore

    def test_get_event_dicts_not_implemented(self):
        """
        Should require the BaseCalendar.get_event_dicts() method to be implemented
        by any subclass of BaseCalendar
        """
        with self.assertRaises(NotImplementedError):
            BaseCalendar.get_event_dicts(Mock())
