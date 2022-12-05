#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re


# A utility class for retrieving user preferences for this workflow; all
# preferences are stored as Alfred Workflow variables, and are exposed to the
# scripting runtime as environment variables
class Prefs(object):

    def __init__(self):
        self.pref_field_types = {
            'conference_domains': self.convert_str_to_list,
            'calendar_names': self.convert_str_to_list,
            'event_time_threshold_mins': int,
            'use_direct_zoom': self.convert_str_to_bool,
            'use_direct_msteams': self.convert_str_to_bool,
            'time_system': str
        }

    # Convert a comma-separated string of values to a proper list type
    def convert_str_to_list(self, value):
        value_list = re.split(r'\s*,\s*', value.strip())
        if value_list == ['']:
            return []
        else:
            return value_list

    # Convert a boolean-like string value (like 'Yes' or 'True') to a proper
    # boolean
    def convert_str_to_bool(self, value):
        return value.lower().strip() in ('1', 'y', 'yes', 'true', 't')

    def __getitem__(self, pref_name):
        return self.pref_field_types[pref_name](os.environ[pref_name])


prefs = Prefs()
