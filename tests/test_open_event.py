#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from io import StringIO
from unittest.mock import patch

import pytest

from ocu import open_event
from tests.utils import use_env

ORIGINAL_STDERR = sys.stderr

NON_GOOGLE_URLS = [
    "https://zoom.us/j/123456789",
    "https://teams.microsoft.com/l/meetup-join/123",
    "https://example.com/meeting",
    "https://meet.google.co.uk/abc-def-ghi",
]

GOOGLE_MEET_URLS = [
    "https://meet.google.com/abc-def-ghi",
    "https://meet.google.com/xyz-123-456?authuser=0",
]


def teardown_function(_function):
    """Ensure stderr is restored after each test."""
    sys.stderr = ORIGINAL_STDERR


def capture_stderr():
    """Capture stderr output for the duration of a test."""
    stderr_capture = StringIO()
    sys.stderr = stderr_capture
    return stderr_capture


def test_should_open_google_meet_app_with_none_url():
    """should_open_google_meet_app should return False for None URL."""
    result = open_event.should_open_google_meet_app(None)
    assert not result


def test_should_open_google_meet_app_with_empty_url():
    """should_open_google_meet_app should return False for empty URL."""
    result = open_event.should_open_google_meet_app("")
    assert not result


@pytest.mark.parametrize("url", NON_GOOGLE_URLS)
def test_should_open_google_meet_app_with_non_google_url(url):
    """should_open_google_meet_app should return False for non-Google URLs."""
    result = open_event.should_open_google_meet_app(url)
    assert not result


@pytest.mark.parametrize("url", GOOGLE_MEET_URLS)
@use_env("use_direct_gmeet", "true")
def test_should_open_google_meet_app_with_google_url_and_pref_enabled(url):
    """should_open_google_meet_app should return True when preference enabled."""
    result = open_event.should_open_google_meet_app(url)
    assert result


@use_env("use_direct_gmeet", "false")
def test_should_open_google_meet_app_with_google_url_and_pref_disabled():
    """should_open_google_meet_app should return False when preference disabled."""
    url = "https://meet.google.com/abc-def-ghi"
    result = open_event.should_open_google_meet_app(url)
    assert not result


@use_env("use_direct_gmeet", "")
def test_should_open_google_meet_app_with_google_url_and_pref_unset():
    """should_open_google_meet_app should default to False when unset."""
    url = "https://meet.google.com/abc-def-ghi"
    result = open_event.should_open_google_meet_app(url)
    assert not result


def test_should_open_google_meet_app_with_missing_pref_key():
    """should_open_google_meet_app should handle missing preference key."""
    url = "https://meet.google.com/abc-def-ghi"

    with patch.dict(os.environ, {}, clear=True):
        result = open_event.should_open_google_meet_app(url)
        assert not result


@patch("subprocess.run")
def test_open_url_with_native_app_success(mock_run):
    """open_url_with_native_app should successfully open URL with native app."""
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
def test_open_url_with_native_app_subprocess_error(mock_open_no_app, mock_run):
    """open_url_with_native_app should fallback to browser on subprocess error."""
    from subprocess import CalledProcessError

    mock_run.side_effect = CalledProcessError(1, ["open"])
    stderr_capture = capture_stderr()

    open_event.open_url_with_native_app(
        "https://meet.google.com/abc-def-ghi", "Google Meet"
    )

    stderr_output = stderr_capture.getvalue()
    assert "Failed to open URL with Google Meet" in stderr_output
    mock_open_no_app.assert_called_once_with("https://meet.google.com/abc-def-ghi")


@patch("subprocess.run")
@patch("ocu.open_event.open_url_no_app")
def test_open_url_with_native_app_file_not_found(mock_open_no_app, mock_run):
    """open_url_with_native_app should fallback when app missing."""
    mock_run.side_effect = FileNotFoundError("Application not found")
    stderr_capture = capture_stderr()

    open_event.open_url_with_native_app(
        "https://meet.google.com/abc-def-ghi", "Google Meet"
    )

    stderr_output = stderr_capture.getvalue()
    assert "Application Google Meet not found" in stderr_output
    assert "opening with default browser" in stderr_output
    mock_open_no_app.assert_called_once_with("https://meet.google.com/abc-def-ghi")


@patch("subprocess.run")
def test_open_url_no_app_success(mock_run):
    """open_url_no_app should successfully open URL with default browser."""
    mock_run.return_value = None

    open_event.open_url_no_app("https://example.com")

    mock_run.assert_called_once_with(["open", "https://example.com"], check=True)


@patch("subprocess.run")
@patch("sys.exit")
def test_open_url_no_app_failure(mock_exit, mock_run):
    """open_url_no_app should exit with error code on failure."""
    from subprocess import CalledProcessError

    mock_run.side_effect = CalledProcessError(1, ["open"])
    stderr_capture = capture_stderr()

    open_event.open_url_no_app("https://example.com")

    stderr_output = stderr_capture.getvalue()
    assert "Failed to open URL" in stderr_output
    mock_exit.assert_called_once_with(1)


@patch("sys.argv", ["open_event.py"])
@patch("sys.exit")
def test_main_no_arguments(mock_exit):
    """main should exit with usage message when no arguments provided."""
    mock_exit.side_effect = SystemExit(1)
    stderr_capture = capture_stderr()

    with pytest.raises(SystemExit):
        open_event.main()

    stderr_output = stderr_capture.getvalue()
    assert "Usage: open-event.py <conference_url>" in stderr_output
    mock_exit.assert_called_once_with(1)


