#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import os.path
import re
import subprocess
from ocu.calendars.base_calendar import BaseCalendar


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
        os.path.join(os.path.dirname(os.path.realpath(__file__)), 'icalBuddy')
    ]

    # Retrieve the first available path to the binary among a list of possible
    # paths (this allows us to prefer the already-signed Homebrew icalBuddy
    # binary over our workflow-bundled binary that requires explicit permission
    # to execute)
    def get_binary_path(self):
        for binary_path in self.binary_paths:
            if os.path.exists(binary_path):
                return binary_path
        return binary_path[-1]

    # Retrieve the raw event strings from icalBuddy
    def get_event_strs(self):
        return re.split(r'(?:^|\n)• ', subprocess.check_output([
            self.get_binary_path(),
            # Override the default date/time formats
            '--dateFormat',
            self.date_format,
            '--noRelativeDates',
            '--timeFormat',
            self.time_format,
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
