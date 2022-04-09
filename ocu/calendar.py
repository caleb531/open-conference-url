
import os
import os.path
import re
import subprocess

from ocu.prefs import prefs


# An abstraction class between this workflow and the program that retrieves the
# calendar data (in this case, icalBuddy)
class Calendar(object):

    # The date and time used internally to display and parse icalBuddy event
    # output; ***do not change this***
    date_format = '%Y-%m-%d'
    time_format = '%H:%M'
    # The properties (in order) that icalBuddy must output; changing this order
    # will break the parsing of event data
    event_props = ('title', 'datetime', 'location', 'url', 'notes')
    # All possible paths to check for the icalBuddy binary that's used for
    # retrieving calendar data; the first path that exists on the user's system
    # is the one that's used
    binary_paths = [
        os.path.join(os.sep, 'opt', 'homebrew', 'bin', 'icalBuddy'),
        os.path.join(os.sep, 'usr', 'local', 'bin', 'icalBuddy'),
        os.path.join(os.path.dirname(os.path.realpath(__file__)), 'icalBuddy')
    ]

    # Retrieve the first available path to the binary among a list of possible
    # paths (this allows us to prefer the already-signed Homebrew icalBuddy
    # binary over our workflow-bundled binary that requires explicit permission
    # to execute)
    def get_binary_path(self):
        for binary_path in self.binary_paths:
            if os.path.exists(binary_path):
                return binary_path
        return binary_path[-1]

    # Retrieve the raw event blob data from icalBuddy
    def get_event_blobs(self):
        event_blobs = re.split(r'(?:^|\n)• ', subprocess.check_output([
            self.get_binary_path(),
            # Override the default date/time formats
            '--dateFormat',
            self.date_format,
            '--noRelativeDates',
            '--timeFormat',
            self.time_format,
            # remove parenthetical calendar names from event titles
            '--noCalendarNames',
            # Only include the following fields and enforce their order
            '--includeEventProps',
            ','.join(self.event_props),
            '--propertyOrder',
            ','.join(self.event_props),
            'eventsToday+{}'.format(prefs['offset_from_today'])
        ]).decode('utf-8'))
        # The first element will always be an empty string, because the bullet
        # point we are splitting on is not a delimiter
        event_blobs.pop(0)
        return event_blobs


calendar = Calendar()
