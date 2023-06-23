#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ocu.calendars.applescript_calendar import AppleScriptCalendar
from ocu.calendars.icalbuddy_calendar import IcalBuddyCalendar


if IcalBuddyCalendar.is_icalbuddy_installed():
    calendar = IcalBuddyCalendar()
else:
    calendar = AppleScriptCalendar()
