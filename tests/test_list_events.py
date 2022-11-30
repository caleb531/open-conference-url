#!/usr/bin/env python3

import json
import unittest

from freezegun import freeze_time

from ocu import list_events
from tests.utilities import redirect_stdout, use_event_blobs

case = unittest.TestCase()


@use_event_blobs([{
    'title': 'My Meeting',
    'startDate': '2022-10-16T08:00',
    'endDate': '2022-10-16T09:00',
    'notes': 'https://zoom.us/j/123456'
}])
@freeze_time('2022-10-16 07:55:00')
@redirect_stdout
def test_5mins_before(out, get_events_today):
    """Should list meeting starting in 5 minutes"""
    list_events.main()
    feedback = json.loads(out.getvalue())
    case.assertEqual(feedback['items'][0]['title'], 'My Meeting')
    case.assertEqual(feedback['items'][0]['subtitle'], '8:00am')
    case.assertEqual(len(feedback['items']), 1)


@use_event_blobs([{
    'title': 'My Meeting',
    'startDate': '2022-10-16T08:00',
    'endDate': '2022-10-16T09:00',
    'notes': 'https://zoom.us/j/123456'
}])
@freeze_time('2022-10-16 8:05:00')
@redirect_stdout
def test_5mins_after(out, get_events_today):
    """Should list meeting that started 5 minutes ago"""
    list_events.main()
    feedback = json.loads(out.getvalue())
    case.assertEqual(feedback['items'][0]['title'], 'My Meeting')
    case.assertEqual(feedback['items'][0]['subtitle'], '8:00am')
    case.assertEqual(len(feedback['items']), 1)


@use_event_blobs([{
    'title': 'My Meeting',
    'startDate': '2022-10-16T08:00',
    'endDate': '2022-10-16T09:00',
    'notes': 'https://zoom.us/j/123456'
}])
@freeze_time('2022-10-16 7:30:00')
@redirect_stdout
def test_before_window(out, get_events_today):
    """Should list all meetings if before next meeting's window"""
    list_events.main()
    feedback = json.loads(out.getvalue())
    case.assertEqual(feedback['items'][0]['title'], 'No Results')
    case.assertEqual(feedback['items'][1]['title'], 'My Meeting')
    case.assertEqual(len(feedback['items']), 2)


@use_event_blobs([{
    'title': 'My Meeting',
    'startDate': '2022-10-16T08:00',
    'endDate': '2022-10-16T09:00',
    'notes': 'https://zoom.us/j/123456'
}])
@freeze_time('2022-10-16 9:30:00')
@redirect_stdout
def test_after_window(out, get_events_today):
    """Should list all meetings if after next meeting's window"""
    list_events.main()
    feedback = json.loads(out.getvalue())
    case.assertEqual(feedback['items'][0]['title'], 'No Results')
    case.assertEqual(feedback['items'][1]['title'], 'My Meeting')
    case.assertEqual(len(feedback['items']), 2)


@use_event_blobs([{
    'title': 'All-Day Conference',
    'startDate': '2022-10-16T00:00',
    'isAllDay': 'true',
    'notes': 'https://zoom.us/j/123456'
}])
@freeze_time('2022-10-16 8:00:00')
@redirect_stdout
def test_all_day_standalone(out, get_events_today):
    """Should list all-day meetings by themselves"""
    list_events.main()
    feedback = json.loads(out.getvalue())
    case.assertEqual(feedback['items'][0]['title'], 'All-Day Conference')
    case.assertEqual(feedback['items'][0]['subtitle'], 'All-Day')
    case.assertEqual(len(feedback['items']), 1)


@use_event_blobs([
    {
        'title': 'All-Day Conference',
        'startDate': '2022-10-16T00:00',
        'isAllDay': 'true',
        'notes': 'https://zoom.us/j/123456'
    },
    {
        'title': 'Morning Scrum',
        'startDate': '2022-10-16T08:00',
        'endDate': '2022-10-16T09:00',
        'notes': 'https://zoom.us/j/123456'
    }
])
@freeze_time('2022-10-16 7:58:00')
@redirect_stdout
def test_all_day_mixed(out, get_events_today):
    """Should list all-day meetings alongside upcoming meetings"""
    list_events.main()
    feedback = json.loads(out.getvalue())
    case.assertEqual(feedback['items'][0]['title'], 'All-Day Conference')
    case.assertEqual(feedback['items'][0]['subtitle'], 'All-Day')
    case.assertEqual(feedback['items'][1]['title'], 'Morning Scrum')
    case.assertEqual(feedback['items'][1]['subtitle'], '8:00am')
    case.assertEqual(len(feedback['items']), 2)


@use_event_blobs([])
@freeze_time('2022-10-16 9:30:00')
@redirect_stdout
def test_no_events_for_today(out, get_events_today):
    """Should display no meetings if there are no events for today"""
    list_events.main()
    feedback = json.loads(out.getvalue())
    case.assertEqual(feedback['items'][0]['title'], 'No Results')
    case.assertEqual(len(feedback['items']), 1)
