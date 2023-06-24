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
