"""External IP checking with multi-source fallback."""

import subprocess
import threading
import time
from urllib.parse import urlparse

from ip_guardian.config import resolve_ip_sources


class IPChecker:
    """Checks and caches the external IP address."""

    def __init__(
        self,
        allowed_ips,
        interval=30,
        ip_sources=None,
        source_timeout=5,
    ):
        self.allowed_ips = allowed_ips
        self.interval = interval
        self.ip_sources = resolve_ip_sources(ip_sources)
        self.source_timeout = source_timeout
        self.current_ip = None
        self.current_source = None
        self.last_check = 0
        self.status = "unknown"  # "allowed", "blocked", "error"
        self._lock = threading.Lock()
        self._callbacks = []

    def fetch_ip(self):
        """Fetch external IP from configured sources with fallback."""
        for source in self.ip_sources:
            ip = self._fetch_from_source(source)
            if ip:
                return ip, self._source_label(source)
        return None, None

    def _fetch_from_source(self, source):
        """Fetch and validate IP from a single source."""
        try:
            result = subprocess.run(
                [
                    "curl",
                    "-fsS",
                    "--max-time",
                    str(self.source_timeout),
                    source,
                ],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                return None
            ip = result.stdout.strip()
            if ip and self._is_valid_ip(ip):
                return ip
            return None
        except Exception:
            return None

    def check(self):
        """Check IP and update status. Returns (ip, status)."""
        ip, source = self.fetch_ip()
        with self._lock:
            if ip is None:
                self.status = "error"
                self.current_source = None
            elif ip in self.allowed_ips:
                self.current_ip = ip
                self.current_source = source
                self.status = "allowed"
            else:
                self.current_ip = ip
                self.current_source = source
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

    @staticmethod
    def _source_label(source):
        parsed = urlparse(source)
        return parsed.netloc or source
