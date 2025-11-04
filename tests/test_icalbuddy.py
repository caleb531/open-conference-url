#!/usr/bin/env python3

from unittest.mock import patch

from freezegun import freeze_time

from ocu.calendar import get_calendar
from ocu.calendars.icalbuddy_calendar import IcalBuddyCalendar
from tests.utils import use_env, use_icalbuddy_output


@patch("os.path.exists", return_value=True)
@use_env("use_icalbuddy", "true")
def test_icalbuddy_available_enabled(_exists):
    """should use icalBuddy if it is both available and enabled"""
    assert isinstance(get_calendar(), IcalBuddyCalendar)


@patch("os.path.exists", return_value=True)
@use_env("use_icalbuddy", "false")
def test_icalbuddy_available_disabled(_exists):
    """should not use icalBuddy if it is available but disabled"""
    assert not isinstance(get_calendar(), IcalBuddyCalendar)


@patch("os.path.exists", return_value=False)
@use_env("use_icalbuddy", "true")
def test_icalbuddy_unavailable_enabled(_exists):
    """should not use icalBuddy if it is enabled but unavailable"""
    assert not isinstance(get_calendar(), IcalBuddyCalendar)


@patch("os.path.exists", return_value=False)
@use_env("use_icalbuddy", "false")
def test_icalbuddy_unavailable_disabled(_exists):
    """should not use icalBuddy if it is disabled and unavailable"""
    assert not isinstance(get_calendar(), IcalBuddyCalendar)


@use_icalbuddy_output("single_event")
def test_single_event():
    """should parse single event from icalBuddy output"""
    calendar = IcalBuddyCalendar()
    event_dicts = calendar.get_event_dicts()
    assert event_dicts[0]["title"] == "WWDC 2022 Keynote"
    assert event_dicts[0]["startDate"] == "2022-06-06T10:00"
    assert event_dicts[0]["endDate"] == "2022-06-06T12:15"
    assert event_dicts[0].get("location") == "https://apple.zoom.us/j/123456"
    assert event_dicts[0].get("notes") == ""
    assert len(event_dicts) == 1


@use_icalbuddy_output("multiple_events")
def test_multiple_events():
    """should parse multiple events from icalBuddy output"""
    calendar = IcalBuddyCalendar()
    event_dicts = calendar.get_event_dicts()
    assert event_dicts[0]["title"] == "WWDC 2023 Keynote"
    assert event_dicts[0]["startDate"] == "2023-06-05T10:00"
    assert event_dicts[0]["endDate"] == "2023-06-05T12:15"
    assert event_dicts[0].get("location") == "https://apple.zoom.us/j/123456"
    assert event_dicts[0].get("notes") == ""
    assert event_dicts[1]["title"] == "WWDC 2023 State of the Platform"
    assert event_dicts[1]["startDate"] == "2023-06-05T13:00"
    assert event_dicts[1]["endDate"] == "2023-06-05T14:30"
    assert event_dicts[1].get("location") == "https://apple.zoom.us/j/789012"
    assert event_dicts[1].get("notes") == ""
    assert len(event_dicts) == 2


@use_env("calendar_names", "General,Work")
@use_icalbuddy_output("multiple_events")
def test_select_calendars():
    """should specify certain calendars from which to fetch event data"""
    calendar = IcalBuddyCalendar()
    event_dicts = calendar.get_event_dicts()
    assert event_dicts[0]["title"] == "WWDC 2023 Keynote"
    assert event_dicts[0]["startDate"] == "2023-06-05T10:00"
    assert event_dicts[0]["endDate"] == "2023-06-05T12:15"
    assert event_dicts[0].get("location") == "https://apple.zoom.us/j/123456"
    assert event_dicts[0].get("notes") == ""
    assert event_dicts[1]["title"] == "WWDC 2023 State of the Platform"
    assert event_dicts[1]["startDate"] == "2023-06-05T13:00"
    assert event_dicts[1]["endDate"] == "2023-06-05T14:30"
    assert event_dicts[1].get("location") == "https://apple.zoom.us/j/789012"
    assert event_dicts[1].get("notes") == ""
    assert len(event_dicts) == 2


@use_icalbuddy_output("multiple_days")
def test_multiple_days():
    """should parse single event spanning multiple days from icalBuddy output"""
    calendar = IcalBuddyCalendar()
    event_dicts = calendar.get_event_dicts()
    assert event_dicts[0]["title"] == "Multi-Day Meeting"
    assert event_dicts[0]["startDate"] == "2023-06-26T09:00"
    assert event_dicts[0]["endDate"] == "2023-06-27T15:30"
    assert event_dicts[0].get("location") == "https://zoom.us/j/123456"
    assert event_dicts[0].get("notes") == ""
    assert len(event_dicts) == 1


@use_icalbuddy_output("single_day_all_day")
def test_single_day_all_day():
    """should parse all-day event (on a single day) from icalBuddy output"""
    calendar = IcalBuddyCalendar()
    event_dicts = calendar.get_event_dicts()
    assert event_dicts[0]["title"] == "Single-Day All-Day Meeting"
    assert event_dicts[0]["startDate"] == "2023-06-21T00:00"
    assert event_dicts[0]["endDate"] == "2023-06-21T23:59"
    assert event_dicts[0].get("location") == "https://zoom.us/j/123456"
    assert event_dicts[0].get("notes") == ""
    assert len(event_dicts) == 1


@use_icalbuddy_output("multiple_days_all_day")
def test_multiple_days_all_day():
    """should parse all-day event (over multiple days) from icalBuddy output"""
    calendar = IcalBuddyCalendar()
    event_dicts = calendar.get_event_dicts()
    assert event_dicts[0]["title"] == "Multi-Day All-Day Meeting"
    assert event_dicts[0]["startDate"] == "2023-06-28T00:00"
    assert event_dicts[0]["endDate"] == "2023-06-30T23:59"
    assert event_dicts[0].get("location") == "https://zoom.us/j/123456"
    assert event_dicts[0].get("notes") == ""
    assert len(event_dicts) == 1


@use_icalbuddy_output("missing_times")
@freeze_time("2023-09-21 9:00:00")
def test_missing_times():
    """should gracefully handle missing times in calendar events"""
    calendar = IcalBuddyCalendar()
    event_dicts = calendar.get_event_dicts()
    assert event_dicts[0]["title"] == "Vocabulary 9/25 [Weldon - SCIENCE-GRADE 7 - S1]"
    assert event_dicts[0]["startDate"] == "2023-09-21T09:00"
    assert event_dicts[0]["endDate"] == "2023-09-21T09:00"
    assert event_dicts[0].get("location") == "https://zoom.us/j/123456"
    assert event_dicts[0].get("notes") == ""
    assert len(event_dicts) == 2
