#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import functools
import itertools
import json
import sys
from datetime import datetime, timedelta
from typing import Iterable, Optional

from ocu.calendar import get_calendar
from ocu.event import Event
from ocu.prefs import prefs

# The number of hours in a day
HOURS_IN_DAY = 24
# The number of minutes in an hour
MINUTES_IN_HOUR = 60


# Fetch all of today's events, regardless of proximity to the system's current
# time
def get_events_today() -> list[Event]:
    event_dicts = get_calendar().get_event_dicts()
    return [Event(event_dict) for event_dict in event_dicts]


# Retrieve only events from today for which a conference URL has been found
def get_events_today_with_conference_urls() -> list[Event]:
    return [event for event in get_events_today() if event.conference_url]


# Return True if the given date/time is sometime within the past; otherwise,
# return False
def is_time_in_past(
    event_datetime: datetime,
    time_threshold: int,
    current_datetime: Optional[datetime] = None,
) -> bool:
    if current_datetime is None:
        current_datetime = datetime.now()
    min_datetime = event_datetime
    return min_datetime < current_datetime


# Return True if the given date/time is within the next 15 minutes; otherwise, return False
def is_time_upcoming(
    event_datetime: datetime,
    time_threshold: int,
    current_datetime: Optional[datetime] = None,
) -> bool:
    if current_datetime is None:
        current_datetime = datetime.now()
    threshold_delta = timedelta(minutes=time_threshold)
    min_datetime = event_datetime - threshold_delta
    max_datetime = event_datetime + threshold_delta
    return min_datetime < current_datetime <= max_datetime


# Get those events from today which are in the past
def filter_to_past_events(events: Iterable[Event]) -> list[Event]:
    return [
        event
        for event in events
        if is_time_in_past(
            event.end_datetime, time_threshold=prefs["event_time_threshold_mins"]
        )
    ]


# Get those events from today which are either in the past or upcoming (but not
# any further into the future)
def filter_to_upcoming_events(events: Iterable[Event]):
    # Filter those events to only those which are nearest to the current time
    return [
        event
        for event in events
        if is_time_upcoming(
            event.start_datetime, time_threshold=prefs["event_time_threshold_mins"]
        )
    ]


# Sort the events such that future events are listed chronologically, whereas
# past events are listed reverse-chronologically; all-day events are always
# listed last
def get_event_sort_key(current_datetime: datetime, event: Event):
    if event.is_all_day:
        # List all-day events at the very bottom of the list
        return sys.maxsize
    elif is_time_upcoming(
        event.start_datetime,
        time_threshold=prefs["event_time_threshold_mins"],
        current_datetime=current_datetime,
    ):
        # e.g. 8:00am, 8:30am, 9:00am
        return event.start_datetime.timestamp()
    elif is_time_in_past(
        event.start_datetime,
        time_threshold=prefs["event_time_threshold_mins"],
        current_datetime=current_datetime,
    ):
        # e.g. 7:30am, 7:00am, 6:30am
        return sys.maxsize - event.end_datetime.timestamp()
    else:
        # this case will never occur because the other logic in this module
        # guarantees that the provided event object will always be either an
        # upcoming event or a past event
        return 0


# When we are using the get_event_sort_key() key function above, it is crucial
# that use the same current datetime for all iterated events; otherwise, it
# leaves open the possibility that some events could have a slightly different
# datetime than others
def get_event_sort_key_fn_for_current_datetime():
    current_datetime = datetime.now()
    return functools.partial(get_event_sort_key, current_datetime)


# Return a sorted list the given events where events that start AFTER the
# current time are listed chronologically (i.e. forward in time), whereas events
# in the past are listed reverse-chronologically (i.e. backward in time); this
# ensures that the nearest upcoming event is listed first, whereas the oldest
# past event is listed last
def sort_events_by_time(events: Iterable[Event]):
    return sorted(events, key=get_event_sort_key_fn_for_current_datetime())


# Get the event time (or 'All-Day' if the event is all-day)
def get_event_time(event: Event):
    if event.is_all_day:
        return "All-Day"
    elif prefs["time_system"] == "24-hour":
        return event.start_datetime.strftime("%H:%M").lower()
    else:
        return event.start_datetime.strftime("%-I:%M%p").lower()


# Return an Alfred feedback item representing the given Event instance
def get_event_feedback_item(event: Event):
    return {
        "title": event.title,
        "subtitle": get_event_time(event),
        "text": {
            # Copy the conference URL to the clipboard when cmd-c is
            # pressed
            "copy": event.conference_url,
            # Display the conference URL via Alfred's Large Type feature
            # when cmd-l is pressed
            "largetype": event.conference_url,
        },
        "variables": {
            "event_title": event.title,
            "event_conference_url": event.conference_url,
        },
    }


def main():
    all_events = get_events_today_with_conference_urls()
    upcoming_events = filter_to_upcoming_events(all_events)
    past_events = filter_to_past_events(all_events)
    # If both upcoming events and past events should be listed, only list the
    # most recent past event
    if upcoming_events and len(past_events) > 1:
        past_events[:] = [
            min(past_events, key=get_event_sort_key_fn_for_current_datetime())
        ]

    events_to_display = sort_events_by_time(
        set(itertools.chain(past_events, upcoming_events))
    )

    # The feedback object which will be fed to Alfred to display the results
    feedback = {"items": []}
    # For convenience, display all events for today if there are no upcoming
    # events; also display a No Results item at the top of the result set (so
    # that an event isn't hurriedly actioned by the user)
    if not all_events:
        feedback["items"].append(
            {"title": "No Results", "subtitle": "No meetings for today", "valid": "no"}
        )
    elif all_events and not upcoming_events and past_events:
        feedback["items"].append(
            {
                "title": "No Upcoming Meetings",
                "subtitle": "Showing events from earlier today",
                "valid": "no",
            }
        )
        feedback["items"].extend(
            get_event_feedback_item(event) for event in events_to_display
        )
    elif all_events and not upcoming_events and not past_events:
        feedback["items"].append(
            {
                "title": "No Upcoming Meetings",
                "subtitle": "Showing all events for today",
                "valid": "no",
            }
        )
        feedback["items"].extend(get_event_feedback_item(event) for event in all_events)
    else:
        feedback["items"].extend(
            get_event_feedback_item(event) for event in events_to_display
        )

    # Alfred doesn't appear to care about whitespace in the resulting JSON, so
    # we are prettifying the JSON output here for easier debugging
    print(json.dumps(feedback, indent=2))


if __name__ == "__main__":
    main()
