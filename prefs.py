#!/usr/bin/env python3

import json


# The user's preferences for this workflow
class Prefs(object):

    def __init__(self):
        with open('prefs.json', 'r') as prefs_json:
            # Make all JSON keys accessible as instance attributes
            self.__dict__.update(json.load(prefs_json))


prefs = Prefs()
