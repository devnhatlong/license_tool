# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['generate_license.py'],
    pathex=[],
    binaries=[],
    datas=[
        # Chỉ gói icon + logo cỡ nhỏ (không gói logo.png gốc cho nhẹ file .exe)
        ('assets/logo.ico', 'assets'),
        ('assets/logo_48.png', 'assets'),
        ('assets/logo_72.png', 'assets'),
        ('assets/logo_96.png', 'assets'),
    ],
    hiddenimports=['utils.license_utils'],
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
    a.binaries,
    a.datas,
    [],
    name='generate_license',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI application
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/logo.ico',  # Icon cho file .exe
)