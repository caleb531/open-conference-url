#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import os.path
import re
import subprocess
from ocu.event import Event
from ocu.calendars.base_calendar import BaseCalendar
from ocu.prefs import prefs


# A Calendar class for retrieving event data via AppleScript
class IcalBuddyCalendar(BaseCalendar):

    # The properties (in order) that icalBuddy must output; changing this order
    # will break the parsing of event data
    event_props = ('title', 'datetime', 'location', 'url', 'notes')
    # All possible paths to check for the icalBuddy binary that's used for
    # retrieving calendar data; the first path that exists on the user's system
    # is the one that's used
    binary_paths = [
        os.path.join(os.sep, 'opt', 'homebrew', 'bin', 'icalBuddy'),
        os.path.join(os.sep, 'usr', 'local', 'bin', 'icalBuddy'),
    ]

    # Retrieve the first available path to the binary among a list of possible
    # paths (this allows us to prefer the already-signed Homebrew icalBuddy
    # binary over our workflow-bundled binary that requires explicit permission
    # to execute)
    @classmethod
    def get_binary_path(cls):
        for binary_path in cls.binary_paths:
            if os.path.exists(binary_path):
                return binary_path
        return None

    # A simple utility method to check if icalBuddy is currently installed on
    # the user's system
    @classmethod
    def is_icalbuddy_installed(cls):
        return bool(cls.get_binary_path()) and prefs['use_icalbuddy']

    # Retrieve the raw event strings from icalBuddy
    def get_raw_event_strs(self):
        event_blobs = re.split(r'(?:^|\n)• ', subprocess.check_output([
            self.__class__.get_binary_path(),
            # Override the default date/time formats
            '--dateFormat',
            Event.date_format,
            '--noRelativeDates',
            '--timeFormat',
            Event.time_format,
            # remove parenthetical calendar names from event titles
            '--noCalendarNames',
            # Only include the following fields and enforce their order
            '--includeEventProps',
            ','.join(self.event_props),
            '--propertyOrder',
            ','.join(self.event_props),
            # If we omit the '+0', the icalBuddy output does not include the
            # current date, which our parsing logic assumes is present
            'eventsToday+0'
        ]).decode('utf-8'))
        # The first element will always be an empty string, because the bullet
        # point we are splitting on is not a delimiter
        event_blobs.pop(0)
        return event_blobs

    # Because parsing date/time information from an icalBuddy event string is
    # more involved, we have a dedicated method for it
    def parse_date_info(self, raw_event_str):
        date_matches_single_day = re.search(
            r'\n\s{4}(.*?) at (.*?) - (.*?)\n',
            raw_event_str)
        date_matches_multi_day = re.search(
            r'\n\s{4}(.*?) at (.*?) - (.*?) at (.*?)\n',
            raw_event_str)
        if date_matches_multi_day:
            return {
                'start_date': date_matches_multi_day.group(1),
                'start_time': date_matches_multi_day.group(2),
                'end_date': date_matches_multi_day.group(3),
                'end_time': date_matches_multi_day.group(4)
            }
        else:
            return {
                'start_date': date_matches_single_day.group(1),
                'start_time': date_matches_single_day.group(2),
                'end_date': date_matches_single_day.group(1),
                'end_time': date_matches_single_day.group(3)
            }

    # Parse a string of raw event data into a dictionary which can be consumed
    # by the Event class
    def convert_raw_event_str_to_dict(self, raw_event_str):
        title_matches = re.search(
            r'^(.*?)\n',
            raw_event_str)
        date_info = self.parse_date_info(raw_event_str)
        location_matches = re.search(
            r'\n\s{4}location: (.*?)\n',
            raw_event_str)
        notes_matches = re.search(
            r'\n\s{4}notes: ((?:.|\n)*)$',
            raw_event_str)
        return {
            # 'raw_data': raw_event_str,
            'title': title_matches.group(1) if title_matches else '',
            'startDate': '{}T{}'.format(
                date_info['start_date'],
                date_info['start_time']),
            'endDate': '{}T{}'.format(
                date_info['end_date'],
                date_info['end_time']),
            'location': location_matches.group(1) if location_matches else '',
            'notes': notes_matches.group(1) if notes_matches else ''
        }

    # Transform the raw event data into a list of dictionaries that are
    # consumable by the Event class
    def get_event_dicts(self):
        return [self.convert_raw_event_str_to_dict(raw_event_str)
                for raw_event_str in self.get_raw_event_strs()]