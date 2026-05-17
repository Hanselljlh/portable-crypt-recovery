# PyInstaller spec for Windows one-folder build (PyInstaller 6.x)
# Usage: pyinstaller packaging/windows/pyinstaller-one-folder.spec

from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

repo_root = Path(SPECPATH).parent.parent
src_dir = str(repo_root / "src")

hidden = (
    collect_submodules("portable_crypt_recovery")
    + ["PySide6.QtCore", "PySide6.QtGui", "PySide6.QtWidgets"]
)

a = Analysis(
    [str(repo_root / "src" / "portable_crypt_recovery" / "main.py")],
    pathex=[src_dir],
    binaries=[],
    datas=[
        (str(repo_root / "docs"), "docs"),
    ],
    hiddenimports=hidden,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "unittest", "email", "xml", "http", "multiprocessing"],
)

pyz = PYZ(a.pure)

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
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=["vcruntime140.dll", "msvcp140.dll"],
    name="PCR",
)
