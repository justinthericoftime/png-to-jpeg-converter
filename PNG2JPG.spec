# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for PNG to JPEG Converter

Build command: pyinstaller PNG2JPG.spec

NOTE: This must be run on macOS to create a macOS .app bundle.
"""

import os

block_cipher = None

# Check if custom icon exists
icon_file = 'AppIcon.icns' if os.path.exists('AppIcon.icns') else None

a = Analysis(
    ['png2jpg_gui.py'],
    pathex=['.'],
    binaries=[],
    datas=[],
    hiddenimports=[
        'PIL',
        'PIL.Image',
        'PIL._tkinter_finder',
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='PNG2JPGConverter',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # Disabled - UPX often not installed on macOS
    console=False,  # No terminal window
    disable_windowed_traceback=False,
    argv_emulation=True,  # Important for macOS
    target_arch=None,  # Build for current architecture
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='PNG2JPGConverter',
)

# Build the macOS app bundle
app = BUNDLE(
    coll,
    name='PNG to JPEG Converter.app',
    icon=icon_file,
    bundle_identifier='com.png2jpg.converter',
    info_plist={
        'CFBundleName': 'PNG to JPEG Converter',
        'CFBundleDisplayName': 'PNG to JPEG Converter',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '10.13.0',
    },
)
