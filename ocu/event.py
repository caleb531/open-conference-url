#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from datetime import datetime

from ocu.prefs import prefs


class Event(object):

    # Initialize an Event object by parsing an event blob string as input; the
    # event blob represents raw event data from icalBuddy, which has a very
    # particular string format and must be parsed with regular expressions
    def __init__(self, event_blob):
        self.blob = event_blob
        self.title = self.parse_title()
        self.start_datetime = self.parse_start_datetime()
        if self.start_datetime.hour == 0 and self.start_datetime.minute == 0:
            self.is_all_day = True
            # Set the time of all-day events to the system's current time, to
            # ensure that those events always show
            self.start_datetime = datetime.now()
        else:
            self.is_all_day = False
        self.conference_url = self.parse_conference_url()

    # Parse and return the display title of the event from the blob string
    def parse_title(self):
        return re.search(r'^(.*?)\n', self.blob).group(1)

    # Parse and return the date and time the event starts
    def parse_start_datetime(self):
        start_datetime_matches = re.search(
            r'\s{4}(([\d\-\/]+)( at ([^-]+))?)', self.blob)
        if start_datetime_matches.group(3):
            # Handle events with specific start time
            return datetime.strptime(
                start_datetime_matches.group(1).strip(),
                '{} at {}'.format(
                    prefs.date_format, prefs.time_format))
        else:
            # Handle all-day events
            return datetime.strptime(
                start_datetime_matches.group(1).strip(),
                prefs.date_format)

    # Return the conference URL for the given event, whereby some services have
    # higher precedence than others (e.g. always prefer Zoom URLs over Google
    # Meet URLs if both are present)
    def parse_conference_url(self):
        for domain in prefs.conference_domains:
            matches = re.search(
                r'https://(\w+\.)?({domain})/([^><"\']+?)(?=([\s><"\']|$))'.format(domain=domain),
                self.blob)
            if matches:
                return matches.group(0)
        return None
