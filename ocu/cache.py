#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json
import os
import os.path
import re
import subprocess
from datetime import datetime

from ocu.prefs import prefs


# Manages storage and retrieval of cached data for this workflow (e.g. calendar
# events, date/time of last run, etc.)
class Cache(object):

    # The unique bundle ID of the workflow
    workflow_bundle_id = 'com.calebevans.openconferenceurl'

    # The directory for (volatile) Alfred workflow cache entries
    cache_dir = os.path.expanduser(os.path.join(
        '~', 'Library', 'Caches', 'com.runningwithcrayons.Alfred',
        'Workflow Data', workflow_bundle_id))

    # The file path to the cache store
    cache_path = os.path.join(cache_dir, 'event-cache.json')

    # The directory containing the workflow's source files
    code_dir = os.path.dirname(os.path.realpath(__file__))

    # The path to the icalBuddy binary used for retrieving calendar data
    binary_path = os.path.join(code_dir, 'icalBuddy')

    def __init__(self):
        self.create_cache_dir()
        try:
            return self.read()
        except (IOError, RuntimeError):
            self.refresh()
            return self.read()

    # Return the current date as a string (for comparison against the date the
    # cache was last refreshed)
    def get_current_date(self):
        return datetime.now().strftime(prefs.date_format)

    # Read the cache JSON into memory
    def read(self):
        with open(self.cache_path, 'r') as cache_file:
            # Make all JSON keys accessible as instance attributes
            self.__dict__.update(json.load(cache_file))
        # Invalidate the cache at the start of every day
        if self.last_refresh_date != self.get_current_date():
            # Raising a RuntimeError will run the exception-handling code in
            # the constructor
            raise RuntimeError('Last refresh date is too old')

    # Create the cache directory if it doesn't already exist
    def create_cache_dir(self):
        try:
            os.makedirs(self.cache_dir)
        except OSError:
            pass

    # Return True if the given key exists in the cache; otherwise, return false
    def has(self, key):
        if self.__dict__[key]:
            return True
        else:
            return False

    # Return True if the given key exists in the cache; otherwise, return false
    def get(self, key):
        return self.__dict__[key]

    # Store the given value at the specified key in the cache
    def set(self, key, value):
        self.__dict__[key] = value
        with open(self.cache_path, 'w') as cache_file:
            json.dump(self.__dict__, cache_file,
                      indent=2, separators=(',', ': '))

    # Refresh latest calendar event data
    def refresh(self):
        event_blobs = re.split(r'(?:^|\n)• ', subprocess.check_output([
            self.binary_path,
            # Override the default date/time formats
            '--dateFormat',
            prefs.date_format,
            '--noRelativeDates',
            '--timeFormat',
            prefs.time_format,
            # remove parenthetical calendar names from event titles
            '--noCalendarNames',
            # Only include the following fields and enforce their order
            '--includeEventProps',
            ','.join(prefs.event_props),
            '--propertyOrder',
            ','.join(prefs.event_props),
            'eventsToday+{}'.format(prefs.offset_from_today)
        ]).decode('utf-8'))
        # The first element will always be an empty string, because the bullet
        # point we are splitting on is not a delimiter
        event_blobs.pop(0)
        # Detect when cache data has been updated, or if it has remained the
        # same (the event blobs are the only data worth checking)
        if self.get('event_blobs') != event_blobs:
            # Cache event blob data for next execution of workflow
            self.set('event_blobs', event_blobs)
            # Cache event blob data for next execution of workflow
            self.set('last_refresh_date', self.get_current_date())
            has_cache_updated = True
        else:
            has_cache_updated = False
        return has_cache_updated

    # Queue a refresh of the cache (this will cause Alfred to refresh the
    # workflow cache in the background without blocking the execution of this
    # script)
    def queue_refresh(self):
        subprocess.call([
            '/usr/bin/osascript',
            os.path.join(self.code_dir, 'queue_cache_refresh.applescript')
        ])


cache = Cache()
