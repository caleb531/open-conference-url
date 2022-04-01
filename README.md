# Open Conference URL

*Copyright 2020-2022 Caleb Evans*  
*Released under the MIT license*

Open Conference URL is an [Alfred][alfred] workflow which enables you to quickly
open links for Zoom and other conferencing services, based on your upcoming
calendar events.

[alfred]: https://www.alfredapp.com/

## Installation

Simply download the workflow file (shown in the file list above) and
double-click it to install it in Alfred.

## Usage

To use, simply type the `conf` command into Alfred, and you will see a list of
upcoming calendar events. It does this by including all events within +/- 20
minutes of your system's current time, so even if you're running late to a
meeting, the logical event will show.

The workflow also accounts for timezones and Daylight Saving Time (DST). All
times are displayed in your system's local timezone.

## Preferences

This workflow contains user configuration options for various aspects of the
workflow's behavior. To view this preferences file:

1. Right-click the workflow in Alfred Preferences
2. Choose **Open In Finder**
3. Navigate into the `ocu` folder
4. Open `prefs.json` in your preferred text editor

What follows is a description of each preference you can configure. If you are
unfamiliar with JSON syntax, you can find many quick tutorials online.

### offset_from_today

The `offset_from_today` is a positive integer representing how many days into
the future the workflow should fetch calendar events. For example, a value of
`1` will display events from tomorrow alongside events from today.

### event_time_threshold

The `event_time_threshold` is an object that can contain any combination of
`hours` and `minutes` integers. If an event is within this duration of time
(relative to the system's current time), it will be displayed in Alfred's
results.

For example, a value of `{"minutes": 20}` will mean the workflow will only show
events whose start time was within the last 20 minutes *or* whose start time is
within the next 20 minutes.

### conference_domains

The `conference_domains` is an array of domain names representing which URLs to
check within each calendar event. This domains list determines which links are
considered "conference" URLs.

The domains are listed in order of precedence, so if `"zoom.us"` precedes
`"google.com"` in the file, then the workflow will prefer the Zoom link over the
Google Meet link if both are present.

## Credits

Kudos to [@jacksonrayhamilton][jrh] for his architecture ideas and feedback on
this project.

[jrh]: https://github.com/jacksonrayhamilton
