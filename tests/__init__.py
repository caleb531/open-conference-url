#!/usr/bin/env python3

import os


os.environ['conference_domains'] = '*.zoom.us, zoom.us, meet.google.com, hangouts.google.com, *.microsoft.com, gotomeeting.com, *.gotomeeting.com, webex.com, *.webex.com, uberconference.com'  # noqa
os.environ['use_direct_zoom'] = 'false'
os.environ['time_threshold'] = '20'
