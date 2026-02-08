"""Manage Launch at Login via macOS LaunchAgent."""

import os
import plistlib
import subprocess
import sys

LABEL = "com.ipguardian.app"
PLIST_NAME = f"{LABEL}.plist"
PLIST_PATH = os.path.expanduser(f"~/Library/LaunchAgents/{PLIST_NAME}")


def _get_app_path():
    """Get the path to launch the app."""
    if getattr(sys, "frozen", False):
        # Running as .app bundle — open the .app itself
        # sys.executable is inside .app/Contents/MacOS/
        return os.path.abspath(
            os.path.join(os.path.dirname(sys.executable), "..", "..")
        )
    # Running as script — use the shell wrapper .app
    return os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "IP Guardian.app", "Contents", "MacOS", "ip-guardian",
    )


def is_enabled():
    """Check if launch at login is enabled."""
    return os.path.exists(PLIST_PATH)


def enable():
    """Create LaunchAgent plist and register with launchctl."""
    app_path = _get_app_path()
    if getattr(sys, "frozen", False):
        # .app bundle: use 'open' command
        args = ["/usr/bin/open", app_path]
    else:
        args = [app_path]
    plist = {
        "Label": LABEL,
        "ProgramArguments": args,
        "RunAtLoad": True,
        "KeepAlive": False,
        "StandardOutPath": "/tmp/ip_guardian.log",
        "StandardErrorPath": "/tmp/ip_guardian.err",
    }
    os.makedirs(os.path.dirname(PLIST_PATH), exist_ok=True)
    with open(PLIST_PATH, "wb") as f:
        plistlib.dump(plist, f)
    uid = os.getuid()
    subprocess.run(
        ["launchctl", "bootstrap", f"gui/{uid}", PLIST_PATH],
        check=False,
    )


def disable():
    """Unregister from launchctl and remove plist."""
    uid = os.getuid()
    subprocess.run(
        ["launchctl", "bootout", f"gui/{uid}/{LABEL}"],
        check=False,
    )
    if os.path.exists(PLIST_PATH):
        os.remove(PLIST_PATH)
