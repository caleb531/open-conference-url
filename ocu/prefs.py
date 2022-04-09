#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import os.path


# The user's preferences for this workflow
class Prefs(object):

    # The date and time used internally to display and parse icalBuddy event
    # output; ***do not change this***
    date_format = '%Y-%m-%d'
    time_format = '%H:%M'
    # The properties (in order) that icalBuddy must output; changing this order
    # will break the parsing of event data
    event_props = ('title', 'datetime', 'location', 'url', 'notes')
    pref_field_types = {
        'conference_domains': lambda value: value.split(','),
        'event_time_threshold_mins': int,
        'offset_from_today': int,
        'use_direct_zoom': lambda value: value.lower() == 'yes'
    }

    def __getitem__(self, name):
        return self.pref_field_types[name.lower()](os.environ[name.lower()])


prefs = Prefs()
