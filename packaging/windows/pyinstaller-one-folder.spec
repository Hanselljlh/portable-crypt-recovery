# PyInstaller spec for Windows one-folder build
# Usage: pyinstaller packaging/windows/pyinstaller-one-folder.spec

import sys
from pathlib import Path

repo_root = Path(SPECPATH).parent.parent
src_dir = str(repo_root / "src")

block_cipher = None

a = Analysis(
    [str(repo_root / "src" / "portable_crypt_recovery" / "main.py")],
    pathex=[src_dir],
    binaries=[],
    datas=[
        (str(repo_root / "docs"), "docs"),
    ],
    hiddenimports=[
        "portable_crypt_recovery",
        "portable_crypt_recovery.app",
        "portable_crypt_recovery.core",
        "portable_crypt_recovery.models",
        "portable_crypt_recovery.workspace",
        "portable_crypt_recovery.services",
        "portable_crypt_recovery.ui",
        "PySide6.QtCore",
        "PySide6.QtGui",
        "PySide6.QtWidgets",
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
    name="PCR",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="PCR",
)
