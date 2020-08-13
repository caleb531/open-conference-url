#!/usr/bin/env python3

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

# How long before or into the meeting to show the conference URL
TIME_THRESHOLD = {
    'minutes': 20
}


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
def is_time_within_range(event_datetime):
    current_datetime = datetime.now().astimezone()
    threshold = timedelta(**TIME_THRESHOLD)
    min_datetime = (event_datetime - threshold)
    max_datetime = (event_datetime + threshold)
    if min_datetime <= current_datetime <= max_datetime:
        return True
    else:
        return False


def main():

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
        # Do not add the event in the results if it is not upcoming
        if not is_time_within_range(event.start_datetime_local):
            continue
        feedback['items'].append({
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
        })

    if not feedback['items']:
        feedback['items'].append({
            'title': 'No Results',
            'subtitle': 'No calendar events could be found',
            'valid': 'no'
        })

    # Alfred doesn't appear to care about whitespace in the resulting JSON, so
    # we are prettifying the JSON output here for easier debugging
    print(json.dumps(feedback, indent=2))


if __name__ == '__main__':
    main()
