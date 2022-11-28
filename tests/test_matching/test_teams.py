#!/usr/bin/env python3

import json
import unittest

from ocu.event import Event


tc = unittest.TestCase()


def test_teams():
    with open('tests/sample_events/teams.json', 'r') as json_file:
        raw_data = json.load(json_file)
        event = Event(raw_data)
        tc.assertEqual(
            event.conference_url,
            'https://teams.microsoft.com/l/meetup-join/12%3ameeting_A1b2C3%40thread.v2/0?context=%7b%22Tid')  # noqa
