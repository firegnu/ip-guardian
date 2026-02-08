"""Configuration management for IP Guardian."""

import json
import os
import shutil
import sys

CONFIG_DIR = os.path.expanduser("~/.ip_guardian")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")


def _get_bundled_config():
    """Get path to bundled default config (for first-run copy)."""
    if getattr(sys, "frozen", False):
        # Running as py2app bundle
        return os.path.join(os.path.dirname(sys.executable), "..", "Resources", "config.json")
    # Running as script
    return os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "config.json",
    )


def _ensure_config():
    """Copy default config to ~/.ip_guardian/ if not exists."""
    if os.path.exists(CONFIG_PATH):
        return
    os.makedirs(CONFIG_DIR, exist_ok=True)
    bundled = _get_bundled_config()
    if os.path.exists(bundled):
        shutil.copy2(bundled, CONFIG_PATH)


def load_config(path=None):
    """Load configuration from JSON file."""
    _ensure_config()
    path = path or CONFIG_PATH
    with open(path, "r") as f:
        return json.load(f)


def save_config(config, path=None):
    """Save configuration to JSON file."""
    path = path or CONFIG_PATH
    with open(path, "w") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
        f.write("\n")


def get_config_path():
    """Return the config file path."""
    return CONFIG_PATH
