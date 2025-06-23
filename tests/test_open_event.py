#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import unittest
from io import StringIO
from unittest.mock import patch

from ocu import open_event
from tests.utils import use_env


class TestOpenEvent(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.original_stderr = sys.stderr
        self.captured_stderr = StringIO()

    def tearDown(self):
        """Clean up after tests"""
        sys.stderr = self.original_stderr

    def capture_stderr(self):
        """Helper to capture stderr output"""
        sys.stderr = self.captured_stderr
        return self.captured_stderr

    def test_should_open_google_meet_app_with_none_url(self):
        """should_open_google_meet_app should return False for None URL"""
        result = open_event.should_open_google_meet_app(None)
        self.assertFalse(result)

    def test_should_open_google_meet_app_with_empty_url(self):
        """should_open_google_meet_app should return False for empty URL"""
        result = open_event.should_open_google_meet_app("")
        self.assertFalse(result)

    def test_should_open_google_meet_app_with_non_google_url(self):
        """should_open_google_meet_app should return False for non-Google URLs"""
        urls = [
            "https://zoom.us/j/123456789",
            "https://teams.microsoft.com/l/meetup-join/123",
            "https://example.com/meeting",
            "https://meet.google.co.uk/abc-def-ghi",  # Wrong domain
        ]
        for url in urls:
            with self.subTest(url=url):
                result = open_event.should_open_google_meet_app(url)
                self.assertFalse(result)

    @use_env("use_direct_gmeet", "true")
    def test_should_open_google_meet_app_with_google_url_and_pref_enabled(self):
        """
        should_open_google_meet_app should return True for Google Meet URLs when
        preference is enabled
        """
        urls = [
            "https://meet.google.com/abc-def-ghi",
            "https://meet.google.com/xyz-123-456?authuser=0",
        ]
        for url in urls:
            with self.subTest(url=url):
                result = open_event.should_open_google_meet_app(url)
                self.assertTrue(result)

    @use_env("use_direct_gmeet", "false")
    def test_should_open_google_meet_app_with_google_url_and_pref_disabled(self):
        """
        should_open_google_meet_app should return False for Google Meet URLs
        when preference is disabled"""
        url = "https://meet.google.com/abc-def-ghi"
        result = open_event.should_open_google_meet_app(url)
        self.assertFalse(result)

    @use_env("use_direct_gmeet", "")  # Empty env var should default to False
    def test_should_open_google_meet_app_with_google_url_and_pref_unset(self):
        """
        should_open_google_meet_app should return False for Google Meet URLs
        when preference is unset"""
        url = "https://meet.google.com/abc-def-ghi"
        result = open_event.should_open_google_meet_app(url)
        self.assertFalse(result)

    def test_should_open_google_meet_app_with_missing_pref_key(self):
        """
        should_open_google_meet_app should handle missing preference key
        gracefully
        """
        url = "https://meet.google.com/abc-def-ghi"

        with patch.dict("os.environ", {}, clear=True):  # Clear all env vars
            result = open_event.should_open_google_meet_app(url)
            self.assertFalse(result)

    @patch("subprocess.run")
    def test_open_url_with_native_app_success(self, mock_run):
        """open_url_with_native_app should successfully open URL with native app"""
        mock_run.return_value = None

        open_event.open_url_with_native_app(
            "https://meet.google.com/abc-def-ghi", "Google Meet"
        )

        mock_run.assert_called_once_with(
            ["open", "-a", "Google Meet", "https://meet.google.com/abc-def-ghi"],
            check=True,
        )

    @patch("subprocess.run")
    @patch("ocu.open_event.open_url_no_app")
    def test_open_url_with_native_app_subprocess_error(
        self, mock_open_no_app, mock_run
    ):
        """
        open_url_with_native_app should fallback to default browser on
        subprocess error
        """
        from subprocess import CalledProcessError

        mock_run.side_effect = CalledProcessError(1, ["open"])
        stderr_capture = self.capture_stderr()

        open_event.open_url_with_native_app(
            "https://meet.google.com/abc-def-ghi", "Google Meet"
        )

        stderr_output = stderr_capture.getvalue()
        self.assertIn("Failed to open URL with Google Meet", stderr_output)
        mock_open_no_app.assert_called_once_with("https://meet.google.com/abc-def-ghi")

    @patch("subprocess.run")
    @patch("ocu.open_event.open_url_no_app")
    def test_open_url_with_native_app_file_not_found(self, mock_open_no_app, mock_run):
        """
        open_url_with_native_app should fallback to default browser when app not
        found
        """
        mock_run.side_effect = FileNotFoundError("Application not found")
        stderr_capture = self.capture_stderr()

        open_event.open_url_with_native_app(
            "https://meet.google.com/abc-def-ghi", "Google Meet"
        )

        stderr_output = stderr_capture.getvalue()
        self.assertIn("Application Google Meet not found", stderr_output)
        self.assertIn("opening with default browser", stderr_output)
        mock_open_no_app.assert_called_once_with("https://meet.google.com/abc-def-ghi")

    @patch("subprocess.run")
    def test_open_url_no_app_success(self, mock_run):
        """open_url_no_app should successfully open URL with default browser"""
        mock_run.return_value = None

        open_event.open_url_no_app("https://example.com")

        mock_run.assert_called_once_with(["open", "https://example.com"], check=True)

    @patch("subprocess.run")
    @patch("sys.exit")
    def test_open_url_no_app_failure(self, mock_exit, mock_run):
        """open_url_no_app should exit with error code on failure"""
        from subprocess import CalledProcessError

        mock_run.side_effect = CalledProcessError(1, ["open"])
        stderr_capture = self.capture_stderr()

        open_event.open_url_no_app("https://example.com")

        stderr_output = stderr_capture.getvalue()
        self.assertIn("Failed to open URL", stderr_output)
        mock_exit.assert_called_once_with(1)

    @patch("sys.argv", ["open_event.py"])
    @patch("sys.exit")
    def test_main_no_arguments(self, mock_exit):
        """main should exit with usage message when no arguments provided"""
        # Make sys.exit actually stop execution by raising SystemExit
        mock_exit.side_effect = SystemExit(1)
        stderr_capture = self.capture_stderr()

        with self.assertRaises(SystemExit):
            open_event.main()

        stderr_output = stderr_capture.getvalue()
        self.assertIn("Usage: open-event.py <conference_url>", stderr_output)
        mock_exit.assert_called_once_with(1)

    @patch("sys.argv", ["open_event.py", "https://zoom.us/j/123456789"])
    @patch("ocu.open_event.open_url_no_app")
    def test_main_non_google_meet_url(self, mock_open_no_app):
        """main should open non-Google Meet URLs with default handler"""
        stderr_capture = self.capture_stderr()

        open_event.main()

        stderr_output = stderr_capture.getvalue()
        self.assertIn(
            "Opening conference URL: https://zoom.us/j/123456789", stderr_output
        )
        mock_open_no_app.assert_called_once_with("https://zoom.us/j/123456789")

    @patch("sys.argv", ["open_event.py", "https://meet.google.com/abc-def-ghi"])
    @patch("ocu.open_event.open_url_no_app")
    @use_env("use_direct_gmeet", "false")
    def test_main_google_meet_url_pref_disabled(self, mock_open_no_app):
        """
        main should open Google Meet URLs with default handler when preference
        disabled
        """
        stderr_capture = self.capture_stderr()

        open_event.main()

        stderr_output = stderr_capture.getvalue()
        self.assertIn(
            "Opening conference URL: https://meet.google.com/abc-def-ghi", stderr_output
        )
        mock_open_no_app.assert_called_once_with("https://meet.google.com/abc-def-ghi")

    @patch("sys.argv", ["open_event.py", "https://meet.google.com/abc-def-ghi"])
    @patch("ocu.open_event.open_url_with_native_app")
    @use_env("use_direct_gmeet", "true")
    @use_env("gmeet_app_name", "Google Meet")
    def test_main_google_meet_url_pref_enabled_default_app(self, mock_open_with_app):
        """main should open Google Meet URLs with native app when preference enabled"""
        stderr_capture = self.capture_stderr()

        open_event.main()

        stderr_output = stderr_capture.getvalue()
        url = "https://meet.google.com/abc-def-ghi"
        self.assertIn(
            f"Opening Google Meet URL in Desktop app: {url}",
            stderr_output,
        )
        mock_open_with_app.assert_called_once_with(
            "https://meet.google.com/abc-def-ghi", "Google Meet"
        )

    @patch("sys.argv", ["open_event.py", "https://meet.google.com/abc-def-ghi"])
    @patch("ocu.open_event.open_url_with_native_app")
    @use_env("use_direct_gmeet", "true")
    @use_env("gmeet_app_name", "Custom Meet App")
    def test_main_google_meet_url_pref_enabled_custom_app(self, mock_open_with_app):
        """main should open Google Meet URLs with custom app name when configured"""
        stderr_capture = self.capture_stderr()

        open_event.main()

        stderr_output = stderr_capture.getvalue()
        url = "https://meet.google.com/abc-def-ghi"
        self.assertIn(
            f"Opening Google Meet URL in Desktop app: {url}",
            stderr_output,
        )
        mock_open_with_app.assert_called_once_with(
            "https://meet.google.com/abc-def-ghi", "Custom Meet App"
        )

    @patch("sys.argv", ["open_event.py", "https://meet.google.com/abc-def-ghi"])
    @patch("ocu.open_event.open_url_with_native_app")
    @use_env("use_direct_gmeet", "true")
    @use_env("gmeet_app_name", "")  # Empty app name should default to "Google Meet"
    def test_main_google_meet_url_empty_app_name(self, mock_open_with_app):
        """main should use default app name when gmeet_app_name is empty"""
        stderr_capture = self.capture_stderr()

        open_event.main()

        stderr_output = stderr_capture.getvalue()
        url = "https://meet.google.com/abc-def-ghi"
        self.assertIn(
            f"Opening Google Meet URL in Desktop app: {url}",
            stderr_output,
        )
        mock_open_with_app.assert_called_once_with(
            "https://meet.google.com/abc-def-ghi", "Google Meet"
        )

    @patch("sys.argv", ["open_event.py", "https://meet.google.com/abc-def-ghi"])
    @patch("ocu.open_event.should_open_google_meet_app")
    @patch("ocu.open_event.open_url_no_app")
    def test_main_exception_handling(self, mock_open_no_app, mock_should_open):
        """
        main should handle unexpected exceptions gracefully and fallback to
        default browser
        """
        mock_should_open.side_effect = Exception("Unexpected error")
        stderr_capture = self.capture_stderr()

        open_event.main()

        stderr_output = stderr_capture.getvalue()
        self.assertIn(
            "Error processing conference URL: Unexpected error", stderr_output
        )
        mock_open_no_app.assert_called_once_with("https://meet.google.com/abc-def-ghi")

    @patch(
        "sys.argv", ["open_event.py", "zoommtg://zoom.us/join?confno=123456789&pwd=abc"]
    )
    @patch("ocu.open_event.open_url_no_app")
    def test_main_zoom_native_protocol(self, mock_open_no_app):
        """main should handle Zoom native protocol URLs correctly"""
        stderr_capture = self.capture_stderr()

        open_event.main()

        stderr_output = stderr_capture.getvalue()
        self.assertIn(
            "Opening conference URL: zoommtg://zoom.us/join?confno=123456789&pwd=abc",
            stderr_output,
        )
        mock_open_no_app.assert_called_once_with(
            "zoommtg://zoom.us/join?confno=123456789&pwd=abc"
        )

    @patch(
        "sys.argv", ["open_event.py", "msteams://teams.microsoft.com/l/meetup-join/123"]
    )
    @patch("ocu.open_event.open_url_no_app")
    def test_main_teams_native_protocol(self, mock_open_no_app):
        """main should handle Teams native protocol URLs correctly"""
        stderr_capture = self.capture_stderr()

        open_event.main()

        stderr_output = stderr_capture.getvalue()
        self.assertIn(
            "Opening conference URL: msteams://teams.microsoft.com/l/meetup-join/123",
            stderr_output,
        )
        mock_open_no_app.assert_called_once_with(
            "msteams://teams.microsoft.com/l/meetup-join/123"
        )
