#!/usr/bin/env python3

from unittest.mock import Mock

import pytest

from ocu.calendars.base_calendar import BaseCalendar


def test_base_calendar_not_instantiable():
    """Should not be able to instantiate a BaseCalendar object by itself"""
    with pytest.raises(TypeError):
        BaseCalendar()  # type: ignore


def test_get_event_dicts_not_implemented():
    """
    Should require the BaseCalendar.get_event_dicts() method to be implemented
    by any subclass of BaseCalendar
    """
    with pytest.raises(NotImplementedError):
        BaseCalendar.get_event_dicts(Mock())
