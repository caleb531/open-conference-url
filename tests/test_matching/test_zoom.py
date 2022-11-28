#!/usr/bin/env python3

import json
import unittest

from ocu.event import Event


tc = unittest.TestCase()


def test_zoom():
    with open('tests/sample_events/zoom.json', 'r') as json_file:
        raw_data = json.load(json_file)
        event = Event(raw_data)
        tc.assertEqual(
            event.conference_url,
            'https://zoom.us/l/123456?usp=sharing')  # noqa
