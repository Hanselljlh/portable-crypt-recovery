"""Password Builder view — segment-based wordlist builder with workspace export."""

from __future__ import annotations


class PasswordBuilderView:  # pragma: no cover
    """Segment-based password builder.  Saves wordlists to generated/wordlists/."""

    def __new__(cls):
        from PySide6.QtCore import Qt
        from PySide6.QtWidgets import (
            QAbstractItemView,
            QFrame,
            QGroupBox,
            QHBoxLayout,
            QLabel,
            QLineEdit,
            QListWidget,
            QPushButton,
            QSplitter,
            QVBoxLayout,
            QWidget,
        )

        class _PasswordBuilderView(QWidget):
            def __init__(self) -> None:
                super().__init__()
                # _segments: ordered list; each element is an ordered list of
                # variant strings for that position.
                self._segments: list[list[str]] = []

                main_layout = QVBoxLayout(self)

                # ── top toolbar ──────────────────────────────────────────────
                top_bar = QHBoxLayout()
                lbl_title = QLabel("<b>Password Builder</b>")
                lbl_hint = QLabel(
                    "Build ordered segments, expand variants, then generate a wordlist."
                )
                lbl_hint.setStyleSheet("color: gray; font-size: 11px;")
                top_bar.addWidget(lbl_title)
                top_bar.addWidget(lbl_hint)
                top_bar.addStretch()
                main_layout.addLayout(top_bar)

                # ── main splitter ─────────────────────────────────────────────
                splitter = QSplitter(Qt.Orientation.Horizontal)

                # ─── LEFT: segment list + variant editor ──────────────────────
                left = QWidget()
                left_layout = QVBoxLayout(left)
                left_layout.setContentsMargins(0, 0, 4, 0)

                # Segment list
                seg_grp = QGroupBox("Segments (ordered — one value per segment joins to form a password)")
                seg_grp_layout = QVBoxLayout(seg_grp)

                seg_toolbar = QHBoxLayout()
                self.btn_seg_add = QPushButton("+ Add Segment")
                self.btn_seg_del = QPushButton("Remove")
                self.btn_seg_up = QPushButton("↑")
                self.btn_seg_dn = QPushButton("↓")
                self.btn_seg_up.setFixedWidth(30)
                self.btn_seg_dn.setFixedWidth(30)
                for _b in [self.btn_seg_add, self.btn_seg_del, self.btn_seg_up, self.btn_seg_dn]:
                    seg_toolbar.addWidget(_b)
                seg_toolbar.addStretch()
                seg_grp_layout.addLayout(seg_toolbar)

                self.seg_list = QListWidget()
                self.seg_list.setMinimumHeight(90)
                self.seg_list.setMaximumHeight(140)
                seg_grp_layout.addWidget(self.seg_list)

                left_layout.addWidget(seg_grp)

                # Variant editor
                self.edit_grp = QGroupBox("Edit Segment  (select a segment above)")
                edit_layout = QVBoxLayout(self.edit_grp)

                var_toolbar = QHBoxLayout()
                var_toolbar.addWidget(QLabel("Variants:"))
                var_toolbar.addStretch()
                self.btn_var_up = QPushButton("↑")
                self.btn_var_dn = QPushButton("↓")
                self.btn_var_del = QPushButton("Remove")
                self.btn_var_up.setFixedWidth(30)
                self.btn_var_dn.setFixedWidth(30)
                for _b in [self.btn_var_up, self.btn_var_dn, self.btn_var_del]:
                    var_toolbar.addWidget(_b)
                edit_layout.addLayout(var_toolbar)

                self.var_list = QListWidget()
                self.var_list.setMinimumHeight(120)
                edit_layout.addWidget(self.var_list, 1)

                add_row = QHBoxLayout()
                self.txt_variant = QLineEdit()
                self.txt_variant.setPlaceholderText(
                    "Type a variant and click Add  (or use expand buttons below)"
                )
                self.btn_var_add = QPushButton("Add")
                add_row.addWidget(self.txt_variant, 1)
                add_row.addWidget(self.btn_var_add)
                edit_layout.addLayout(add_row)

                expand_row = QHBoxLayout()
                expand_row.addWidget(QLabel("Expand input text:"))
                self.btn_case = QPushButton("Case Variants")
                self.btn_qc = QPushButton("?C Pattern")
                self.btn_perms = QPushButton("Permutations")
                self.btn_import = QPushButton("Import Lines…")
                for _b in [self.btn_case, self.btn_qc, self.btn_perms, self.btn_import]:
                    expand_row.addWidget(_b)
                expand_row.addStretch()
                edit_layout.addLayout(expand_row)

                left_layout.addWidget(self.edit_grp, 1)
                splitter.addWidget(left)

                # ─── RIGHT: preview + generate + saved list ───────────────────
                right = QWidget()
                right_layout = QVBoxLayout(right)
                right_layout.setContentsMargins(4, 0, 0, 0)

                self.lbl_count = QLabel("Candidates: 0")
                self.lbl_count.setStyleSheet("font-weight: bold; font-size: 14px;")
                right_layout.addWidget(self.lbl_count)

                right_layout.addWidget(QLabel("Preview (first 30 candidates):"))
                self.preview_list = QListWidget()
                self.preview_list.setSelectionMode(
                    QAbstractItemView.SelectionMode.NoSelection
                )
                right_layout.addWidget(self.preview_list, 1)

                self.btn_generate = QPushButton("⬇  Generate & Save to Workspace")
                self.btn_generate.setStyleSheet(
                    "font-weight: bold; padding: 7px; font-size: 13px;"
                )
                right_layout.addWidget(self.btn_generate)

                # ── separator ──
                sep = QFrame()
                sep.setFrameShape(QFrame.Shape.HLine)
                sep.setFrameShadow(QFrame.Shadow.Sunken)
                right_layout.addWidget(sep)

                saved_hdr = QHBoxLayout()
                saved_hdr.addWidget(QLabel("<b>Saved Workspace Wordlists</b>"))
                saved_hdr.addStretch()
                self.btn_refresh_saved = QPushButton("Refresh")
                self.btn_open_wl_folder = QPushButton("Open Folder")
                saved_hdr.addWidget(self.btn_refresh_saved)
                saved_hdr.addWidget(self.btn_open_wl_folder)
                right_layout.addLayout(saved_hdr)

                self.saved_list = QListWidget()
                self.saved_list.setMinimumHeight(100)
                self.saved_list.setMaximumHeight(180)
                right_layout.addWidget(self.saved_list)

                saved_btn_row = QHBoxLayout()
                self.btn_del_wl = QPushButton("Delete Selected")
                self.btn_clear_segments = QPushButton("Clear All Segments")
                saved_btn_row.addWidget(self.btn_del_wl)
                saved_btn_row.addStretch()
                saved_btn_row.addWidget(self.btn_clear_segments)
                right_layout.addLayout(saved_btn_row)

                splitter.addWidget(right)
                splitter.setSizes([480, 340])
                main_layout.addWidget(splitter, 1)

                # ── signals ───────────────────────────────────────────────────
                self.seg_list.currentRowChanged.connect(self._on_seg_selected)
                self.btn_seg_add.clicked.connect(self._add_segment)
                self.btn_seg_del.clicked.connect(self._del_segment)
                self.btn_seg_up.clicked.connect(lambda: self._move_seg(-1))
                self.btn_seg_dn.clicked.connect(lambda: self._move_seg(1))

                self.btn_var_add.clicked.connect(self._add_variant)
                self.btn_var_del.clicked.connect(self._del_variant)
                self.btn_var_up.clicked.connect(lambda: self._move_var(-1))
                self.btn_var_dn.clicked.connect(lambda: self._move_var(1))
                self.txt_variant.returnPressed.connect(self._add_variant)

                self.btn_case.clicked.connect(self._expand_case)
                self.btn_qc.clicked.connect(self._expand_qc)
                self.btn_perms.clicked.connect(self._expand_perms)
                self.btn_import.clicked.connect(self._import_multiline)

                self.btn_generate.clicked.connect(self._generate_and_save)
                self.btn_refresh_saved.clicked.connect(self._refresh_list)
                self.btn_open_wl_folder.clicked.connect(self._open_wl_folder)
                self.btn_del_wl.clicked.connect(self._del_wordlist)
                self.btn_clear_segments.clicked.connect(self._clear_all_segments)

                self._update_preview()
                self._refresh_list()

            # ------------------------------------------------------------------
            # Helpers
            # ------------------------------------------------------------------

            def _workspace(self):
                from portable_crypt_recovery.app.app_state import get_app_state
                state = get_app_state()
                return state.workspace_root if state.is_workspace_open() else None

            # ------------------------------------------------------------------
            # Segment operations
            # ------------------------------------------------------------------

            def _rebuild_seg_list(self) -> None:
                from PySide6.QtWidgets import QListWidgetItem
                cur = self.seg_list.currentRow()
                self.seg_list.clear()
                for i, seg in enumerate(self._segments):
                    n = len(seg)
                    if n == 0:
                        summary = "(no variants)"
                    elif n <= 5:
                        summary = ", ".join(f'"{v}"' for v in seg)
                    else:
                        summary = ", ".join(f'"{v}"' for v in seg[:4]) + f", … ({n} total)"
                    self.seg_list.addItem(QListWidgetItem(f"Seg {i+1}:  {summary}"))
                count = self.seg_list.count()
                if count > 0:
                    new_row = min(cur, count - 1) if cur >= 0 else 0
                    self.seg_list.setCurrentRow(new_row)
                self._update_edit_title()
                self._update_preview()

            def _add_segment(self) -> None:
                self._segments.append([])
                self._rebuild_seg_list()
                self.seg_list.setCurrentRow(len(self._segments) - 1)

            def _del_segment(self) -> None:
                row = self.seg_list.currentRow()
                if 0 <= row < len(self._segments):
                    self._segments.pop(row)
                    self._rebuild_seg_list()

            def _move_seg(self, direction: int) -> None:
                row = self.seg_list.currentRow()
                new_row = row + direction
                n = len(self._segments)
                if 0 <= row < n and 0 <= new_row < n:
                    self._segments[row], self._segments[new_row] = (
                        self._segments[new_row], self._segments[row]
                    )
                    self._rebuild_seg_list()
                    self.seg_list.setCurrentRow(new_row)

            def _on_seg_selected(self, row: int) -> None:
                self._rebuild_var_list(row)
                self._update_edit_title()

            def _update_edit_title(self) -> None:
                row = self.seg_list.currentRow()
                if row < 0 or not self._segments:
                    self.edit_grp.setTitle("Edit Segment  (add a segment above)")
                else:
                    self.edit_grp.setTitle(f"Edit Segment {row + 1}")

            def _clear_all_segments(self) -> None:
                from PySide6.QtWidgets import QMessageBox
                if not self._segments:
                    return
                reply = QMessageBox.question(
                    self, "Clear All",
                    "Remove all segments and their variants?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No,
                )
                if reply == QMessageBox.StandardButton.Yes:
                    self._segments.clear()
                    self._rebuild_seg_list()
                    self.var_list.clear()

            # ------------------------------------------------------------------
            # Variant operations
            # ------------------------------------------------------------------

            def _si(self) -> int:
                """Current segment index."""
                return self.seg_list.currentRow()

            def _rebuild_var_list(self, seg_row: int | None = None) -> None:
                from PySide6.QtWidgets import QListWidgetItem
                if seg_row is None:
                    seg_row = self._si()
                self.var_list.clear()
                if 0 <= seg_row < len(self._segments):
                    for v in self._segments[seg_row]:
                        self.var_list.addItem(QListWidgetItem(v))
                self._update_preview()

            def _add_variants_to_seg(self, variants: list[str]) -> None:
                from PySide6.QtWidgets import QMessageBox
                si = self._si()
                if si < 0 or si >= len(self._segments):
                    QMessageBox.information(
                        self, "No Segment", "Select or add a segment first."
                    )
                    return
                existing = set(self._segments[si])
                added = 0
                for v in variants:
                    if v and v not in existing:
                        self._segments[si].append(v)
                        existing.add(v)
                        added += 1
                self._rebuild_var_list()
                self._rebuild_seg_list()

            def _add_variant(self) -> None:
                text = self.txt_variant.text().strip()
                if not text:
                    return
                self._add_variants_to_seg([text])
                self.txt_variant.clear()

            def _del_variant(self) -> None:
                si = self._si()
                vi = self.var_list.currentRow()
                if 0 <= si < len(self._segments) and 0 <= vi < len(self._segments[si]):
                    self._segments[si].pop(vi)
                    self._rebuild_var_list()
                    self._rebuild_seg_list()

            def _move_var(self, direction: int) -> None:
                si = self._si()
                vi = self.var_list.currentRow()
                new_vi = vi + direction
                seg = self._segments[si] if 0 <= si < len(self._segments) else None
                if seg and 0 <= vi < len(seg) and 0 <= new_vi < len(seg):
                    seg[vi], seg[new_vi] = seg[new_vi], seg[vi]
                    self._rebuild_var_list()
                    self.var_list.setCurrentRow(new_vi)

            # ------------------------------------------------------------------
            # Expand operations (operate on txt_variant input)
            # ------------------------------------------------------------------

            def _expand_case(self) -> None:
                from PySide6.QtWidgets import QMessageBox

                from portable_crypt_recovery.services.builders.password_builder import (
                    case_variants,
                )
                text = self.txt_variant.text().strip()
                if not text:
                    QMessageBox.information(
                        self, "Case Variants",
                        "Type a word in the input box, then click Case Variants.\n"
                        "All upper/lower combinations are added as variants.\n"
                        "Example: 'dog' → dog, Dog, dOg, doG, DOg, DoG, dOG, DOG"
                    )
                    return
                variants = case_variants(text)
                self._add_variants_to_seg(variants)
                self.txt_variant.clear()

            def _expand_qc(self) -> None:
                from PySide6.QtWidgets import QMessageBox

                from portable_crypt_recovery.services.builders.password_builder import (
                    expand_pattern_tokens,
                )
                text = self.txt_variant.text().strip()
                if not text:
                    QMessageBox.information(
                        self, "?C Pattern Expansion",
                        "Type a pattern containing ?C in the input box.\n\n"
                        "?C is replaced by every letter a–z and A–Z (52 variants each).\n"
                        "Multiple ?C tokens multiply the result.\n\n"
                        "Examples:\n"
                        "  pa?Cs  →  paas, pabs, …, paZs  (52 variants)\n"
                        "  ?C?C   →  aa, ab, …, ZZ  (2 704 variants)"
                    )
                    return
                if "?C" not in text:
                    QMessageBox.information(
                        self, "?C Pattern",
                        f"'{text}' has no ?C token.  Add ?C where you want a letter wildcard."
                    )
                    return
                variants = expand_pattern_tokens(text)
                if len(variants) > 500:
                    reply = QMessageBox.question(
                        self, "?C Pattern",
                        f"This will add {len(variants):,} variants.  Continue?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                        QMessageBox.StandardButton.No,
                    )
                    if reply != QMessageBox.StandardButton.Yes:
                        return
                self._add_variants_to_seg(variants)
                self.txt_variant.clear()

            def _expand_perms(self) -> None:
                from PySide6.QtWidgets import QMessageBox

                from portable_crypt_recovery.services.builders.password_builder import (
                    permutation_variants,
                )
                text = self.txt_variant.text().strip()
                if not text:
                    QMessageBox.information(
                        self, "Permutations",
                        "Type a short string, then click Permutations.\n"
                        "All unique character orderings are added as variants.\n"
                        "Example: 'abc' → abc, acb, bac, bca, cab, cba"
                    )
                    return
                variants = permutation_variants(text)
                if len(variants) > 1000:
                    reply = QMessageBox.question(
                        self, "Permutations",
                        f"'{text}' produces {len(variants):,} permutations.  Continue?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                        QMessageBox.StandardButton.No,
                    )
                    if reply != QMessageBox.StandardButton.Yes:
                        return
                self._add_variants_to_seg(variants)
                self.txt_variant.clear()

            def _import_multiline(self) -> None:
                from PySide6.QtWidgets import (
                    QDialog,
                    QDialogButtonBox,
                    QLabel,
                    QPlainTextEdit,
                    QVBoxLayout,
                )
                dlg = QDialog(self)
                dlg.setWindowTitle("Import Variants from Text")
                dlg.resize(420, 320)
                lay = QVBoxLayout(dlg)
                lay.addWidget(QLabel(
                    "Paste variants — one per line.  Blank lines are ignored."
                ))
                txt = QPlainTextEdit()
                txt.setPlaceholderText("dog\nDog\nDOG\n123\n...")
                lay.addWidget(txt, 1)
                btns = QDialogButtonBox(
                    QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
                )
                btns.accepted.connect(dlg.accept)
                btns.rejected.connect(dlg.reject)
                lay.addWidget(btns)
                if dlg.exec() == 1:
                    lines = [
                        line.strip()
                        for line in txt.toPlainText().splitlines()
                        if line.strip()
                    ]
                    if lines:
                        self._add_variants_to_seg(lines)

            # ------------------------------------------------------------------
            # Live preview
            # ------------------------------------------------------------------

            def _update_preview(self) -> None:
                from portable_crypt_recovery.services.builders.password_builder import (
                    combine_segments,
                    count_candidates,
                )
                self.preview_list.clear()
                active = [s for s in self._segments if s]
                if not active:
                    self.lbl_count.setText("Candidates: 0")
                    self.lbl_count.setStyleSheet(
                        "font-weight: bold; font-size: 14px; color: gray;"
                    )
                    self.preview_list.addItem("(add segments and variants to see a preview)")
                    return

                upper = count_candidates(active)

                if upper > 10_000_000:
                    self.lbl_count.setText(f"Candidates: ~{upper:,}  ⛔ exceeds 10 M hard limit")
                    self.lbl_count.setStyleSheet(
                        "font-weight: bold; font-size: 14px; color: #cc3333;"
                    )
                    self.preview_list.addItem("(too many to preview — reduce variants)")
                    return

                if upper > 1_000_000:
                    self.lbl_count.setText(
                        f"Candidates: ~{upper:,}  ⚠ requires confirmation to generate"
                    )
                    self.lbl_count.setStyleSheet(
                        "font-weight: bold; font-size: 14px; color: #cc5500;"
                    )
                    self.preview_list.addItem("(preview skipped for very large lists)")
                    return

                candidates = combine_segments(active)
                real = len(candidates)
                if real > 100_000:
                    self.lbl_count.setText(f"Candidates: {real:,}  ⚠ large list (warning)")
                    self.lbl_count.setStyleSheet(
                        "font-weight: bold; font-size: 14px; color: #cc8800;"
                    )
                else:
                    self.lbl_count.setText(f"Candidates: {real:,}")
                    self.lbl_count.setStyleSheet(
                        "font-weight: bold; font-size: 14px; color: #22aa44;"
                    )

                for pw in candidates[:30]:
                    self.preview_list.addItem(pw)
                if real > 30:
                    self.preview_list.addItem(f"  … and {real - 30:,} more")

            # ------------------------------------------------------------------
            # Generate & Save
            # ------------------------------------------------------------------

            def _generate_and_save(self) -> None:
                from PySide6.QtWidgets import QMessageBox

                ws = self._workspace()
                if ws is None:
                    QMessageBox.warning(self, "No Workspace", "Open a workspace first.")
                    return

                active = [s for s in self._segments if s]
                if not active:
                    QMessageBox.warning(
                        self, "Nothing to Generate",
                        "Add at least one segment with variants."
                    )
                    return

                try:
                    from portable_crypt_recovery.services.builders.password_builder import (
                        PasswordLimitBlocked,
                        PasswordLimitConfirmRequired,
                        build_generated_password_source,
                    )
                    try:
                        src = build_generated_password_source(active, ws, force=False)
                    except PasswordLimitConfirmRequired as exc:
                        reply = QMessageBox.question(
                            self, "Large Candidate List",
                            str(exc) + "\n\nGenerate anyway?",
                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                            QMessageBox.StandardButton.No,
                        )
                        if reply != QMessageBox.StandardButton.Yes:
                            return
                        src = build_generated_password_source(active, ws, force=True)
                    except PasswordLimitBlocked as exc:
                        QMessageBox.critical(
                            self, "Candidate Limit Exceeded",
                            str(exc) + "\n\nReduce the number of candidates to continue."
                        )
                        return

                    QMessageBox.information(
                        self, "Wordlist Saved",
                        f"{src.candidate_count:,} candidates saved to workspace.\n"
                        f"File: {src.workspace_relative_path}\n\n"
                        "Select it in the Jobs view under Password Source → "
                        "Workspace wordlist."
                    )
                    self._refresh_list()

                except Exception as exc:
                    QMessageBox.critical(self, "Generation Failed", str(exc))

            # ------------------------------------------------------------------
            # Saved wordlists  (named _refresh_list for main_window auto-refresh)
            # ------------------------------------------------------------------

            def _refresh_list(self) -> None:
                from PySide6.QtWidgets import QListWidgetItem
                self.saved_list.clear()
                ws = self._workspace()
                if ws is None:
                    self.saved_list.addItem(QListWidgetItem("(no workspace open)"))
                    return
                wl_dir = ws / "generated" / "wordlists"
                if not wl_dir.exists():
                    self.saved_list.addItem(QListWidgetItem("(no wordlists saved yet)"))
                    return
                txt_files = sorted(wl_dir.glob("*.txt"))
                if not txt_files:
                    self.saved_list.addItem(QListWidgetItem("(no wordlists saved yet)"))
                    return
                for p in txt_files:
                    try:
                        count = sum(1 for _ in p.open("r", encoding="utf-8", errors="replace"))
                    except OSError:
                        count = 0
                    item = QListWidgetItem(f"{p.name}  —  {count:,} lines")
                    item.setData(256, str(p))
                    self.saved_list.addItem(item)

            def _open_wl_folder(self) -> None:
                import os
                import subprocess
                import sys
                ws = self._workspace()
                if ws is None:
                    return
                folder = ws / "generated" / "wordlists"
                folder.mkdir(parents=True, exist_ok=True)
                if sys.platform == "win32":
                    os.startfile(str(folder))
                else:
                    subprocess.Popen(["xdg-open", str(folder)])

            def _del_wordlist(self) -> None:
                from pathlib import Path  # noqa: PLC0415

                from PySide6.QtWidgets import QMessageBox
                item = self.saved_list.currentItem()
                if not item or item.data(256) is None:
                    QMessageBox.information(self, "Delete", "Select a wordlist to delete.")
                    return
                path_str = item.data(256)
                reply = QMessageBox.question(
                    self, "Delete Wordlist",
                    f"Permanently delete:\n{path_str}",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No,
                )
                if reply == QMessageBox.StandardButton.Yes:
                    try:
                        Path(path_str).unlink(missing_ok=True)
                        self._refresh_list()
                    except Exception as exc:
                        QMessageBox.critical(self, "Delete Failed", str(exc))

        return _PasswordBuilderView()
