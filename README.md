# Open Conference URL

*Copyright 2020 Caleb Evans*  
*Released under the MIT license*

Open Conference URL is an [Alfred][alfred] workflow which enables you to quickly
open links for Zoom and other conferencing services, based on your upcoming
calendar events.

[alfred]: http://alfredapp.com/

## Usage

Before you can use Open Conference URL, you must install the
[icalBuddy][icalBuddy] utility:

```sh
brew install ical-buddy
```

[icalBuddy]: https://formulae.brew.sh/formula/ical-buddy

To use, simply type the `conf` command into Alfred, and you will see a list of
upcoming calendar events. It does this by including all events within +/- 20
minutes of your system's current time, so even if you're running late to a
meeting, the logical event will show.

The workflow also accounts for timezones and Daylight Saving Time (DST). All
times are displayed in your system's local timezone.
