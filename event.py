#!/usr/bin/env python3

import re
from datetime import datetime


class Event(object):

    # A list of conference domains to look for, in order of precedence
    conference_domains = [
        # Zoom
        'zoom.us',
        # Google Meet
        'google.com',
        # UberConference
        'uberconference.com',
        # Microsoft Teams
        'microsoft.com',
        # GoToMeeting
        'gotomeeting.com'
    ]

    # Initialize an Event object by parsing an event blob string as input; the
    # event blob represents raw event data from icalBuddy, which has a very
    # particular string format and must be parsed with regular expressions
    def __init__(self, event_blob):
        self.blob = event_blob
        self.title = self.parse_title()
        self.start_datetime = self.parse_start_datetime()
        self.conference_url = self.parse_conference_url()

    # Parse and return the display title of the event from the blob string
    def parse_title(self):
        return re.search(r'^(.*?)\n', self.blob).group(1)

    # Parse and return the date and time the event starts
    def parse_start_datetime(self):
        start_datetime_matches = re.search(
            r'\s{4}((.*?) at ([^-]+))', self.blob)
        return datetime.strptime(
            start_datetime_matches.group(1).strip(),
            '{} at {}'.format('%Y-%m-%d', '%H:%M')).astimezone()

    # Return the conference URL for the given event, whereby some services have
    # higher precedence than others (e.g. always prefer Zoom URLs over Google
    # Meet URLs if both are present)
    def parse_conference_url(self):
        for domain in self.conference_domains:
            matches = re.search(
                r'https://(\w+\.)?({domain})/([^><"\']+?)(?=([\s><"\']|$))'.format(domain=domain),
                self.blob)
            if matches:
                return matches.group(0)
        return None
