#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ocu.calendars.applescript_calendar import AppleScriptCalendar
from ocu.calendars.icalbuddy_calendar import IcalBuddyCalendar


# Retrieve the correct calendar to use
def get_calendar():
    if IcalBuddyCalendar.is_icalbuddy_installed():
        return IcalBuddyCalendar()
    else:
        return AppleScriptCalendar()
