"""Monitor and block GUI application launches via NSWorkspace."""

import subprocess

import objc
from AppKit import NSWorkspace, NSWorkspaceDidLaunchApplicationNotification
from Foundation import NSObject


class _Observer(NSObject):
    """NSObject subclass that receives workspace notifications."""

    def initWithHandler_(self, handler):
        self = objc.super(_Observer, self).init()
        if self is None:
            return None
        self._handler = handler
        return self

    def appLaunched_(self, notification):
        self._handler(notification)


class AppMonitor:
    """Watches for GUI app launches and blocks them if IP is not allowed."""

    def __init__(self, gui_apps, ip_checker):
        self.gui_apps = {app["bundle_id"]: app["name"] for app in gui_apps}
        self.ip_checker = ip_checker
        self._on_blocked = None
        self._observer = None

    def on_blocked(self, callback):
        """Register callback(app_name) when an app is blocked."""
        self._on_blocked = callback

    def start(self):
        """Start monitoring app launches."""
        self._observer = _Observer.alloc().initWithHandler_(
            self._handle_launch
        )
        workspace = NSWorkspace.sharedWorkspace()
        center = workspace.notificationCenter()
        center.addObserver_selector_name_object_(
            self._observer,
            b"appLaunched:",
            NSWorkspaceDidLaunchApplicationNotification,
            None,
        )

    def stop(self):
        """Stop monitoring."""
        if self._observer:
            workspace = NSWorkspace.sharedWorkspace()
            center = workspace.notificationCenter()
            center.removeObserver_(self._observer)

    def _handle_launch(self, notification):
        """Handle an app launch notification."""
        app_info = notification.userInfo()
        bundle_id = app_info.get("NSApplicationBundleIdentifier", "")
        if bundle_id not in self.gui_apps:
            return
        # Real-time IP check at launch time
        self.ip_checker.check()
        if self.ip_checker.is_allowed():
            return
        # Block: kill the app
        pid = int(app_info.get("NSApplicationProcessIdentifier", 0))
        app_name = self.gui_apps[bundle_id]
        if pid:
            try:
                subprocess.run(["kill", "-9", str(pid)], check=False)
            except Exception:
                pass
        if self._on_blocked:
            self._on_blocked(app_name)
