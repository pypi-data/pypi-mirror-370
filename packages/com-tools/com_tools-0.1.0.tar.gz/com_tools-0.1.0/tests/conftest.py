# conftest.py
import pytest
from com_tools.loggers import logger

def pytest_configure(config):
    """
    Configure logging for pytest.

    This hook is called once at the beginning of a test run.
    It sets up the basic logging configuration for the root logger,
    directing log messages to the console (standard error by default).
    """
    # Get the root logger
    root_logger = logger
