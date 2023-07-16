#!/usr/bin/env python3

import unittest
from unittest.mock import patch

from ocu.calendar import get_calendar
from ocu.calendars.icalbuddy_calendar import IcalBuddyCalendar
from tests.utils import use_env, use_icalbuddy_output

case = unittest.TestCase()


@patch("os.path.exists", return_value=True)
@use_env("use_icalbuddy", "true")
def test_icalbuddy_available_enabled(exists):
    """should use icalBuddy if it is both available and enabled"""
    case.assertIsInstance(get_calendar(), IcalBuddyCalendar)


@patch("os.path.exists", return_value=True)
@use_env("use_icalbuddy", "false")
def test_icalbuddy_available_disabled(exists):
    """should not use icalBuddy if it is available but disabled"""
    case.assertNotIsInstance(get_calendar(), IcalBuddyCalendar)


@patch("os.path.exists", return_value=False)
@use_env("use_icalbuddy", "true")
def test_icalbuddy_unavailable_enabled(exists):
    """should not use icalBuddy if it is enabled but unavailable"""
    case.assertNotIsInstance(get_calendar(), IcalBuddyCalendar)


@patch("os.path.exists", return_value=False)
@use_env("use_icalbuddy", "false")
def test_icalbuddy_unavailable_disabled(exists):
    """should not use icalBuddy if it is disabled and unavailable"""
    case.assertNotIsInstance(get_calendar(), IcalBuddyCalendar)


@use_icalbuddy_output("single_event")
def test_single_event():
    """should parse single event from icalBuddy output"""
    calendar = IcalBuddyCalendar()
    event_dicts = calendar.get_event_dicts()
    case.assertEqual(event_dicts[0]["title"], "WWDC 2022 Keynote")
    case.assertEqual(event_dicts[0]["startDate"], "2022-06-06T10:00")
    case.assertEqual(event_dicts[0]["endDate"], "2022-06-06T12:15")
    case.assertEqual(event_dicts[0]["location"], "https://apple.zoom.us/j/123456")
    case.assertEqual(event_dicts[0]["notes"], "")
    case.assertEqual(len(event_dicts), 1)


@use_icalbuddy_output("multiple_events")
def test_multiple_events():
    """should parse multiple events from icalBuddy output"""
    calendar = IcalBuddyCalendar()
    event_dicts = calendar.get_event_dicts()
    case.assertEqual(event_dicts[0]["title"], "WWDC 2023 Keynote")
    case.assertEqual(event_dicts[0]["startDate"], "2023-06-05T10:00")
    case.assertEqual(event_dicts[0]["endDate"], "2023-06-05T12:15")
    case.assertEqual(event_dicts[0]["location"], "https://apple.zoom.us/j/123456")
    case.assertEqual(event_dicts[0]["notes"], "")
    case.assertEqual(event_dicts[1]["title"], "WWDC 2023 State of the Platform")
    case.assertEqual(event_dicts[1]["startDate"], "2023-06-05T13:00")
    case.assertEqual(event_dicts[1]["endDate"], "2023-06-05T14:30")
    case.assertEqual(event_dicts[1]["location"], "https://apple.zoom.us/j/789012")
    case.assertEqual(event_dicts[1]["notes"], "")
    case.assertEqual(len(event_dicts), 2)


@use_icalbuddy_output("multiple_days")
def test_multiple_days():
    """should parse single event spanning multiple days from icalBuddy output"""
    calendar = IcalBuddyCalendar()
    event_dicts = calendar.get_event_dicts()
    case.assertEqual(event_dicts[0]["title"], "Multi-Day Meeting")
    case.assertEqual(event_dicts[0]["startDate"], "2023-06-26T09:00")
    case.assertEqual(event_dicts[0]["endDate"], "2023-06-27T15:30")
    case.assertEqual(event_dicts[0]["location"], "https://zoom.us/j/123456")
    case.assertEqual(event_dicts[0]["notes"], "")
    case.assertEqual(len(event_dicts), 1)


@use_icalbuddy_output("single_day_all_day")
def test_single_day_all_day():
    """should parse all-day event (on a single day) from icalBuddy output"""
    calendar = IcalBuddyCalendar()
    event_dicts = calendar.get_event_dicts()
    case.assertEqual(event_dicts[0]["title"], "Single-Day All-Day Meeting")
    case.assertEqual(event_dicts[0]["startDate"], "2023-06-21T00:00")
    case.assertEqual(event_dicts[0]["endDate"], "2023-06-21T23:59")
    case.assertEqual(event_dicts[0]["location"], "https://zoom.us/j/123456")
    case.assertEqual(event_dicts[0]["notes"], "")
    case.assertEqual(len(event_dicts), 1)


@use_icalbuddy_output("multiple_days_all_day")
def test_multiple_days_all_day():
    """should parse all-day event (over multiple days) from icalBuddy output"""
    calendar = IcalBuddyCalendar()
    event_dicts = calendar.get_event_dicts()
    case.assertEqual(event_dicts[0]["title"], "Multi-Day All-Day Meeting")
    case.assertEqual(event_dicts[0]["startDate"], "2023-06-28T00:00")
    case.assertEqual(event_dicts[0]["endDate"], "2023-06-30T23:59")
    case.assertEqual(event_dicts[0]["location"], "https://zoom.us/j/123456")
    case.assertEqual(event_dicts[0]["notes"], "")
    case.assertEqual(len(event_dicts), 1)
