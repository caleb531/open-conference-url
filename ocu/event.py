#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from datetime import datetime
from operator import itemgetter
from urllib.parse import urlparse

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
        # Bypass the browser when opening Zoom Join URLs, if enabled
        if self.__class__.is_convertible_zoom_url(self.conference_url):
            self.conference_url = self.__class__.convert_zoom_url_to_direct(
                self.conference_url)
        # Bypass the browser when opening MS Teams Meeting URLs, if enabled
        if self.__class__.is_convertible_msteams_url(self.conference_url):
            self.conference_url = self.__class__.convert_msteams_url_to_direct(
                self.conference_url)

    # Return True if the given URL is a Zoom URL that can be converted to a
    # direct link (via the zoommtg:// protocol); return False otherwise
    @staticmethod
    def is_convertible_zoom_url(url):
        if not url or not prefs['use_direct_zoom']:
            return False
        matches = re.search(r'https://([\w\-]+\.)?(zoom.us)/j/', url)
        return bool(matches)

    # Return True if the given URL is a Microsoft Teams URL that can be
    # converted to a direct link (via the msteams:// protocol); return False
    # otherwise
    @staticmethod
    def is_convertible_msteams_url(url):
        if not url or not prefs['use_direct_msteams']:
            return False
        return 'https://teams.microsoft.com/' in url

    # Convert an https: Zoom URL to the zoommtg: protocol which will allow it
    # to bypass a web browser to open directly in the Zoom application
    @staticmethod
    def convert_zoom_url_to_direct(zoom_url):
        zoom_url = re.sub(r'https://', 'zoommtg://', zoom_url)
        zoom_url = re.sub(r'/j/', '/join?action=join&confno=', zoom_url)
        zoom_url = re.sub(r'\?pwd=', '&pwd=', zoom_url)
        return zoom_url

    # Convert an https: Microsoft Teams URL to the msteams: protocol which will
    # allow it to bypass a web browser to open directly in the Microsoft Teams
    # application
    @staticmethod
    def convert_msteams_url_to_direct(msteams_url):
        return msteams_url.replace('https://', 'msteams://')

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

    # Return true if the given domain (e.g. "us02web.zoom.us") matches the given
    # pattern (e.g. "*.zoom.us")
    def does_domain_match_pattern(self, domain, pattern):
        domain_patt = re.sub(r'\\\*', r'([a-z0-9\-]+)', re.escape(pattern))
        matches = re.match(domain_patt, domain)
        if matches:
            return True
        else:
            return False

    # Compute a numeric score to represent the likelihood that this is the
    # conference domain we want
    def get_url_score(self, url):
        if re.search(r'\.[a-z]{3}$', url):
            return -1
        url_parts = urlparse(url)
        for i, domain_patt in enumerate(prefs['conference_domains']):
            if self.does_domain_match_pattern(url_parts.hostname, domain_patt):
                return 10 * (len(prefs['conference_domains']) - i)
        return -1

    # Return the conference URL for the given event, whereby some services have
    # higher precedence than others (e.g. always prefer Zoom URLs over Google
    # Meet URLs if both are present)
    def parse_conference_url(self):
        event_search_str = '\n'.join(self.raw_data.values())
        urls = re.findall(r'https://(?:.*?)(?=[\s><"\']|$)', event_search_str)
        if not urls:
            return None
        url_pairs = [(url, self.get_url_score(url)) for url in urls]
        filtered_url_pairs = [(url, score)
                              for url, score in url_pairs if score >= 0]
        if not filtered_url_pairs:
            return None
        return max(filtered_url_pairs, key=itemgetter(1))[0]
