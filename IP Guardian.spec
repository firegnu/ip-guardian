# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['ip_guardian/app.py'],
    pathex=[],
    binaries=[],
    datas=[('icons', 'icons'), ('config.json', '.')],
    hiddenimports=['rumps', 'objc', 'AppKit', 'Foundation'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='IP Guardian',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='IP Guardian',
)
app = BUNDLE(
    coll,
    name='IP Guardian.app',
    icon=None,
    bundle_identifier='com.ipguardian.app',
)
