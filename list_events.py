#!/usr/bin/env python3

import argparse
import glob
import json
import os
import os.path
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


# Retrieve a list of event UIDs for today's calendar day
def get_event_uids():

    event_uids = subprocess.check_output([
        'osascript',
        'get-event-uids.applescript'
    ]).decode('utf-8').replace('.', '').strip().split(',')

    if len(event_uids) == 1 and event_uids[0] == '':
        return []
    else:
        return event_uids


# Retrieve the path to the ICS file corresponding to the given event UID
def get_event_path(event_uid):
    normalized_event_uid = event_uid.replace('.', '').replace(':', '')
    event_filename = f'{normalized_event_uid}.ics'
    event_paths = glob.glob(os.path.join(
        CALENDAR_DB_DIR, '*', '*', 'Events', event_filename))
    if event_paths:
        return event_paths[0]
    else:
        return None


# Read the given ICS file path and return the Event object corresponding to
# that event data
def get_event(event_path):
    with open(event_path, 'r') as event_file:
        return Event(event_file.read())


# Return True if the given date/time object is within the acceptable tolerance
# range (e.g. within the next 15 minutes OR in the last 15 minutes); if not,
# return False
def is_time_within_range(event_datetime, threshold):
    current_datetime = datetime.now().astimezone()
    threshold = timedelta(**threshold)
    min_datetime = (event_datetime - threshold)
    max_datetime = (event_datetime + threshold)
    if min_datetime <= current_datetime <= max_datetime:
        return True
    else:
        return False


# Get the time threshold used for the is_time_within_range function
def get_time_threshold(mode):
    if mode and mode.strip().lower().startswith('a'):
        return {'minutes': HOURS_IN_DAY * MINUTES_IN_HOUR}
    else:
        return {'minutes': 20}


# Return an Alfred feedback item representing the given Event instance
def get_event_feedback_item(event):
    return {
        'title': event.summary,
        'subtitle': event.start_datetime_local.strftime('%-I:%M%p').lower(),
        'text': {
            # Copy the conference URL to the clipboard when cmd-c is
            # pressed
            'copy': event.conference_url,
            # Display the conference URL via Alfred's Large Type feature
            # when cmd-l is pressed
            'largetype': event.conference_url
        },
        'variables': {
            'event_summary': event.summary,
            'event_conference_url': event.conference_url
        }
    }


# Parse command line arguments to this program
def parse_cli_args():

    parser = argparse.ArgumentParser()
    parser.add_argument(
        'mode',
        nargs='?',
        help='a case-insensitive keyword to adjust the behavior of the'
             'program (can be ALL)')

    return parser.parse_args()


def main():

    cli_args = parse_cli_args()
    threshold = get_time_threshold(**vars(cli_args))

    all_events = []
    # The feedback object which will be fed to Alfred to display the results
    feedback = {'items': []}

    for event_uid in get_event_uids():
        event_path = get_event_path(event_uid)
        if not event_path:
            continue
        event = get_event(event_path)
        # Do not display the event in the results if it has no conference URL
        if not event.conference_url:
            continue
        all_events.append(event)

    upcoming_events = [event for event in all_events if is_time_within_range(
                       event.start_datetime_local, threshold)]

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
