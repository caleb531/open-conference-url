#!/usr/bin/env python3

from typing import Optional

import pytest
from dotenv import load_dotenv


@pytest.hookimpl(tryfirst=True)
def pytest_report_teststatus(
    report: pytest.TestReport, config: pytest.Config
) -> Optional[tuple[str, str, str]]:
    if report.passed and report.when == "call":
        # Silence the dot progress output for successful call phases
        return report.outcome, "", report.outcome.upper()
    return None


@pytest.fixture(autouse=True, scope="session")
def load_tests_env():
    """Load test-specific environment variables for the entire test session."""
    load_dotenv("tests/.env.test")
