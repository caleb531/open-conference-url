#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
from typing import Any, Callable, Literal, Union

# The available preference names for this workflow; if you wish to access a
# preference's value using subscripting (i.e. via square brackets), you must use
# one of these names
PrefName = Union[
    Literal["conference_domains"],
    Literal["calendar_names"],
    Literal["event_time_threshold_mins"],
    Literal["use_direct_zoom"],
    Literal["use_direct_msteams"],
    Literal["use_direct_gmeet"],
    Literal["gmeet_app_name"],
    Literal["use_icalbuddy"],
    Literal["time_system"],
]


# A utility class for retrieving user preferences for this workflow; all
# preferences are stored as Alfred Workflow variables, and are exposed to the
# scripting runtime as environment variables
class Prefs(object):
    pref_field_types: dict[PrefName, Callable]

    def __init__(self) -> None:
        self.pref_field_types = {
            "conference_domains": self.convert_str_to_list,
            "calendar_names": self.convert_str_to_list,
            "event_time_threshold_mins": int,
            "use_direct_zoom": self.convert_str_to_bool,
            "use_direct_msteams": self.convert_str_to_bool,
            "use_direct_gmeet": self.convert_str_to_bool,
            "gmeet_app_name": str,
            "use_icalbuddy": self.convert_str_to_bool,
            "time_system": str,
        }

    # Convert a comma-separated string of values to a proper list type
    def convert_str_to_list(self, value: str) -> list:
        value_list = re.split(r"\s*(?:,|\n)\s*", value.strip())
        if value_list == [""]:
            return []
        else:
            return value_list

    # Convert a boolean-like string value (like 'Yes' or 'True') to a proper
    # boolean
    def convert_str_to_bool(self, value: str) -> bool:
        return value.lower().strip() in ("1", "y", "yes", "true", "t")

    def __getitem__(self, pref_name: PrefName) -> Any:
        converter = self.pref_field_types[pref_name]
        return converter(os.environ[pref_name])


prefs = Prefs()
