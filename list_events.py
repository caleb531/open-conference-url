#!/usr/bin/env python3

import json
import os
import os.path
import re
import subprocess
from datetime import datetime, timedelta

from event import Event


# The path to the user's local calendar database
CALENDAR_DB_DIR = os.path.expanduser(os.path.join(
    '~', 'Library', 'Calendars'))
# The number of hours in a day
HOURS_IN_DAY = 24
# The number of minutes in an hour
MINUTES_IN_HOUR = 60
# The number of minutes threshold used to determine of
TIME_THRESHOLD = {'minutes': 20}


# Retrieve the raw calendar output for today's events
def get_event_blobs(event_props, date_format, time_format, offset_from_today):
    return re.split(r'• ', subprocess.check_output([
        'icalBuddy',
        # Override the default date/time formats
        '--dateFormat',
        date_format,
        '--noRelativeDates',
        '--timeFormat',
        time_format,
        # remove parenthetical calendar names from event titles
        '--noCalendarNames',
        # Only include the following fields and enforce their order
        '--includeEventProps',
        ','.join(event_props),
        '--propertyOrder',
        ','.join(event_props),
        'eventsToday+{}'.format(offset_from_today)
    ]).decode('utf-8'))


# Retrieve a list of event UIDs for today's calendar day
def get_events():

    event_blobs = get_event_blobs(
        event_props=('title', 'datetime', 'location', 'url', 'notes'),
        # YYYY-MM-DD (e.g. 2019-08-09)
        date_format='%Y-%m-%d',
        # 24-hour time (e.g. 18:30)
        time_format='%H:%M',
        # Represents how far out to look for future events (in addition to
        # today's events)
        offset_from_today=0)
    # The first element will always be an empty string, because the bullet
    # point we are splitting on is not a delimiter
    event_blobs.pop(0)
    return [Event(event_blob) for event_blob in event_blobs]


# Read the given ICS file path and return the Event object corresponding to
# that event data
def get_event(event_path):
    with open(event_path, 'r') as event_file:
        return Event(event_file.read())


# Return True if the given date/time object is within the acceptable tolerance
# range (e.g. within the next 15 minutes OR in the last 15 minutes); if not,
# return False
def is_time_within_range(event_datetime, time_threshold):
    current_datetime = datetime.now().astimezone()
    time_threshold = timedelta(**time_threshold)
    min_datetime = (event_datetime - time_threshold)
    max_datetime = (event_datetime + time_threshold)
    if min_datetime <= current_datetime <= max_datetime:
        return True
    else:
        return False


# Return an Alfred feedback item representing the given Event instance
def get_event_feedback_item(event):
    return {
        'title': event.title,
        'subtitle': event.start_datetime.strftime('%-I:%M%p').lower(),
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

    all_events = []
    # The feedback object which will be fed to Alfred to display the results
    feedback = {'items': []}

    for event in get_events():
        # Do not display the event in the results if it has no conference URL
        if not event.conference_url:
            continue
        all_events.append(event)

    upcoming_events = [event for event in all_events if is_time_within_range(
                       event.start_datetime, TIME_THRESHOLD)]

    # For convenience, display all events for today if there are no upcoming
    # events; also display a No Results item at the top of the result set (so
    # that an event isn't hurriedly actioned by the user)
    if not upcoming_events:
        upcoming_events = all_events
        feedback['items'].append({
            'title': 'No Results',
            'subtitle': 'No calendar events could be found',
            'valid': 'no'
        })
    feedback['items'].extend(get_event_feedback_item(event)
                             for event in upcoming_events)

    # Alfred doesn't appear to care about whitespace in the resulting JSON, so
    # we are prettifying the JSON output here for easier debugging
    print(json.dumps(feedback, indent=2))


if __name__ == '__main__':
    main()
