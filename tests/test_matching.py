#!/usr/bin/env python3

import json
import os
import os.path
import unittest

from ocu.event import Event


EVENT_DATA_DIR = os.path.join('tests', 'sample_events')


tc = unittest.TestCase()


def get_event_from_file(file_name):
    with open(os.path.join(EVENT_DATA_DIR, file_name), 'r') as json_file:
        raw_data = json.load(json_file)
        return Event(raw_data)


def test_zoom():
    event = get_event_from_file('zoom.json')
    tc.assertEqual(
        event.conference_url,
        'https://zoom.us/l/123456?usp=sharing')


def test_meet():
    event = get_event_from_file('meet.json')
    tc.assertEqual(
        event.conference_url,
        'https://meet.google.com/abc-defg-hij')


def test_teams():
    event = get_event_from_file('teams.json')
    tc.assertEqual(
        event.conference_url,
        'https://teams.microsoft.com/l/meetup-join/12%3ameeting_A1b2C3%40thread.v2/0?context=%7b%22Tid')


def test_excluding_non_conference_urls():
    event = get_event_from_file('non-meeting.json')
    tc.assertEqual(event.conference_url, None)
