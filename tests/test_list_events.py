#!/usr/bin/env python3

import json
import unittest

from freezegun import freeze_time

from ocu import list_events
from tests.utils import redirect_stdout, use_env, use_event_dicts


class TestListEvents(unittest.TestCase):
    @use_event_dicts(
        [
            {
                "title": "My Meeting",
                "startDate": "2022-10-16T08:00",
                "endDate": "2022-10-16T09:00",
                "location": "https://zoom.us/j/123456",
            }
        ]
    )
    @freeze_time("2022-10-16 07:55:00")
    @redirect_stdout
    def test_5mins_before(self, out, event_dicts):
        """Should list meeting starting in 5 minutes"""
        list_events.main()
        feedback = json.loads(out.getvalue())
        self.assertEqual(feedback["items"][0]["title"], "My Meeting")
        self.assertEqual(feedback["items"][0]["subtitle"], "8:00am")
        self.assertEqual(
            feedback["items"][0]["text"]["copy"], event_dicts[0]["location"]
        )
        self.assertEqual(
            feedback["items"][0]["text"]["largetype"], event_dicts[0]["location"]
        )
        self.assertEqual(len(feedback["items"]), 1)

    @use_event_dicts(
        [
            {
                "title": "My Meeting",
                "startDate": "2022-10-16T08:00",
                "endDate": "2022-10-16T09:00",
                "location": "https://zoom.us/j/123456",
            }
        ]
    )
    @freeze_time("2022-10-16 8:05:00")
    @redirect_stdout
    def test_5mins_after(self, out, event_dicts):
        """Should list meeting that started 5 minutes ago"""
        list_events.main()
        feedback = json.loads(out.getvalue())
        self.assertEqual(feedback["items"][0]["title"], "My Meeting")
        self.assertEqual(feedback["items"][0]["subtitle"], "8:00am")
        self.assertEqual(
            feedback["items"][0]["text"]["copy"], event_dicts[0]["location"]
        )
        self.assertEqual(
            feedback["items"][0]["text"]["largetype"], event_dicts[0]["location"]
        )
        self.assertEqual(len(feedback["items"]), 1)

    @use_event_dicts(
        [
            {
                "title": "My Meeting",
                "startDate": "2022-10-16T08:00",
                "endDate": "2022-10-16T09:00",
                "location": "https://zoom.us/j/123456",
            }
        ]
    )
    @freeze_time("2022-10-16 8:00:00")
    @redirect_stdout
    def test_exact_start_time(self, out, event_dicts):
        """Should list meeting that starts at this exact minute"""
        list_events.main()
        feedback = json.loads(out.getvalue())
        self.assertEqual(feedback["items"][0]["title"], "My Meeting")
        self.assertEqual(feedback["items"][0]["subtitle"], "8:00am")
        self.assertEqual(
            feedback["items"][0]["text"]["copy"], event_dicts[0]["location"]
        )
        self.assertEqual(
            feedback["items"][0]["text"]["largetype"], event_dicts[0]["location"]
        )
        self.assertEqual(len(feedback["items"]), 1)

    @use_event_dicts(
        [
            {
                "title": "My Meeting",
                "startDate": "2022-10-16T08:00",
                "endDate": "2022-10-16T08:15",
                "location": "https://zoom.us/j/123456",
            }
        ]
    )
    @freeze_time("2022-10-16 8:16:00")
    @redirect_stdout
    def test_combine_duplicate_events(self, out, event_dicts):
        """Should not list meetings twice"""
        list_events.main()
        feedback = json.loads(out.getvalue())
        self.assertEqual(feedback["items"][0]["title"], "My Meeting")
        self.assertEqual(feedback["items"][0]["subtitle"], "8:00am")
        self.assertEqual(
            feedback["items"][0]["text"]["copy"], event_dicts[0]["location"]
        )
        self.assertEqual(
            feedback["items"][0]["text"]["largetype"], event_dicts[0]["location"]
        )
        self.assertEqual(len(feedback["items"]), 1)

    @use_event_dicts(
        [
            {
                "title": "My Meeting",
                "startDate": "2022-10-16T08:00",
                "endDate": "2022-10-16T09:00",
                "location": "https://zoom.us/j/123456",
            }
        ]
    )
    @freeze_time("2022-10-16 7:30:00")
    @redirect_stdout
    def test_before_window(self, out, event_dicts):
        """Should list all meetings if before next meeting's window"""
        list_events.main()
        feedback = json.loads(out.getvalue())
        self.assertEqual(feedback["items"][0]["title"], "No Upcoming Meetings")
        self.assertEqual(feedback["items"][1]["title"], "My Meeting")
        self.assertEqual(
            feedback["items"][1]["text"]["copy"], event_dicts[0]["location"]
        )
        self.assertEqual(
            feedback["items"][1]["text"]["largetype"], event_dicts[0]["location"]
        )
        self.assertEqual(len(feedback["items"]), 2)

    @use_event_dicts(
        [
            {
                "title": "All-Day Conference",
                "startDate": "2022-10-16T00:00",
                "endDate": "2022-10-16T23:59",
                "isAllDay": "true",
                "location": "https://zoom.us/j/123456",
            }
        ]
    )
    @freeze_time("2022-10-16 8:00:00")
    @redirect_stdout
    def test_all_day_standalone(self, out, event_dicts):
        """Should list all-day meetings by themselves"""
        list_events.main()
        feedback = json.loads(out.getvalue())
        self.assertEqual(feedback["items"][0]["title"], "All-Day Conference")
        self.assertEqual(feedback["items"][0]["subtitle"], "All-Day")
        self.assertEqual(
            feedback["items"][0]["text"]["copy"], event_dicts[0]["location"]
        )
        self.assertEqual(
            feedback["items"][0]["text"]["largetype"], event_dicts[0]["location"]
        )
        self.assertEqual(len(feedback["items"]), 1)

    @use_event_dicts(
        [
            {
                "title": "My Meeting 1",
                "startDate": "2022-10-16T06:00",
                "endDate": "2022-10-16T07:00",
                "location": "https://zoom.us/j/123456",
            },
            {
                "title": "All-Day Conference",
                "startDate": "2022-10-16T00:00",
                "endDate": "2022-10-16T23:59",
                "isAllDay": "true",
                "location": "https://zoom.us/j/123456",
            },
        ]
    )
    @freeze_time("2022-10-16 8:00:00")
    @redirect_stdout
    def test_all_day_with_past(self, out, event_dicts):
        """Should list all-day meetings below past events"""
        list_events.main()
        feedback = json.loads(out.getvalue())
        self.assertEqual(feedback["items"][0]["title"], "My Meeting 1")
        self.assertEqual(feedback["items"][0]["subtitle"], "6:00am")
        self.assertEqual(
            feedback["items"][0]["text"]["copy"], event_dicts[0]["location"]
        )
        self.assertEqual(
            feedback["items"][0]["text"]["largetype"], event_dicts[0]["location"]
        )
        self.assertEqual(feedback["items"][1]["title"], "All-Day Conference")
        self.assertEqual(feedback["items"][1]["subtitle"], "All-Day")
        self.assertEqual(
            feedback["items"][1]["text"]["copy"], event_dicts[1]["location"]
        )
        self.assertEqual(
            feedback["items"][1]["text"]["largetype"], event_dicts[1]["location"]
        )
        self.assertEqual(len(feedback["items"]), 2)

    @use_event_dicts(
        [
            {
                "title": "All-Day Conference",
                "startDate": "2022-10-16T00:00",
                "endDate": "2022-10-18T23:59",
                "isAllDay": "true",
                "location": "https://zoom.us/j/123456",
            }
        ]
    )
    @freeze_time("2022-10-16 8:00:00")
    @redirect_stdout
    def test_all_day_multiple_days(self, out, event_dicts):
        """Should handle all-day events spanning multiple days"""
        list_events.main()
        feedback = json.loads(out.getvalue())
        self.assertEqual(feedback["items"][0]["title"], "All-Day Conference")
        self.assertEqual(feedback["items"][0]["subtitle"], "All-Day")
        self.assertEqual(
            feedback["items"][0]["text"]["copy"], event_dicts[0]["location"]
        )
        self.assertEqual(
            feedback["items"][0]["text"]["largetype"], event_dicts[0]["location"]
        )
        self.assertEqual(len(feedback["items"]), 1)

    @use_event_dicts(
        [
            {
                "title": "All-Day Conference",
                "startDate": "2022-10-16T00:00",
                "endDate": "2022-10-16T23:59",
                "isAllDay": "true",
                "location": "https://zoom.us/j/123456",
            },
            {
                "title": "Morning Scrum",
                "startDate": "2022-10-16T08:00",
                "endDate": "2022-10-16T09:00",
                "location": "https://zoom.us/j/789012",
            },
        ]
    )
    @freeze_time("2022-10-16 7:58:00")
    @redirect_stdout
    def test_all_day_mixed(self, out, event_dicts):
        """Should list all-day meetings alongside upcoming meetings"""
        list_events.main()
        feedback = json.loads(out.getvalue())
        self.assertEqual(feedback["items"][0]["title"], "Morning Scrum")
        self.assertEqual(feedback["items"][0]["subtitle"], "8:00am")
        self.assertEqual(
            feedback["items"][0]["text"]["copy"], event_dicts[1]["location"]
        )
        self.assertEqual(
            feedback["items"][0]["text"]["largetype"], event_dicts[1]["location"]
        )
        self.assertEqual(feedback["items"][1]["title"], "All-Day Conference")
        self.assertEqual(feedback["items"][1]["subtitle"], "All-Day")
        self.assertEqual(
            feedback["items"][1]["text"]["copy"], event_dicts[0]["location"]
        )
        self.assertEqual(
            feedback["items"][1]["text"]["largetype"], event_dicts[0]["location"]
        )
        self.assertEqual(len(feedback["items"]), 2)

    @use_event_dicts(
        [
            {
                "title": "My Meeting 1",
                "startDate": "2022-10-16T08:00",
                "endDate": "2022-10-16T09:00",
                "location": "https://zoom.us/j/123456",
            },
            {
                "title": "My Meeting 2",
                "startDate": "2022-10-16T08:15",
                "endDate": "2022-10-16T09:00",
                "location": "https://zoom.us/j/789012",
            },
        ]
    )
    @freeze_time("2022-10-16 07:58:00")
    @redirect_stdout
    def test_multiple_meetings_at_once(self, out, event_dicts):
        """Should list multiple upcoming meetings at once"""
        list_events.main()
        feedback = json.loads(out.getvalue())
        self.assertEqual(feedback["items"][0]["title"], "My Meeting 1")
        self.assertEqual(feedback["items"][0]["subtitle"], "8:00am")
        self.assertEqual(
            feedback["items"][0]["text"]["copy"], event_dicts[0]["location"]
        )
        self.assertEqual(
            feedback["items"][0]["text"]["largetype"], event_dicts[0]["location"]
        )
        self.assertEqual(feedback["items"][1]["title"], "My Meeting 2")
        self.assertEqual(feedback["items"][1]["subtitle"], "8:15am")
        self.assertEqual(
            feedback["items"][1]["text"]["copy"], event_dicts[1]["location"]
        )
        self.assertEqual(
            feedback["items"][1]["text"]["largetype"], event_dicts[1]["location"]
        )
        self.assertEqual(len(feedback["items"]), 2)

    @use_event_dicts(
        [
            {
                "title": "My Meeting 1",
                "startDate": "2022-10-16T06:00",
                "endDate": "2022-10-16T07:00",
                "location": "https://zoom.us/j/123456",
            },
            {
                "title": "My Meeting 2",
                "startDate": "2022-10-16T08:00",
                "endDate": "2022-10-16T09:00",
                "location": "https://zoom.us/j/789012",
            },
        ]
    )
    @freeze_time("2022-10-16 9:15:00")
    @redirect_stdout
    def test_past_meetings_only(self, out, event_dicts):
        """Should list recent past meetings only"""
        list_events.main()
        feedback = json.loads(out.getvalue())
        self.assertEqual(feedback["items"][0]["title"], "No Upcoming Meetings")
        self.assertEqual(feedback["items"][1]["title"], "My Meeting 2")
        self.assertEqual(feedback["items"][1]["subtitle"], "8:00am")
        self.assertEqual(
            feedback["items"][1]["text"]["copy"], event_dicts[1]["location"]
        )
        self.assertEqual(
            feedback["items"][1]["text"]["largetype"], event_dicts[1]["location"]
        )
        self.assertEqual(feedback["items"][2]["title"], "My Meeting 1")
        self.assertEqual(feedback["items"][2]["subtitle"], "6:00am")
        self.assertEqual(
            feedback["items"][2]["text"]["copy"], event_dicts[0]["location"]
        )
        self.assertEqual(
            feedback["items"][2]["text"]["largetype"], event_dicts[0]["location"]
        )
        self.assertEqual(len(feedback["items"]), 3)

    @use_event_dicts(
        [
            {
                "title": "My Meeting 1",
                "startDate": "2022-10-16T06:00",
                "endDate": "2022-10-16T07:00",
                "location": "https://zoom.us/j/123456",
            },
            {
                "title": "My Meeting 2",
                "startDate": "2022-10-16T07:15",
                "endDate": "2022-10-16T07:45",
                "location": "https://zoom.us/j/123456",
            },
            {
                "title": "My Meeting 3",
                "startDate": "2022-10-16T08:00",
                "endDate": "2022-10-16T09:00",
                "location": "https://zoom.us/j/789012",
            },
        ]
    )
    @freeze_time("2022-10-16 07:55:00")
    @redirect_stdout
    def test_past_meetings_with_upcoming(self, out, event_dicts):
        """Should list recent past meetings alongside upcoming meetings"""
        list_events.main()
        feedback = json.loads(out.getvalue())
        self.assertEqual(feedback["items"][0]["title"], "My Meeting 3")
        self.assertEqual(feedback["items"][0]["subtitle"], "8:00am")
        self.assertEqual(
            feedback["items"][0]["text"]["copy"], event_dicts[2]["location"]
        )
        self.assertEqual(
            feedback["items"][0]["text"]["largetype"], event_dicts[2]["location"]
        )
        self.assertEqual(feedback["items"][1]["title"], "My Meeting 2")
        self.assertEqual(feedback["items"][1]["subtitle"], "7:15am")
        self.assertEqual(
            feedback["items"][1]["text"]["copy"], event_dicts[1]["location"]
        )
        self.assertEqual(
            feedback["items"][1]["text"]["largetype"], event_dicts[1]["location"]
        )
        self.assertEqual(len(feedback["items"]), 2)

    @use_event_dicts(
        [
            {
                "title": "My Meeting 1",
                "startDate": "2022-10-16T07:00",
                "endDate": "2022-10-16T07:30",
                "location": "https://zoom.us/j/123456",
            },
            {
                "title": "My Meeting 2",
                "startDate": "2022-10-16T07:15",
                "endDate": "2022-10-16T07:45",
                "location": "https://zoom.us/j/123456",
            },
            {
                "title": "My Meeting 3",
                "startDate": "2022-10-16T08:00",
                "endDate": "2022-10-16T09:00",
                "location": "https://zoom.us/j/789012",
            },
        ]
    )
    @freeze_time("2022-10-16 07:55:00")
    @redirect_stdout
    def test_multiple_past_meetings_with_upcoming(self, out, event_dicts):
        """Should list only most recent past meetings alongside upcoming meetings"""
        list_events.main()
        feedback = json.loads(out.getvalue())
        self.assertEqual(feedback["items"][0]["title"], "My Meeting 3")
        self.assertEqual(feedback["items"][0]["subtitle"], "8:00am")
        self.assertEqual(
            feedback["items"][0]["text"]["copy"], event_dicts[2]["location"]
        )
        self.assertEqual(
            feedback["items"][0]["text"]["largetype"], event_dicts[2]["location"]
        )
        self.assertEqual(feedback["items"][1]["title"], "My Meeting 2")
        self.assertEqual(feedback["items"][1]["subtitle"], "7:15am")
        self.assertEqual(
            feedback["items"][1]["text"]["copy"], event_dicts[1]["location"]
        )
        self.assertEqual(
            feedback["items"][1]["text"]["largetype"], event_dicts[1]["location"]
        )
        self.assertEqual(len(feedback["items"]), 2)

    @use_event_dicts(
        [
            {
                "title": "My Meeting",
                "startDate": "2022-10-16T08:00",
                "endDate": "2022-10-16T09:00",
                "location": "https://zoom.us/j/123456",
            },
            {
                "title": "My Non-Meeting",
                "startDate": "2022-10-16T08:00",
                "endDate": "2022-10-16T09:00",
                "location": "https://github.com",
            },
        ]
    )
    @freeze_time("2022-10-16 07:55:00")
    @redirect_stdout
    def test_excluding_non_conference_urls(self, out, event_dicts):
        """Should exclude non-conference URLs from 'upcoming' results"""
        list_events.main()
        feedback = json.loads(out.getvalue())
        self.assertEqual(feedback["items"][0]["title"], "My Meeting")
        self.assertEqual(feedback["items"][0]["subtitle"], "8:00am")
        self.assertEqual(
            feedback["items"][0]["text"]["copy"], event_dicts[0]["location"]
        )
        self.assertEqual(
            feedback["items"][0]["text"]["largetype"], event_dicts[0]["location"]
        )
        self.assertEqual(len(feedback["items"]), 1)

    @use_event_dicts([])
    @freeze_time("2022-10-16 9:30:00")
    @redirect_stdout
    def test_no_events_for_today(self, out, event_dicts):
        """Should display no meetings if there are no events for today"""
        list_events.main()
        feedback = json.loads(out.getvalue())
        self.assertEqual(feedback["items"][0]["title"], "No Results")
        self.assertEqual(len(feedback["items"]), 1)

    @use_env("time_system", "24-hour")
    @use_event_dicts(
        [
            {
                "title": "My Meeting",
                "startDate": "2022-10-16T13:00",
                "endDate": "2022-10-16T14:00",
                "location": "https://zoom.us/j/123456",
            }
        ]
    )
    @freeze_time("2022-10-16 12:55:00")
    @redirect_stdout
    def test_24_hour(self, out, event_dicts):
        """Should list meeting starting in 5 minutes (in 24-hour time)"""
        list_events.main()
        feedback = json.loads(out.getvalue())
        self.assertEqual(feedback["items"][0]["title"], "My Meeting")
        self.assertEqual(feedback["items"][0]["subtitle"], "13:00")
        self.assertEqual(
            feedback["items"][0]["text"]["copy"], event_dicts[0]["location"]
        )
        self.assertEqual(
            feedback["items"][0]["text"]["largetype"], event_dicts[0]["location"]
        )
        self.assertEqual(len(feedback["items"]), 1)
