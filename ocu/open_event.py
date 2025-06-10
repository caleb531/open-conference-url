#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import subprocess
import sys
from typing import Optional

from ocu.prefs import PrefName, prefs


def should_open_google_meet_app(url: Optional[str]) -> bool:
    """
    Return True if the given URL is a Google Meet URL, and the user prefers to open it in the native app;
    return False otherwise
    """
    if not url:
        return False

    matches = re.search(r"https://(meet\.google\.com)", url)
    is_google_url = bool(matches)
    if not is_google_url:
        return False

    # Check if the user prefers to open Google Meet URLs in the native app
    try:
        return prefs["use_direct_gmeet"]
    except KeyError:
        print(
            "Preference 'use_direct_gmeet' not found, defaulting to False",
            file=sys.stderr,
        )
        return False


def open_url_with_native_app(url: str, app_name: str) -> None:
    """
    Open the given URL with the specified native application using macOS open command
    """
    try:
        subprocess.run(["open", "-a", app_name, url], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to open URL with {app_name}: {e}", file=sys.stderr)
        # Fallback to default browser
        open_url_no_app(url)
    except FileNotFoundError:
        print(
            f"Application {app_name} not found, opening with default browser",
            file=sys.stderr,
        )
        # Fallback to default browser
        open_url_no_app(url)


def open_url_no_app(url: str) -> None:
    """
    Open the given URL with the default browser/application
    """
    try:
        subprocess.run(["open", url], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to open URL: {e}", file=sys.stderr)
        sys.exit(1)


def get_pref_str_safely(pref_name: PrefName, default: str = "") -> str:
    """
    Safely get a string preference value, returning the default if the preference is not set
    """
    try:
        return prefs[pref_name]
    except KeyError:
        return default


def main() -> None:
    # Get the conference URL from command line arguments
    if len(sys.argv) < 2:
        print("Usage: open-event.py <conference_url>", file=sys.stderr)
        sys.exit(1)

    conference_url = sys.argv[1]

    try:
        # Check if this is a Google Meet URL and user prefers native app
        # Note: Zoom and Teams URLs are already converted to native protocols
        # (zoommtg:// and msteams://) by the Event class when preferences are enabled,
        # so they automatically open in native apps. Google Meet doesn't have a
        # custom protocol, so we need special handling with the -a flag.

        open_google_meet = should_open_google_meet_app(conference_url)
        if open_google_meet:
            print(
                f"Opening Google Meet URL in Desktop app: {conference_url}",
                file=sys.stderr,
            )

            # Get the configured Google Meet app name (default: "Google Meet")
            gmeet_app_name = get_pref_str_safely("gmeet_app_name", "Google Meet")
            open_url_with_native_app(conference_url, gmeet_app_name)
        else:
            print(
                f"Opening conference URL: {conference_url}",
                file=sys.stderr,
            )
            # For all other URLs (including Zoom/Teams with native protocols,
            # or when native app preference is disabled), open with default handler
            open_url_no_app(conference_url)

    except Exception as e:
        print(f"Error processing conference URL: {e}", file=sys.stderr)
        # Fallback to default browser
        open_url_no_app(conference_url)


if __name__ == "__main__":
    main()
