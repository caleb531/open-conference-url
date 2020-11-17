#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json
from datetime import datetime, timedelta

from ocu.event import Event
from ocu.cache import cache
from ocu.prefs import prefs


# The number of hours in a day
HOURS_IN_DAY = 24
# The number of minutes in an hour
MINUTES_IN_HOUR = 60


# Retrieve the raw calendar output for today's events
def get_event_blobs():
    if not cache.has('event_blobs'):
        cache.refresh()
    return cache.get('event_blobs')


# Retrieve a list of event UIDs for today's calendar day
def get_events():

    event_blobs = get_event_blobs()
    return [Event(event_blob) for event_blob in event_blobs]


# Read the given ICS file path and return the Event object corresponding to
# that event data
def get_event(event_path):
    with open(event_path, 'r') as event_file:
        return Event(event_file.read())


# Return True if the given date/time object is within the acceptable tolerance
# range (e.g. within the next 15 minutes OR in the last 15 minutes); if not,
# return False
def is_time_within_range(event_datetime, event_time_threshold):
    current_datetime = datetime.now().astimezone()
    event_time_threshold = timedelta(**event_time_threshold)
    min_datetime = (event_datetime - event_time_threshold)
    max_datetime = (event_datetime + event_time_threshold)
    if min_datetime <= current_datetime <= max_datetime:
        return True
    else:
        return False


# Return an Alfred feedback item representing the given Event instance
def get_event_feedback_item(event):
    return {
        'title': event.title,
        'subtitle': 'All-Day' if event.is_all_day else event.start_datetime.strftime('%-I:%M%p').lower(),
        'text': {
            # Copy the conference URL to the clipboard when cmd-c is
            # pressed
            'copy': event.conference_url,
            # Display the conference URL via Alfred's Large Type feature
            # when cmd-l is pressed
            'largetype': event.conference_url
        },
        'variables': {
            'event_title': event.title,
            'event_conference_url': event.conference_url
        }
    }


def main():

    # Fetch all events from cache, regardless of proximity to the system's
    # current time
    all_events = [event for event in get_events() if event.conference_url]

    # Filter those events to only those which are nearest to the current time
    upcoming_events = [event for event in all_events if is_time_within_range(
                       event.start_datetime, prefs.event_time_threshold)]

    # The feedback object which will be fed to Alfred to display the results
    feedback = {'items': []}
    # For convenience, display all events for today if there are no upcoming
    # events; also display a No Results item at the top of the result set (so
    # that an event isn't hurriedly actioned by the user)
    if not all_events and not upcoming_events:
        feedback['items'].append({
            'title': 'No Results',
            'subtitle': 'No calendar events could be found',
            'valid': 'no'
        })
    elif all_events and not upcoming_events:
        upcoming_events = all_events
        feedback['items'].append({
            'title': 'No Results',
            'subtitle': 'Showing all calendar events',
            'valid': 'no'
        })
    feedback['items'].extend(get_event_feedback_item(event)
                             for event in upcoming_events)

    # Tell Alfred to refresh the event cache in the background without blocking
    # the loading of the event list into Alfred's results
    cache.queue_refresh()
    # Alfred doesn't appear to care about whitespace in the resulting JSON, so
    # we are prettifying the JSON output here for easier debugging
    print(json.dumps(feedback, indent=2))


if __name__ == '__main__':
    main()
