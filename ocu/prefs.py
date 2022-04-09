#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os


# The user's preferences for this workflow
class Prefs(object):

    pref_field_types = {
        'conference_domains': lambda value: value.split(','),
        'event_time_threshold_mins': int,
        'use_direct_zoom': lambda value: value.lower() in (
            '1',
            'y',
            'yes',
            'true',
            't'
        )
    }

    def __getitem__(self, name):
        return self.pref_field_types[name.lower()](os.environ[name.lower()])


prefs = Prefs()
