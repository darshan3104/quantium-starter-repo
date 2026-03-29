"""
conftest.py
-----------
Root-level pytest configuration.

Automatically downloads and registers the correct ChromeDriver binary
using webdriver-manager so that dash.testing (Selenium) can find it
without requiring a manual PATH setup.

Install once:
    pip install webdriver-manager
"""

import os
from webdriver_manager.chrome import ChromeDriverManager


def pytest_configure(config):
    """
    Hook that runs before any test collection or execution.
    Downloads the ChromeDriver binary matching the installed Chrome version
    and prepends its directory to the system PATH.
    """
    driver_path = ChromeDriverManager().install()        # downloads if needed
    driver_dir = os.path.dirname(driver_path)            # e.g. .../.wdm/drivers/chromedriver/...
    os.environ["PATH"] = driver_dir + os.pathsep + os.environ.get("PATH", "")
