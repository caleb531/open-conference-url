#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import os.path
import subprocess

from ocu.calendars.base_calendar import BaseCalendar
from ocu.prefs import prefs


# A Calendar class for retrieving event data via AppleScript
class AppleScriptCalendar(BaseCalendar):
    # The path to the AppleScript used for fetching calendar event data
    script_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "get-calendar-events.applescript"
    )

    # Retrieve the raw event attribute dictionaries from the AppleScript
    def get_event_dicts(self):
        return json.loads(
            subprocess.check_output(
                ["osascript", self.script_path, *prefs["calendar_names"]]
            ).decode("utf-8")
        )
