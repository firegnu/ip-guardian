"""py2app build script for IP Guardian."""

import os
import sys

from setuptools import setup

sys.setrecursionlimit(5000)

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

LIBFFI_CANDIDATES = (
    "/opt/anaconda3/lib/libffi.8.dylib",
    "/usr/local/lib/libffi.8.dylib",
)
FRAMEWORKS = [path for path in LIBFFI_CANDIDATES if os.path.exists(path)]

OPTIONS = {
    "argv_emulation": False,
    "iconfile": "icons/app.icns" if os.path.exists("icons/app.icns") else None,
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
    "excludes": [
        "numpy", "docutils", "setuptools", "pkg_resources",
        "PIL", "matplotlib", "scipy", "pandas", "pytest",
        "IPython", "jupyter", "notebook", "sphinx",
        "black", "mypy", "pylint", "tkinter",
    ],
    "frameworks": FRAMEWORKS,
}

setup(
    app=APP,
    name="IP Guardian",
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
