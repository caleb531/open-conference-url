#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json
import itertools
from datetime import datetime, timedelta
from operator import attrgetter

from ocu.calendar import calendar
from ocu.event import Event
from ocu.prefs import prefs


# The number of hours in a day
HOURS_IN_DAY = 24
# The number of minutes in an hour
MINUTES_IN_HOUR = 60


# Retrieve the raw event dictionary data for today's events
def get_event_dicts():
    return calendar.get_event_dicts(prefs['calendar_names'])


# Fetch all of today's events, regardless of proximity to the system's current
# time
def get_events_today():

    event_dicts = get_event_dicts()
    return [Event(event_dict) for event_dict in event_dicts]


# Retrieve only events from today for which a conference URL has been found
def get_events_today_with_conference_urls():

    return [event for event in get_events_today() if event.conference_url]


# Return True if the given date/time is sometime within the past; otherwise,
# return False
def is_time_in_past(event_datetime):
    current_datetime = datetime.now()
    if event_datetime <= current_datetime:
        return True
    else:
        return False


# Return True if the given date/time is within the next 15 minutes; otherwise, return False
def is_time_upcoming(event_datetime, event_time_threshold_mins):
    current_datetime = datetime.now()
    event_time_threshold = timedelta(minutes=event_time_threshold_mins)
    min_datetime = (event_datetime - event_time_threshold)
    if min_datetime < current_datetime <= event_datetime:
        return True
    else:
        return False


# Get those events from today which are in the past
def filter_to_past_events(events):
    return [event for event in events if is_time_in_past(event.start_datetime)]


# Get those events from today which are either in the past or upcoming (but not
# any further into the future)
def filter_to_upcoming_events(events):
    # Filter those events to only those which are nearest to the current time
    return [event for event in events if is_time_upcoming(
                       event.start_datetime,
                       prefs['event_time_threshold_mins'])]


# Return a sorted list the given events by time
def sort_events_by_time(events):
    return sorted(events, key=attrgetter('start_datetime'), reverse=True)


# Get the event time (or 'All-Day' if the event is all-day)
def get_event_time(event):
    if event.is_all_day:
        return 'All-Day'
    elif prefs['time_system'] == '24-hour':
        return event.start_datetime.strftime('%H:%M').lower()
    else:
        return event.start_datetime.strftime('%-I:%M%p').lower()


# Return an Alfred feedback item representing the given Event instance
def get_event_feedback_item(event):
    return {
        'title': event.title,
        'subtitle': get_event_time(event),
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

    all_events = get_events_today_with_conference_urls()
    past_events = filter_to_past_events(all_events)
    upcoming_events = filter_to_upcoming_events(all_events)
    events_to_display = sort_events_by_time(
        set(itertools.chain(past_events, upcoming_events)))

    # The feedback object which will be fed to Alfred to display the results
    feedback = {'items': []}
    # For convenience, display all events for today if there are no upcoming
    # events; also display a No Results item at the top of the result set (so
    # that an event isn't hurriedly actioned by the user)
    if not all_events:
        feedback['items'].append({
            'title': 'No Results',
            'subtitle': 'No meetings for today',
            'valid': 'no'
        })
    elif all_events and not upcoming_events and past_events:
        feedback['items'].append({
            'title': 'No Upcoming Meetings',
            'subtitle': 'Showing events from earlier today',
            'valid': 'no'
        })
        feedback['items'].extend(get_event_feedback_item(event)
                                 for event in events_to_display)
    elif all_events and not upcoming_events and not past_events:
        feedback['items'].append({
            'title': 'No Upcoming Meetings',
            'subtitle': 'Showing all events for today',
            'valid': 'no'
        })
        feedback['items'].extend(get_event_feedback_item(event)
                                 for event in all_events)
    else:
        feedback['items'].extend(get_event_feedback_item(event)
                                 for event in events_to_display)

    # Alfred doesn't appear to care about whitespace in the resulting JSON, so
    # we are prettifying the JSON output here for easier debugging
    print(json.dumps(feedback, indent=2))


if __name__ == '__main__':
    main()
