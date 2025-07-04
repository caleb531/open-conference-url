#!/usr/bin/env python3

import itertools
import json
import os
import os.path
import re
import unittest

from ocu.event import Event
from tests.utils import use_env

# The supported start/end tokens that a conference URL could potentially be
# wrapped in
URL_TOKENS = (("'", "'"), ('"', '"'), ("<", ">"), ("\n", "\n"), (".", "."), (";", ";"))


class TestMatching(unittest.TestCase):
    def get_test_data(self):
        """
        Retrieve a dictionary of information pertaining to the various test cases to
        test manually or generate automatically
        """
        test_data_path = os.path.join("tests", "test_data.json")
        with open(test_data_path, "r") as test_data_file:
            return json.load(test_data_file)

    def get_event_with_defaults(
        self,
        title="Meeting",
        startDate="2011-10-16T08:00",
        endDate="2011-10-16T09:00",
        location="",
        notes="",
    ):
        """
        Build a new Event object from the given service dictionary, with any
        additional parameters
        """
        return Event(
            {
                "title": title,
                "startDate": startDate,
                "endDate": endDate,
                "location": location,
                "notes": notes,
            }
        )

    def generate_location_test_cases(self, service):
        """Should parse conference URLs in the 'Location' field of the event"""
        for correct_url in service["example_correct_urls"]:
            event = self.get_event_with_defaults(
                title="{} Call".format(service["name"]), location=correct_url
            )
            yield self.assertEqual, event.conference_url, correct_url

    def generate_notes_test_cases(self, service):
        """
        Should parse all permutations of correct conference URL in Notes field
        containing other URLs which should be ignored
        """
        for correct_url in service["example_correct_urls"]:
            base_permutation = service["example_incorrect_urls"] + [correct_url]
            permutations = itertools.permutations(base_permutation)
            for permutation in permutations:
                for start_token, end_token in URL_TOKENS:
                    wrapped_urls = [
                        (start_token + url + end_token) for url in permutation
                    ]
                    event = self.get_event_with_defaults(
                        title="{} Call".format(service["name"]),
                        notes=" ".join(wrapped_urls),
                    )
                    yield self.assertEqual, event.conference_url, correct_url

    def test_permutations(self):
        """
        Test all permutations of test cases that the workflow should correctly
        handle
        """
        original_conference_domains = re.split(
            r"\s*,\s*", os.environ["conference_domains"]
        )
        test_data = self.get_test_data()
        for delimiter in test_data["conference_domain_delimiters"]:
            with use_env(
                "conference_domains", delimiter.join(original_conference_domains)
            ):
                for service in test_data["services"]:
                    yield from self.generate_location_test_cases(service)
                    yield from self.generate_notes_test_cases(service)

    def convert_zoom_url_to_direct(self, zoom_url):
        """
        Convert the given https: Zoom URL to a zoommtg: URL; a method for this
        already exists in the Event class, however we have duplicated it here to
        decouple any expected test output from the internal implementation of Event
        """
        zoom_url = re.sub(r"https://", "zoommtg://", zoom_url)
        zoom_url = re.sub(r"/j/", "/join?action=join&confno=", zoom_url)
        zoom_url = re.sub(r"\?pwd=", "&pwd=", zoom_url)
        return zoom_url

    def convert_msteams_url_to_direct(self, msteams_url):
        """
        Convert the given https: Microsoft Teams URL to a msteams: URL; a method for
        this already exists in the Event class, however we have duplicated it here
        to decouple any expected test output from the internal implementation of
        Event
        """
        return msteams_url.replace("https://", "msteams://")

    @use_env("use_direct_zoom", "true")
    def test_zoom_direct(self):
        """Should convert Zoom https: URLs to zoommtg: URLs if enabled"""
        event_data = self.get_test_data()
        zoom_data = [
            service for service in event_data["services"] if service["name"] == "Zoom"
        ][0]
        for correct_url in zoom_data["example_correct_urls"]:
            # Only /j/ URLs can be converted to the zoommtg: protocol; meeting URLs
            # like the personalized /my/ URLs are unable to be converted
            if "/j/" in correct_url:
                event = self.get_event_with_defaults(notes=correct_url)
                direct_zoom_url = self.convert_zoom_url_to_direct(correct_url)
                yield self.assertEqual, event.conference_url, direct_zoom_url

    @use_env("use_direct_msteams", "true")
    def test_msteams_direct(self):
        """Should convert MS Teams https: URLs to msteams: URLs if enabled"""
        event_data = self.get_test_data()
        msteams_data = [
            service
            for service in event_data["services"]
            if service["name"] == "Microsoft Teams"
        ][0]
        for correct_url in msteams_data["example_correct_urls"]:
            # Only /l/ URLs can be converted to the msteams: protocol
            if "/l/" in correct_url:
                event = self.get_event_with_defaults(notes=correct_url)
                direct_msteams_url = self.convert_msteams_url_to_direct(correct_url)
                yield self.assertEqual, event.conference_url, direct_msteams_url

    def test_non_conference_urls(self):
        """
        Should never match non-conference URLs even if they are the only URLs
        present
        """
        event = self.get_event_with_defaults(location="https://github.com")
        self.assertEqual(event.conference_url, None)

    def test_no_urls(self):
        """
        Should handle events without any URLs whatsoever
        """
        event = self.get_event_with_defaults(notes="")
        self.assertEqual(event.conference_url, None)
