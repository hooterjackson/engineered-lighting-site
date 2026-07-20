"""Serve the built site/ directory for the e2e suite.

Run `mkdocs build` before pytest — CI does this explicitly.
PLAYWRIGHT_CHROMIUM_EXECUTABLE overrides the browser binary (local dev
convenience when the cached build doesn't match the driver; unset in CI).
"""
import os
import pathlib
import socket
import subprocess
import time

import pytest

SITE = pathlib.Path(__file__).resolve().parents[2] / "site"
PORT = 4173


@pytest.fixture(scope="session", autouse=True)
def site_server():
    assert SITE.is_dir(), "site/ not found — run `mkdocs build` first"
    proc = subprocess.Popen(
        ["python3", "-m", "http.server", str(PORT), "--bind", "127.0.0.1",
         "--directory", str(SITE)],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    for _ in range(50):
        try:
            with socket.create_connection(("127.0.0.1", PORT), timeout=0.2):
                break
        except OSError:
            time.sleep(0.1)
    yield
    proc.terminate()
    proc.wait(timeout=5)


@pytest.fixture(scope="session")
def base_url():
    return f"http://127.0.0.1:{PORT}"


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    exe = os.environ.get("PLAYWRIGHT_CHROMIUM_EXECUTABLE")
    if exe and pathlib.Path(exe).exists():
        return {**browser_type_launch_args, "executable_path": exe}
    return browser_type_launch_args
