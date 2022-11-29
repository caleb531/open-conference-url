#!/usr/bin/env python3

import itertools
import json
import os
import os.path
import unittest

from ocu.event import Event
from tests.utilities import use_env


# The supported start/end tokens that a conference URL could potentially be
# wrapped in
URL_TOKENS = (
    ('\'', '\''),
    ('"', '"'),
    ('<', '>')
)

case = unittest.TestCase()


def get_test_data():
    """
    Retrieve a dictionary of information pertaining to the various test cases to
    test manually or generate automatically
    """
    test_data_path = os.path.join('tests', 'test_data.json')
    with open(test_data_path, 'r') as test_data_file:
        return json.load(test_data_file)


def get_event_with_defaults(title='Meeting',
                            startDate='2011-10-16T08:00',
                            endDate='2011-10-16T09:00',
                            location='',
                            notes=''):
    """
    Build a new Event object from the given service dictionary, with any
    additional parameters
    """
    return Event({
        'title': title,
        'startDate': startDate,
        'endDate': endDate,
        'location': location,
        'notes': notes
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
    for correct_url in service['example_correct_urls']:
        base_permutation = service['example_incorrect_urls'] + [correct_url]
        permutations = itertools.permutations(base_permutation)
        for permutation in permutations:
            for start_token, end_token in URL_TOKENS:
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


def test_zoom_direct():
    """Should convert Zoom https: URLs to zoommtg: URLs if enabled"""
    event_data = get_test_data()
    zoom_data = [service for service in event_data['services']
                 if service['name'] == 'Zoom'][0]
    with use_env('use_direct_zoom', 'true'):
        for correct_url in zoom_data['example_correct_urls']:
            event = get_event_with_defaults(notes=correct_url)
            direct_zoom_url = event.convert_zoom_url_to_direct(event.conference_url)
            yield case.assertEqual, event.conference_url, direct_zoom_url


def test_excluding_non_conference_urls():
    """
    Should never match non-conference URLs even if they are the only URLs
    present
    """
    event = get_event_with_defaults(location='https://github.com')
    case.assertEqual(event.conference_url, None)
