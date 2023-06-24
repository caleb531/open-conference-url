#!/usr/bin/env python3

import unittest

from ocu.calendars.icalbuddy_calendar import IcalBuddyCalendar
from tests.decorators import use_icalbuddy_output

case = unittest.TestCase()


@use_icalbuddy_output('single_event')
def test_single_event():
    calendar = IcalBuddyCalendar()
    event_dicts = calendar.get_event_dicts()
    case.assertEqual(event_dicts[0]['title'], 'WWDC 2022 Keynote')
    case.assertEqual(event_dicts[0]['startDate'], '2022-06-06T10:00')
    case.assertEqual(event_dicts[0]['endDate'], '2022-06-06T12:15')
    case.assertEqual(event_dicts[0]['location'], 'https://apple.zoom.us/j/123456')
    case.assertEqual(event_dicts[0]['notes'], '')
    case.assertEqual(len(event_dicts), 1)


@use_icalbuddy_output('multiple_events')
def test_multiple_events():
    calendar = IcalBuddyCalendar()
    event_dicts = calendar.get_event_dicts()
    case.assertEqual(event_dicts[0]['title'], 'WWDC 2023 Keynote')
    case.assertEqual(event_dicts[0]['startDate'], '2023-06-05T10:00')
    case.assertEqual(event_dicts[0]['endDate'], '2023-06-05T12:15')
    case.assertEqual(event_dicts[0]['location'], 'https://apple.zoom.us/j/123456')
    case.assertEqual(event_dicts[0]['notes'], '')
    case.assertEqual(event_dicts[1]['title'], 'WWDC 2023 State of the Platform')
    case.assertEqual(event_dicts[1]['startDate'], '2023-06-05T13:00')
    case.assertEqual(event_dicts[1]['endDate'], '2023-06-05T14:30')
    case.assertEqual(event_dicts[1]['location'], 'https://apple.zoom.us/j/789012')
    case.assertEqual(event_dicts[1]['notes'], '')
    case.assertEqual(len(event_dicts), 2)
