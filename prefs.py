#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json


# The user's preferences for this workflow
class Prefs(object):

    # The date and time used internally to display and parse icalBuddy event
    # output; ***do not change this***
    date_format = '%Y-%m-%d'
    time_format = '%H:%M'
    # The properties (in order) that icalBuddy must output; changing this order
    # will break the parsing of event data
    event_props = ('title', 'datetime', 'location', 'url', 'notes')

    def __init__(self):
        with open('prefs.json', 'r') as prefs_file:
            # Make all JSON keys accessible as instance attributes
            self.__dict__.update(json.load(prefs_file))


prefs = Prefs()