@patch("sys.argv", ["open_event.py", "https://zoom.us/j/123456789"])
@patch("ocu.open_event.open_url_no_app")
def test_main_non_google_meet_url(mock_open_no_app):
    """main should open non-Google Meet URLs with default handler."""
    stderr_capture = capture_stderr()

    open_event.main()

    stderr_output = stderr_capture.getvalue()
    assert "Opening conference URL: https://zoom.us/j/123456789" in stderr_output
    mock_open_no_app.assert_called_once_with("https://zoom.us/j/123456789")


@patch("sys.argv", ["open_event.py", "https://meet.google.com/abc-def-ghi"])
@patch("ocu.open_event.open_url_no_app")
@use_env("use_direct_gmeet", "false")
def test_main_google_meet_url_pref_disabled(mock_open_no_app):
    """main should open Google Meet URLs with default handler when disabled."""
    stderr_capture = capture_stderr()

    open_event.main()

    stderr_output = stderr_capture.getvalue()
    assert (
        "Opening conference URL: https://meet.google.com/abc-def-ghi" in stderr_output
    )
    mock_open_no_app.assert_called_once_with("https://meet.google.com/abc-def-ghi")


@patch("sys.argv", ["open_event.py", "https://meet.google.com/abc-def-ghi"])
@patch("ocu.open_event.open_url_with_native_app")
@use_env("use_direct_gmeet", "true")
@use_env("gmeet_app_name", "Google Meet")
def test_main_google_meet_url_pref_enabled_default_app(mock_open_with_app):
    """main should open Google Meet URLs with native app when preference enabled."""
    stderr_capture = capture_stderr()

    open_event.main()

    stderr_output = stderr_capture.getvalue()
    url = "https://meet.google.com/abc-def-ghi"
    assert f"Opening Google Meet URL in Desktop app: {url}" in stderr_output
    mock_open_with_app.assert_called_once_with(
        "https://meet.google.com/abc-def-ghi", "Google Meet"
    )


@patch("sys.argv", ["open_event.py", "https://meet.google.com/abc-def-ghi"])
@patch("ocu.open_event.open_url_with_native_app")
@use_env("use_direct_gmeet", "true")
@use_env("gmeet_app_name", "Custom Meet App")
def test_main_google_meet_url_pref_enabled_custom_app(mock_open_with_app):
    """main should open Google Meet URLs with custom app when configured."""
    stderr_capture = capture_stderr()

    open_event.main()

    stderr_output = stderr_capture.getvalue()
    url = "https://meet.google.com/abc-def-ghi"
    assert f"Opening Google Meet URL in Desktop app: {url}" in stderr_output
    mock_open_with_app.assert_called_once_with(
        "https://meet.google.com/abc-def-ghi", "Custom Meet App"
    )


@patch("sys.argv", ["open_event.py", "https://meet.google.com/abc-def-ghi"])
@patch("ocu.open_event.open_url_with_native_app")
@use_env("use_direct_gmeet", "true")
@use_env("gmeet_app_name", "")
def test_main_google_meet_url_empty_app_name(mock_open_with_app):
    """main should use default app name when gmeet_app_name is empty."""
    stderr_capture = capture_stderr()

    open_event.main()

    stderr_output = stderr_capture.getvalue()
    url = "https://meet.google.com/abc-def-ghi"
    assert f"Opening Google Meet URL in Desktop app: {url}" in stderr_output
    mock_open_with_app.assert_called_once_with(
        "https://meet.google.com/abc-def-ghi", "Google Meet"
    )


@patch("sys.argv", ["open_event.py", "https://meet.google.com/abc-def-ghi"])
@patch("ocu.open_event.should_open_google_meet_app")
@patch("ocu.open_event.open_url_no_app")
def test_main_exception_handling(mock_open_no_app, mock_should_open):
    """main should handle unexpected exceptions gracefully and fallback."""
    mock_should_open.side_effect = Exception("Unexpected error")
    stderr_capture = capture_stderr()

    open_event.main()

    stderr_output = stderr_capture.getvalue()
    assert "Error processing conference URL: Unexpected error" in stderr_output
    mock_open_no_app.assert_called_once_with("https://meet.google.com/abc-def-ghi")


@patch("sys.argv", ["open_event.py", "zoommtg://zoom.us/join?confno=123456789&pwd=abc"])
@patch("ocu.open_event.open_url_no_app")
def test_main_zoom_native_protocol(mock_open_no_app):
    """main should handle Zoom native protocol URLs correctly."""
    stderr_capture = capture_stderr()

    open_event.main()

    stderr_output = stderr_capture.getvalue()
    assert (
        "Opening conference URL: zoommtg://zoom.us/join?confno=123456789&pwd=abc"
        in stderr_output
    )
    mock_open_no_app.assert_called_once_with(
        "zoommtg://zoom.us/join?confno=123456789&pwd=abc"
    )


@patch("sys.argv", ["open_event.py", "msteams://teams.microsoft.com/l/meetup-join/123"])
@patch("ocu.open_event.open_url_no_app")
def test_main_teams_native_protocol(mock_open_no_app):
    """main should handle Teams native protocol URLs correctly."""
    stderr_capture = capture_stderr()

    open_event.main()

    stderr_output = stderr_capture.getvalue()
    assert (
        "Opening conference URL: msteams://teams.microsoft.com/l/meetup-join/123"
        in stderr_output
    )
    mock_open_no_app.assert_called_once_with(
        "msteams://teams.microsoft.com/l/meetup-join/123"
    )
