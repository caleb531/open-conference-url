#!/usr/bin/env python3

import itertools
import json
import os
import os.path
import unittest

from ocu.event import Event
from tests.utilities import use_env


EVENT_DATA_DIR = os.path.join('tests', 'sample_events')


case = unittest.TestCase()


def get_test_data():
    """
    Retrieve a dictionary of information pertaining to the various test cases to
    test manually or generate automatically
    """
    test_data_path = os.path.join('tests', 'test_data.json')
    with open(test_data_path, 'r') as test_data_file:
        return json.load(test_data_file)


def get_event_from_file(file_name):
    """Parse a JSON object from the specified file into an Event object"""
    with open(os.path.join(EVENT_DATA_DIR, file_name), 'r') as json_file:
        raw_data = json.load(json_file)
        return Event(raw_data)


def get_event_with_defaults(**kwargs):
    """
    Build a new Event object from the given service dictionary, with any
    additional parameters
    """
    return Event({
        'title': kwargs.get('title', 'Meeting'),
        'startDate': kwargs.get('startDate', '2011-10-16T08:00'),
        'endDate': kwargs.get('endDate', '2011-10-16T09:00'),
        **kwargs
    })


def generate_location_test_cases(service):
    """Should parse conference URLs in the 'Location' field of the event"""
    for correct_url in service['example_correct_urls']:
        event = get_event_with_defaults(
            title='{} Call'.format(service["name"]),
            location=correct_url)
        yield case.assertEqual, event.conference_url, correct_url


def generate_notes_test_cases(service):
    """
    Should parse all permutations of correct conference URL in Notes field
    containing other URLs which should be ignored
    """
    # TODO
    for correct_url in service['example_correct_urls']:
        base_permutation = service['example_incorrect_urls'] + [correct_url]
        permutations = itertools.permutations(base_permutation)
        for permutation in permutations:
            for start_token, end_token in ('""', '\'\'', '<>'):  # TODO
                wrapped_urls = [(start_token + url + end_token)
                                for url in permutation]
                event = get_event_with_defaults(
                    title='{} Call'.format(service["name"]),
                    notes=' '.join(wrapped_urls)
                )
                yield case.assertEqual, event.conference_url, correct_url


def test_permutations():
    """
    Test all permutations of test cases that the workflow should correctly
    handle
    """
    test_data = get_test_data()
    for service in test_data['services']:
        yield from generate_location_test_cases(service)
        yield from generate_notes_test_cases(service)


@use_env('use_direct_zoom', 'true')
def test_zoom_direct():
    event = get_event_from_file('zoom.json')
    case.assertEqual(
        event.conference_url,
        'zoommtg://zoom.us/join?action=join&confno=123456&pwd=AiBjCk')


def test_excluding_non_conference_urls():
    event = get_event_with_defaults(location='https://github.com')
    case.assertEqual(event.conference_url, None)
