#!/usr/bin/env python3

import itertools
import json
import os
import os.path
import re

import pytest

from ocu.event import Event
from tests.utils import use_env

# The supported start/end tokens that a conference URL could potentially be
# wrapped in
URL_TOKENS = (("'", "'"), ('"', '"'), ("<", ">"), ("\n", "\n"), (".", "."), (";", ";"))


def get_test_data():
    """Retrieve a dictionary of information for the various test cases."""
    test_data_path = os.path.join("tests", "test_data.json")
    with open(test_data_path, "r") as test_data_file:
        return json.load(test_data_file)


def get_event_with_defaults(
    title="Meeting",
    startDate="2011-10-16T08:00",
    endDate="2011-10-16T09:00",
    location="",
    notes="",
):
    """Build an Event object from the given service dictionary."""
    return Event(
        {
            "title": title,
            "startDate": startDate,
            "endDate": endDate,
            "location": location,
            "notes": notes,
        }
    )


def convert_zoom_url_to_direct(zoom_url):
    """Convert an https Zoom URL to a zoommtg URL."""
    zoom_url = re.sub(r"https://", "zoommtg://", zoom_url)
    zoom_url = re.sub(r"/j/", "/join?action=join&confno=", zoom_url)
    zoom_url = re.sub(r"\?pwd=", "&pwd=", zoom_url)
    return zoom_url


def convert_msteams_url_to_direct(msteams_url):
    """Convert an https Microsoft Teams URL to a msteams URL."""
    return msteams_url.replace("https://", "msteams://")


TEST_DATA = get_test_data()
SERVICES_BY_NAME = {service["name"]: service for service in TEST_DATA["services"]}


def _build_permutation_cases():
    cases = []
    for delimiter in TEST_DATA["conference_domain_delimiters"]:
        for service in TEST_DATA["services"]:
            service_name = service["name"]
            for correct_url in service["example_correct_urls"]:
                cases.append(
                    (
                        "location",
                        delimiter,
                        service_name,
                        correct_url,
                        correct_url,
                    )
                )
                base_permutation = service["example_incorrect_urls"] + [correct_url]
                for permutation in itertools.permutations(base_permutation):
                    for start_token, end_token in URL_TOKENS:
                        wrapped_urls = [
                            f"{start_token}{url}{end_token}" for url in permutation
                        ]
                        notes_value = " ".join(wrapped_urls)
                        cases.append(
                            (
                                "notes",
                                delimiter,
                                service_name,
                                notes_value,
                                correct_url,
                            )
                        )
    return cases


def _build_zoom_direct_cases():
    zoom_data = SERVICES_BY_NAME.get("Zoom", {"example_correct_urls": []})
    return [
        (url, convert_zoom_url_to_direct(url))
        for url in zoom_data["example_correct_urls"]
        if "/j/" in url
    ]


def _build_msteams_direct_cases():
    msteams_data = SERVICES_BY_NAME.get("Microsoft Teams", {"example_correct_urls": []})
    return [
        (url, convert_msteams_url_to_direct(url))
        for url in msteams_data["example_correct_urls"]
        if "/l/" in url
    ]


PERMUTATION_CASES = _build_permutation_cases()
ZOOM_DIRECT_CASES = _build_zoom_direct_cases()
MSTEAMS_DIRECT_CASES = _build_msteams_direct_cases()


def _get_conference_domains():
    return re.split(r"\s*,\s*", os.environ["conference_domains"])


@pytest.mark.parametrize(
    ("field", "delimiter", "service_name", "payload", "expected"),
    PERMUTATION_CASES,
)
def test_permutations(field, delimiter, service_name, payload, expected):
    """Test all permutations of supported conference URL scenarios."""
    original_conference_domains = _get_conference_domains()
    env_value = delimiter.join(original_conference_domains)
    with use_env("conference_domains", env_value):
        if field == "location":
            event = get_event_with_defaults(
                title=f"{service_name} Call",
                location=payload,
            )
        else:
            event = get_event_with_defaults(
                title=f"{service_name} Call",
                notes=payload,
            )
        assert event.conference_url == expected


@pytest.mark.parametrize(("correct_url", "expected_direct"), ZOOM_DIRECT_CASES)
@use_env("use_direct_zoom", "true")
def test_zoom_direct(correct_url, expected_direct):
    """Should convert Zoom https URLs to zoommtg URLs if enabled."""
    event = get_event_with_defaults(notes=correct_url)
    assert event.conference_url == expected_direct


@pytest.mark.parametrize(("correct_url", "expected_direct"), MSTEAMS_DIRECT_CASES)
@use_env("use_direct_msteams", "true")
def test_msteams_direct(correct_url, expected_direct):
    """Should convert MS Teams https URLs to msteams URLs if enabled."""
    event = get_event_with_defaults(notes=correct_url)
    assert event.conference_url == expected_direct


def test_non_conference_urls():
    """Should never match non-conference URLs even when alone."""
    event = get_event_with_defaults(location="https://github.com")
    assert event.conference_url is None


def test_no_urls():
    """Should handle events without any URLs whatsoever."""
    event = get_event_with_defaults(notes="")
    assert event.conference_url is None
