#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import os.path
import subprocess


# An abstraction class between this workflow and the program that retrieves the
# calendar data (in this case, get-calendar-events.applescript)
class Calendar(object):

    # The date and time used internally to display and parse raw event data;
    # ***do not change this***
    date_format = '%Y-%m-%d'
    time_format = '%H:%M'
    # The path to the AppleScript used for fetching calendar event data
    script_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'get-calendar-events.applescript')

    # Retrieve the raw event blob data from the AppleScript
    def get_event_blobs(self, calendar_names=None):
        if not calendar_names:
            calendar_names = []
        return json.loads(subprocess.check_output([
            'osascript',
            self.script_path,
            *calendar_names
        ]).decode('utf-8'))


calendar = Calendar()
