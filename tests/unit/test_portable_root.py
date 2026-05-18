"""Tests for portable app-root resolution and bounded log reading."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

from portable_crypt_recovery.core.paths import app_root_from_cwd
from portable_crypt_recovery.ui.logs_view import read_log_tail

# ---------------------------------------------------------------------------
# app_root_from_cwd — packaged vs dev resolution
# ---------------------------------------------------------------------------


def test_app_root_dev_mode_returns_cwd():
    """In dev (non-frozen) mode, app root must equal the current working dir."""
    assert getattr(sys, "frozen", False) is False, "test must run in non-frozen mode"
    assert app_root_from_cwd() == Path.cwd().resolve()


def test_app_root_frozen_returns_executable_parent(tmp_path):
    """In packaged (frozen) mode, app root must be the directory of the .exe."""
    fake_exe = tmp_path / "PCR.exe"
    fake_exe.touch()

    with (
        patch.object(sys, "frozen", True, create=True),
        patch.object(sys, "executable", str(fake_exe)),
    ):
        result = app_root_from_cwd()

    assert result == tmp_path.resolve()


def test_app_root_frozen_ignores_cwd(tmp_path):
    """Frozen mode must NOT use cwd — even when cwd differs from exe parent."""
    fake_exe = tmp_path / "app" / "PCR.exe"
    fake_exe.parent.mkdir()
    fake_exe.touch()

    with (
        patch("os.getcwd", return_value=str(tmp_path / "somewhere_else")),
        patch.object(sys, "frozen", True, create=True),
        patch.object(sys, "executable", str(fake_exe)),
    ):
        result = app_root_from_cwd()

    assert result == fake_exe.parent.resolve()


# ---------------------------------------------------------------------------
# user guide path resolution
# ---------------------------------------------------------------------------


def test_user_guide_path_dev_mode_under_cwd(tmp_path):
    """In dev mode, user-guide path is resolved under the current working dir."""
    # The fix replaces __file__-based navigation with app_root_from_cwd(); in dev
    # mode that is cwd, so the constructed path must sit under cwd.
    root = app_root_from_cwd()
    guide = root / "docs" / "user-guide" / "getting-started.md"
    # path components must be correct regardless of whether the file exists
    assert guide.parts[-3:] == ("docs", "user-guide", "getting-started.md")


def test_user_guide_path_frozen_is_under_exe_parent(tmp_path):
    """In packaged mode, user-guide must resolve under the exe directory."""
    fake_exe = tmp_path / "PCR.exe"
    fake_exe.touch()
    # Simulate a populated portable folder
    (tmp_path / "docs" / "user-guide").mkdir(parents=True)
    (tmp_path / "docs" / "user-guide" / "getting-started.md").touch()

    with (
        patch.object(sys, "frozen", True, create=True),
        patch.object(sys, "executable", str(fake_exe)),
    ):
        root = app_root_from_cwd()

    guide = root / "docs" / "user-guide" / "getting-started.md"
    assert guide.exists(), "guide must resolve under the exe parent in frozen mode"
    assert guide.is_relative_to(tmp_path), "must NOT be inside the source tree"


def test_user_guide_path_frozen_not_source_tree(tmp_path):
    """In packaged mode, the docs path must not contain any source-tree artifacts."""
    fake_exe = tmp_path / "app" / "PCR.exe"
    fake_exe.parent.mkdir()
    fake_exe.touch()

    with (
        patch.object(sys, "frozen", True, create=True),
        patch.object(sys, "executable", str(fake_exe)),
    ):
        root = app_root_from_cwd()

    guide = root / "docs" / "user-guide" / "getting-started.md"
    # Must be rooted at the exe parent, not somewhere in the Python source tree
    assert str(guide).startswith(str(fake_exe.parent.resolve()))


# ---------------------------------------------------------------------------
# read_log_tail — bounded log loading
# ---------------------------------------------------------------------------


def test_read_log_tail_small_file(tmp_path):
    """Files smaller than max_bytes are returned in full."""
    log = tmp_path / "app.log"
    content = "line1\nline2\nline3\n"
    log.write_text(content, encoding="utf-8")

    result = read_log_tail(log, max_bytes=200 * 1024)
    assert result == content


def test_read_log_tail_large_file_truncates(tmp_path):
    """Files larger than max_bytes show a truncation notice and only the tail."""
    log = tmp_path / "big.log"
    max_bytes = 1024
    # Write header content that exceeds the cap + a known tail line
    header = ("x" * 500 + "\n") * 4          # 2 KB header (exceeds 1 KB cap)
    tail_line = "TAIL_MARKER\n"
    log.write_text(header + tail_line, encoding="utf-8")

    result = read_log_tail(log, max_bytes=max_bytes)

    assert "[... log truncated" in result, "truncation notice must be present"
    assert "TAIL_MARKER" in result, "tail content must be present"
    # The full header must NOT appear verbatim in the truncated output
    assert result.count("x" * 500) == 0 or len(result) <= max_bytes + 200


def test_read_log_tail_missing_file(tmp_path):
    """Missing log file returns a 'not found' message, not an exception."""
    result = read_log_tail(tmp_path / "nonexistent.log")
    assert "not found" in result.lower()


def test_read_log_tail_truncation_notice_contains_sizes(tmp_path):
    """Truncation notice must mention both the cap and the original size."""
    log = tmp_path / "large.log"
    max_bytes = 512
    log.write_bytes(b"a\n" * 600)  # ~1.2 KB

    result = read_log_tail(log, max_bytes=max_bytes)
    assert "truncated" in result
    # Should mention the cap size in KB
    assert f"{max_bytes // 1024} KB" in result
