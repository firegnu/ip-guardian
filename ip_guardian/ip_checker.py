"""External IP checking via ifconfig.me."""

import subprocess
import threading
import time


class IPChecker:
    """Checks and caches the external IP address."""

    def __init__(self, allowed_ips, interval=30):
        self.allowed_ips = allowed_ips
        self.interval = interval
        self.current_ip = None
        self.last_check = 0
        self.status = "unknown"  # "allowed", "blocked", "error"
        self._lock = threading.Lock()
        self._callbacks = []

    def fetch_ip(self):
        """Fetch external IP via curl ifconfig.me."""
        try:
            result = subprocess.run(
                ["curl", "-s", "--max-time", "5", "ifconfig.me"],
                capture_output=True,
                text=True,
            )
            ip = result.stdout.strip()
            if ip and self._is_valid_ip(ip):
                return ip
            return None
        except Exception:
            return None

    def check(self):
        """Check IP and update status. Returns (ip, status)."""
        ip = self.fetch_ip()
        with self._lock:
            if ip is None:
                self.status = "error"
            elif ip in self.allowed_ips:
                self.current_ip = ip
                self.status = "allowed"
            else:
                self.current_ip = ip
                self.status = "blocked"
            self.last_check = time.time()
        self._notify()
        return self.current_ip, self.status

    def is_allowed(self):
        """Return True if current IP is in allowed list."""
        with self._lock:
            return self.status == "allowed"

    def on_change(self, callback):
        """Register a callback for status changes."""
        self._callbacks.append(callback)

    def _notify(self):
        for cb in self._callbacks:
            try:
                cb(self.current_ip, self.status)
            except Exception:
                pass

    @staticmethod
    def _is_valid_ip(ip):
        parts = ip.split(".")
        if len(parts) != 4:
            return False
        return all(p.isdigit() and 0 <= int(p) <= 255 for p in parts)
