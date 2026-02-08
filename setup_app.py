"""py2app build script for IP Guardian."""

from setuptools import setup

APP = ["ip_guardian/app.py"]
DATA_FILES = [
    ("icons", [
        "icons/allowed.png",
        "icons/blocked.png",
        "icons/error.png",
        "icons/unknown.png",
    ]),
    ("", ["config.json"]),
]
OPTIONS = {
    "argv_emulation": False,
    "iconfile": None,
    "plist": {
        "CFBundleName": "IP Guardian",
        "CFBundleDisplayName": "IP Guardian",
        "CFBundleIdentifier": "com.ipguardian.app",
        "CFBundleVersion": "1.0.0",
        "CFBundleShortVersionString": "1.0.0",
        "LSUIElement": True,
    },
    "packages": ["ip_guardian"],
    "includes": [
        "rumps",
        "objc",
        "AppKit",
        "Foundation",
    ],
}

setup(
    app=APP,
    name="IP Guardian",
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
