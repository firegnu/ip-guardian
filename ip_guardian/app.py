"""IP Guardian - macOS menu bar app for IP-based app blocking."""

import os
import sys
import threading
import subprocess
import rumps

from ip_guardian.config import load_config, get_config_path
from ip_guardian.ip_checker import IPChecker
from ip_guardian.app_monitor import AppMonitor
from ip_guardian.cli_guard import generate_wrappers
from ip_guardian import autostart


def _icons_dir():
    if getattr(sys, "frozen", False):
        return os.path.join(os.path.dirname(sys.executable), "..", "Resources", "icons")
    return os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "icons"
    )


STATUS_ICONS = {
    k: os.path.join(_icons_dir(), f"{k}.png")
    for k in ("allowed", "blocked", "error", "unknown")
}


class IPGuardianApp(rumps.App):
    """Menu bar application for IP Guardian."""

    def __init__(self):
        super().__init__(
            "IP Guardian",
            icon=STATUS_ICONS["unknown"],
            title=None,
            template=True,
        )
        self.config = load_config()
        self.checker = IPChecker(
            self.config["allowed_ips"],
            self.config.get("check_interval", 30),
            ip_sources=self.config.get("ip_sources"),
        )
        self.monitor = AppMonitor(self.config["gui_apps"], self.checker)
        self._setup_menu()
        self._setup_cli_guard()
        self._setup_app_monitor()
        self._start_periodic_check()

    def _setup_menu(self):
        self.ip_item = rumps.MenuItem("IP: checking...")
        self.source_item = rumps.MenuItem("Source: checking...")
        self.status_item = rumps.MenuItem("Status: unknown")
        self.autostart_item = rumps.MenuItem(
            "Launch at Login", callback=self._on_toggle_autostart
        )
        self.autostart_item.state = autostart.is_enabled()
        self.menu = [
            self.ip_item,
            self.source_item,
            self.status_item,
            None,
            rumps.MenuItem("Refresh Now", callback=self._on_refresh),
            rumps.MenuItem("Open Config", callback=self._on_open_config),
            self.autostart_item,
        ]

    def _setup_cli_guard(self):
        generate_wrappers(
            self.config["cli_commands"],
            self.config["allowed_ips"],
            ip_sources=self.config.get("ip_sources"),
        )

    def _setup_app_monitor(self):
        self.monitor.on_blocked(self._on_app_blocked)
        self.monitor.start()

    def _start_periodic_check(self):
        interval = self.config.get("check_interval", 30)
        self.timer = rumps.Timer(self._on_timer, interval)
        self.timer.start()
        # Do an immediate first check
        threading.Thread(target=self._do_check, daemon=True).start()

    def _do_check(self):
        ip, status = self.checker.check()
        self._update_ui(ip, status)

    def _update_ui(self, ip, status):
        icon_path = STATUS_ICONS.get(status, STATUS_ICONS["unknown"])
        self.icon = icon_path
        self.title = None
        self.ip_item.title = f"IP: {ip or 'unknown'}"
        self.source_item.title = f"Source: {self.checker.current_source or 'unknown'}"
        self.status_item.title = f"Status: {status}"

    def _on_timer(self, _):
        threading.Thread(target=self._do_check, daemon=True).start()

    def _on_refresh(self, _):
        threading.Thread(target=self._do_check, daemon=True).start()

    def _on_open_config(self, _):
        subprocess.run(["open", get_config_path()], check=False)

    def _on_app_blocked(self, app_name):
        ip = self.checker.current_ip or "unknown"
        self._send_notification(
            f"{app_name} blocked",
            f"IP ({ip}) is not in the allowed list.",
        )

    def _on_toggle_autostart(self, sender):
        if autostart.is_enabled():
            autostart.disable()
            sender.state = False
            self._send_notification("Launch at Login", "Disabled.")
        else:
            autostart.enable()
            sender.state = True
            self._send_notification("Launch at Login", "Enabled.")

    @staticmethod
    def _send_notification(title, message):
        script = (
            f'display notification "{message}" '
            f'with title "IP Guardian" subtitle "{title}"'
        )
        subprocess.run(["osascript", "-e", script], check=False)


def main():
    IPGuardianApp().run()


if __name__ == "__main__":
    main()
