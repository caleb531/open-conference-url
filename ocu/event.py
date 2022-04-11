#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from datetime import datetime

from ocu.calendar import calendar
from ocu.prefs import prefs


# The object representation of a calendar event, with all of its fields
# normalized and ready to be consumed by the list_events module
class Event(object):

    # Initialize an Event object by parsing a dictionary of raw event
    # properties as input; this dictionary is constructed and outputted by the
    # get-calendar-events AppleScript
    def __init__(self, raw_data):
        self.raw_data = raw_data
        self.title = raw_data.get('title')
        self.start_datetime = self.parse_start_datetime()
        if self.start_datetime.hour == 0 and self.start_datetime.minute == 0:
            self.is_all_day = True
            # Set the time of all-day events to the system's current time, to
            # ensure that those events always show
            self.start_datetime = datetime.now()
        else:
            self.is_all_day = False
        self.conference_url = self.parse_conference_url()
        # Bypass the browser when opening Zoom URLs, for convenience
        if self.is_zoom_url(self.conference_url) and prefs['use_direct_zoom']:
            self.conference_url = self.convert_zoom_url_to_direct(
                self.conference_url)

    # Return True if the given URL is a Zoom URL; return False otherwise
    def is_zoom_url(self, url):
        if not url:
            return False
        matches = re.search(r'https://([\w\-]+\.)?(zoom.us)', url)
        return bool(matches)

    # Convert an https: Zoom URL to the zoommtg: protocol which will allow it
    # to bypass a web browser to open directly in the Zoom application
    def convert_zoom_url_to_direct(self, zoom_url):
        zoom_url = re.sub(r'https://', 'zoommtg://', zoom_url)
        zoom_url = re.sub(r'/j/', '/join?action=join&confno=', zoom_url)
        zoom_url = re.sub(r'\?pwd=', '&pwd=', zoom_url)
        return zoom_url

    # Parse and return the date and time the event starts
    def parse_start_datetime(self):
        if self.raw_data.get('isAllDay') == 'true':
            # Handle all-day events
            return datetime.strptime(
                self.raw_data['startDate'],
                '{}T00:00'.format(calendar.date_format))
        else:
            # Handle events with specific start time
            return datetime.strptime(
                self.raw_data['startDate'],
                '{}T{}'.format(
                    calendar.date_format, calendar.time_format))

    # Return the conference URL for the given event, whereby some services have
    # higher precedence than others (e.g. always prefer Zoom URLs over Google
    # Meet URLs if both are present)
    def parse_conference_url(self):
        event_search_str = '\n'.join(self.raw_data.values())
        for domain in prefs['conference_domains']:
            matches = re.search(
                r'https://([\w\-]+\.)*({domain})/([^><"\']+?)(?=([\s><"\']|$))'.format(domain=domain),  # noqa
                event_search_str)
            if matches:
                return matches.group(0)
        return None
