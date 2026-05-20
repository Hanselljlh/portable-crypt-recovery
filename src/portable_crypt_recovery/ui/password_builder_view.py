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
                main_layout.setSpacing(4)
                main_layout.setContentsMargins(6, 6, 6, 6)

                # ── top toolbar ──────────────────────────────────────────────
                top_bar = QHBoxLayout()
                lbl_title = QLabel("<b>Password Builder</b>")
                lbl_hint = QLabel(
                    "Build ordered segments, expand variants, then generate a named wordlist."
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
                left_layout.setSpacing(4)

                # Segment list
                seg_grp = QGroupBox(
                    "Segments  (ordered — one value per segment joins to form a password)"
                )
                seg_grp_layout = QVBoxLayout(seg_grp)
                seg_grp_layout.setSpacing(3)

                seg_toolbar = QHBoxLayout()
                seg_toolbar.setSpacing(3)
                self.btn_seg_add = QPushButton("+ Add")
                self.btn_seg_del = QPushButton("Remove")
                self.btn_seg_clear = QPushButton("Clear All")
                self.btn_seg_up = QPushButton("↑")
                self.btn_seg_dn = QPushButton("↓")
                self.btn_seg_up.setFixedWidth(28)
                self.btn_seg_dn.setFixedWidth(28)
                self.btn_seg_add.setFixedHeight(24)
                self.btn_seg_del.setFixedHeight(24)
                self.btn_seg_clear.setFixedHeight(24)
                self.btn_seg_up.setFixedHeight(24)
                self.btn_seg_dn.setFixedHeight(24)
                for _b in [
                    self.btn_seg_add, self.btn_seg_del, self.btn_seg_clear,
                    self.btn_seg_up, self.btn_seg_dn,
                ]:
                    seg_toolbar.addWidget(_b)
                seg_toolbar.addStretch()
                seg_grp_layout.addLayout(seg_toolbar)

                self.seg_list = QListWidget()
                self.seg_list.setSelectionMode(
                    QAbstractItemView.SelectionMode.ExtendedSelection
                )
                self.seg_list.setSpacing(0)
                self.seg_list.setUniformItemSizes(True)
                self.seg_list.setMinimumHeight(70)
                self.seg_list.setMaximumHeight(120)
                seg_grp_layout.addWidget(self.seg_list)

                left_layout.addWidget(seg_grp)

                # Variant editor
                self.edit_grp = QGroupBox("Edit Segment  (select a segment above)")
                edit_layout = QVBoxLayout(self.edit_grp)
                edit_layout.setSpacing(3)

                var_toolbar = QHBoxLayout()
                var_toolbar.setSpacing(3)
                var_toolbar.addWidget(QLabel("Variants:"))
                var_toolbar.addStretch()
                self.btn_var_del = QPushButton("Remove")
                self.btn_var_clear = QPushButton("Clear All")
                self.btn_var_up = QPushButton("↑")
                self.btn_var_dn = QPushButton("↓")
                self.btn_var_up.setFixedWidth(28)
                self.btn_var_dn.setFixedWidth(28)
                self.btn_var_del.setFixedHeight(24)
                self.btn_var_clear.setFixedHeight(24)
                self.btn_var_up.setFixedHeight(24)
                self.btn_var_dn.setFixedHeight(24)
                for _b in [self.btn_var_del, self.btn_var_clear, self.btn_var_up, self.btn_var_dn]:
                    var_toolbar.addWidget(_b)
                edit_layout.addLayout(var_toolbar)

                self.var_list = QListWidget()
                self.var_list.setSelectionMode(
                    QAbstractItemView.SelectionMode.ExtendedSelection
                )
                self.var_list.setSpacing(0)
                self.var_list.setUniformItemSizes(True)
                self.var_list.setMinimumHeight(100)
                edit_layout.addWidget(self.var_list, 1)

                add_row = QHBoxLayout()
                add_row.setSpacing(3)
                self.txt_variant = QLineEdit()
                self.txt_variant.setPlaceholderText(
                    "Type a value — then click Add or an expand button"
                )
                self.btn_var_add = QPushButton("Add")
                self.btn_var_add.setFixedHeight(24)
                add_row.addWidget(self.txt_variant, 1)
                add_row.addWidget(self.btn_var_add)
                edit_layout.addLayout(add_row)

                # Expand row 1 — character transforms
                exp1_row = QHBoxLayout()
                exp1_row.setSpacing(3)
                exp1_row.addWidget(QLabel("Transform:"))
                self.btn_case = QPushButton("Case Variants")
                self.btn_leet = QPushButton("Leet Speak")
                self.btn_reverse = QPushButton("Reverse")
                self.btn_qc = QPushButton("?C Pattern")
                self.btn_perms = QPushButton("Permutations")
                for _b in [
                    self.btn_case, self.btn_leet, self.btn_reverse,
                    self.btn_qc, self.btn_perms,
                ]:
                    _b.setFixedHeight(24)
                    exp1_row.addWidget(_b)
                exp1_row.addStretch()
                edit_layout.addLayout(exp1_row)

                # Expand row 2 — suffix/prefix generators
                exp2_row = QHBoxLayout()
                exp2_row.setSpacing(3)
                exp2_row.addWidget(QLabel("Append:"))
                self.btn_numbers = QPushButton("Numbers…")
                self.btn_years = QPushButton("Years…")
                self.btn_special = QPushButton("Special Chars…")
                self.btn_import = QPushButton("Import Lines…")
                for _b in [
                    self.btn_numbers, self.btn_years,
                    self.btn_special, self.btn_import,
                ]:
                    _b.setFixedHeight(24)
                    exp2_row.addWidget(_b)
                exp2_row.addStretch()
                edit_layout.addLayout(exp2_row)

                left_layout.addWidget(self.edit_grp, 1)
                splitter.addWidget(left)

                # ─── RIGHT: preview + generate + saved list ───────────────────
                right = QWidget()
                right_layout = QVBoxLayout(right)
                right_layout.setContentsMargins(4, 0, 0, 0)
                right_layout.setSpacing(4)

                self.lbl_count = QLabel("Candidates: 0")
                self.lbl_count.setStyleSheet("font-weight: bold; font-size: 13px;")
                right_layout.addWidget(self.lbl_count)

                right_layout.addWidget(QLabel("Preview (first 30):"))
                self.preview_list = QListWidget()
                self.preview_list.setSelectionMode(
                    QAbstractItemView.SelectionMode.NoSelection
                )
                self.preview_list.setSpacing(0)
                self.preview_list.setUniformItemSizes(True)
                right_layout.addWidget(self.preview_list, 1)

                # Name field + generate button
                name_row = QHBoxLayout()
                name_row.setSpacing(4)
                name_row.addWidget(QLabel("Name:"))
                self.txt_nickname = QLineEdit()
                self.txt_nickname.setPlaceholderText(
                    "Give this wordlist a name (e.g. dog-name-variations)"
                )
                name_row.addWidget(self.txt_nickname, 1)
                right_layout.addLayout(name_row)

                self.btn_generate = QPushButton("⬇  Generate & Save to Workspace")
                self.btn_generate.setStyleSheet(
                    "font-weight: bold; padding: 6px; font-size: 12px;"
                )
                right_layout.addWidget(self.btn_generate)

                # ── separator ──
                sep = QFrame()
                sep.setFrameShape(QFrame.Shape.HLine)
                sep.setFrameShadow(QFrame.Shadow.Sunken)
                right_layout.addWidget(sep)

                saved_hdr = QHBoxLayout()
                saved_hdr.setSpacing(3)
                saved_hdr.addWidget(QLabel("<b>Saved Wordlists</b>"))
                saved_hdr.addStretch()
                self.btn_refresh_saved = QPushButton("Refresh")
                self.btn_open_wl_folder = QPushButton("Open Folder")
                self.btn_refresh_saved.setFixedHeight(24)
                self.btn_open_wl_folder.setFixedHeight(24)
                saved_hdr.addWidget(self.btn_refresh_saved)
                saved_hdr.addWidget(self.btn_open_wl_folder)
                right_layout.addLayout(saved_hdr)

                self.saved_list = QListWidget()
                self.saved_list.setSelectionMode(
                    QAbstractItemView.SelectionMode.ExtendedSelection
                )
                self.saved_list.setSpacing(0)
                self.saved_list.setUniformItemSizes(True)
                self.saved_list.setMinimumHeight(80)
                self.saved_list.setMaximumHeight(160)
                right_layout.addWidget(self.saved_list)

                saved_btn_row = QHBoxLayout()
                saved_btn_row.setSpacing(3)
                self.btn_del_wl = QPushButton("Delete Selected")
                self.btn_rename_wl = QPushButton("Rename…")
                self.btn_clear_segments = QPushButton("Clear All Segments")
                self.btn_del_wl.setFixedHeight(24)
                self.btn_rename_wl.setFixedHeight(24)
                self.btn_clear_segments.setFixedHeight(24)
                saved_btn_row.addWidget(self.btn_del_wl)
                saved_btn_row.addWidget(self.btn_rename_wl)
                saved_btn_row.addStretch()
                saved_btn_row.addWidget(self.btn_clear_segments)
                right_layout.addLayout(saved_btn_row)

                splitter.addWidget(right)
                splitter.setSizes([500, 340])
                main_layout.addWidget(splitter, 1)

                # ── signals ───────────────────────────────────────────────────
                self.seg_list.currentRowChanged.connect(self._on_seg_selected)
                self.btn_seg_add.clicked.connect(self._add_segment)
                self.btn_seg_del.clicked.connect(self._del_segment)
                self.btn_seg_clear.clicked.connect(self._clear_all_segments)
                self.btn_seg_up.clicked.connect(lambda: self._move_seg(-1))
                self.btn_seg_dn.clicked.connect(lambda: self._move_seg(1))

                self.btn_var_add.clicked.connect(self._add_variant)
                self.btn_var_del.clicked.connect(self._del_variant)
                self.btn_var_clear.clicked.connect(self._clear_all_variants)
                self.btn_var_up.clicked.connect(lambda: self._move_var(-1))
                self.btn_var_dn.clicked.connect(lambda: self._move_var(1))
                self.txt_variant.returnPressed.connect(self._add_variant)

                # Expand row 1
                self.btn_case.clicked.connect(self._expand_case)
                self.btn_leet.clicked.connect(self._expand_leet)
                self.btn_reverse.clicked.connect(self._expand_reverse)
                self.btn_qc.clicked.connect(self._expand_qc)
                self.btn_perms.clicked.connect(self._expand_perms)

                # Expand row 2
                self.btn_numbers.clicked.connect(self._expand_numbers)
                self.btn_years.clicked.connect(self._expand_years)
                self.btn_special.clicked.connect(self._expand_special)
                self.btn_import.clicked.connect(self._import_multiline)

                self.btn_generate.clicked.connect(self._generate_and_save)
                self.btn_refresh_saved.clicked.connect(self._refresh_list)
                self.btn_open_wl_folder.clicked.connect(self._open_wl_folder)
                self.btn_del_wl.clicked.connect(self._del_wordlist)
                self.btn_rename_wl.clicked.connect(self._rename_wordlist)
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

            def _selected_rows(self, widget) -> list[int]:
                """Return sorted list of selected row indices for a QListWidget."""
                return sorted(set(widget.row(item) for item in widget.selectedItems()))

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
                    elif n <= 4:
                        summary = ", ".join(f'"{v}"' for v in seg)
                    else:
                        summary = ", ".join(f'"{v}"' for v in seg[:3]) + f", … ({n} total)"
                    self.seg_list.addItem(QListWidgetItem(f"Seg {i+1}: {summary}"))
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
                rows = self._selected_rows(self.seg_list)
                if not rows:
                    return
                for row in sorted(rows, reverse=True):
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
                    n = len(self._segments[row])
                    self.edit_grp.setTitle(
                        f"Edit Segment {row + 1}  ({n} variant{'s' if n != 1 else ''})"
                    )

            def _clear_all_segments(self) -> None:
                from PySide6.QtWidgets import QMessageBox
                if not self._segments:
                    return
                reply = QMessageBox.question(
                    self, "Clear All Segments",
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
                if si < 0 or si >= len(self._segments):
                    return
                rows = self._selected_rows(self.var_list)
                if not rows:
                    return
                for vi in sorted(rows, reverse=True):
                    if 0 <= vi < len(self._segments[si]):
                        self._segments[si].pop(vi)
                self._rebuild_var_list()
                self._rebuild_seg_list()

            def _clear_all_variants(self) -> None:
                si = self._si()
                if si < 0 or si >= len(self._segments):
                    return
                if not self._segments[si]:
                    return
                from PySide6.QtWidgets import QMessageBox
                reply = QMessageBox.question(
                    self, "Clear Variants",
                    f"Remove all {len(self._segments[si])} variants from Segment {si + 1}?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No,
                )
                if reply == QMessageBox.StandardButton.Yes:
                    self._segments[si].clear()
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
            # Expand row 1 — character transforms
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
                        "Type a word in the input, then click Case Variants.\n"
                        "Every upper/lower combination is added as a variant.\n\n"
                        "Example: 'dog' → dog, Dog, dOg, doG, DOg, DoG, dOG, DOG"
                    )
                    return
                variants = case_variants(text)
                self._add_variants_to_seg(variants)
                self.txt_variant.clear()

            def _expand_leet(self) -> None:
                from PySide6.QtWidgets import QMessageBox

                from portable_crypt_recovery.services.builders.password_builder import (
                    leet_variants,
                )
                text = self.txt_variant.text().strip()
                if not text:
                    QMessageBox.information(
                        self, "Leet Speak",
                        "Type a word in the input, then click Leet Speak.\n"
                        "Every combination of original/substituted characters is added.\n\n"
                        "Substitutions:  a→@  e→3  i→1  o→0  s→$  t→7  l→1  g→9\n\n"
                        "Example: 'pass' → pass, p@ss, pa$$, pa$s, p@$$, ..."
                    )
                    return
                variants = leet_variants(text)
                self._add_variants_to_seg(variants)
                self.txt_variant.clear()

            def _expand_reverse(self) -> None:
                from portable_crypt_recovery.services.builders.password_builder import (
                    reverse_variant,
                )
                text = self.txt_variant.text().strip()
                if not text:
                    return
                variants = reverse_variant(text)
                self._add_variants_to_seg(variants)
                self.txt_variant.clear()

            def _expand_qc(self) -> None:
                from PySide6.QtWidgets import QMessageBox

                from portable_crypt_recovery.services.builders.password_builder import (
                    estimate_qc_expansion_count,
                    expand_pattern_tokens,
                )
                text = self.txt_variant.text().strip()
                if not text:
                    QMessageBox.information(
                        self, "?C Pattern Expansion",
                        "Type a pattern with ?C in the input.\n\n"
                        "?C is replaced by every letter a–z and A–Z (52 each).\n"
                        "Multiple ?C tokens multiply the result.\n\n"
                        "Examples:\n"
                        "  pa?Cs  →  paas … paZs  (52 variants)\n"
                        "  ?C?C   →  aa … ZZ  (2,704 variants)"
                    )
                    return
                if "?C" not in text:
                    QMessageBox.information(
                        self, "?C Pattern",
                        f"'{text}' has no ?C token.\n"
                        "Add ?C where you want a letter wildcard."
                    )
                    return
                estimated = estimate_qc_expansion_count(text)
                if estimated > 10_000_000:
                    QMessageBox.warning(
                        self, "?C Pattern — Too Large",
                        f"This pattern would generate {estimated:,} variants, which exceeds "
                        "the 10 M hard limit.\nUse 4 or fewer ?C tokens."
                    )
                    return
                if estimated > 500:
                    reply = QMessageBox.question(
                        self, "?C Pattern",
                        f"This will add {estimated:,} variants.  Continue?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                        QMessageBox.StandardButton.No,
                    )
                    if reply != QMessageBox.StandardButton.Yes:
                        return
                variants = expand_pattern_tokens(text)
                self._add_variants_to_seg(variants)
                self.txt_variant.clear()

            def _expand_perms(self) -> None:
                from PySide6.QtWidgets import QMessageBox

                from portable_crypt_recovery.services.builders.password_builder import (
                    estimate_permutation_count,
                    permutation_variants,
                )
                text = self.txt_variant.text().strip()
                if not text:
                    QMessageBox.information(
                        self, "Permutations",
                        "Type a short string, then click Permutations.\n"
                        "All unique character orderings are added as variants.\n\n"
                        "Example: 'abc' → abc, acb, bac, bca, cab, cba"
                    )
                    return
                estimated = estimate_permutation_count(text)
                if estimated > 10_000_000:
                    QMessageBox.warning(
                        self, "Permutations — Too Large",
                        f"'{text}' ({len(text)} chars) has up to {estimated:,} permutations, "
                        "which exceeds the 10 M hard limit.\nUse a string of 9 or fewer characters."
                    )
                    return
                if estimated > 1000:
                    reply = QMessageBox.question(
                        self, "Permutations",
                        f"'{text}' produces up to {estimated:,} permutations.  Continue?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                        QMessageBox.StandardButton.No,
                    )
                    if reply != QMessageBox.StandardButton.Yes:
                        return
                variants = permutation_variants(text)
                self._add_variants_to_seg(variants)
                self.txt_variant.clear()

            # ------------------------------------------------------------------
            # Expand row 2 — suffix/prefix generators
            # ------------------------------------------------------------------

            def _expand_numbers(self) -> None:
                from PySide6.QtWidgets import (
                    QCheckBox,
                    QDialog,
                    QDialogButtonBox,
                    QFormLayout,
                    QLabel,
                    QSpinBox,
                    QVBoxLayout,
                )

                from portable_crypt_recovery.services.builders.password_builder import (
                    number_suffix_variants,
                )
                text = self.txt_variant.text().strip()

                dlg = QDialog(self)
                dlg.setWindowTitle("Number Suffix / Prefix")
                dlg.resize(320, 210)
                lay = QVBoxLayout(dlg)
                lay.addWidget(QLabel(
                    "Append or prepend a range of numbers to:\n"
                    f"  \"{text}\"  (empty = use each variant in current segment)"
                    if text else
                    "Append or prepend numbers to each variant in the active segment."
                ))
                form = QFormLayout()
                sb_start = QSpinBox()
                sb_start.setRange(0, 99999)
                sb_start.setValue(1)
                sb_stop = QSpinBox()
                sb_stop.setRange(0, 99999)
                sb_stop.setValue(9)
                sb_pad = QSpinBox()
                sb_pad.setRange(0, 6)
                sb_pad.setValue(0)
                sb_pad.setToolTip("0 = no padding. 2 = '01','02'…'09'")
                chk_prefix = QCheckBox("Prepend (put number before word)")
                form.addRow("From:", sb_start)
                form.addRow("To:", sb_stop)
                form.addRow("Zero-pad width:", sb_pad)
                form.addRow("", chk_prefix)
                lay.addLayout(form)
                btns = QDialogButtonBox(
                    QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
                )
                btns.accepted.connect(dlg.accept)
                btns.rejected.connect(dlg.reject)
                lay.addWidget(btns)
                if dlg.exec() != 1:
                    return

                start = sb_start.value()
                stop = sb_stop.value()
                if stop < start:
                    start, stop = stop, start
                pad = sb_pad.value()
                prefix = chk_prefix.isChecked()

                if text:
                    variants = number_suffix_variants(text, start, stop, pad, prefix)
                    self._add_variants_to_seg(variants)
                    self.txt_variant.clear()
                else:
                    si = self._si()
                    if si < 0 or si >= len(self._segments) or not self._segments[si]:
                        from PySide6.QtWidgets import QMessageBox
                        QMessageBox.information(
                            self, "No Variants",
                            "Type a word in the input, or add variants to the segment first."
                        )
                        return
                    new_variants: list[str] = []
                    for v in list(self._segments[si]):
                        new_variants.extend(number_suffix_variants(v, start, stop, pad, prefix))
                    self._add_variants_to_seg(new_variants)

            def _expand_years(self) -> None:
                from PySide6.QtWidgets import (
                    QCheckBox,
                    QDialog,
                    QDialogButtonBox,
                    QFormLayout,
                    QLabel,
                    QSpinBox,
                    QVBoxLayout,
                )

                from portable_crypt_recovery.services.builders.password_builder import (
                    year_suffix_variants,
                )
                text = self.txt_variant.text().strip()

                dlg = QDialog(self)
                dlg.setWindowTitle("Year Suffix / Prefix")
                dlg.resize(300, 170)
                lay = QVBoxLayout(dlg)
                lay.addWidget(QLabel("Append or prepend years to the input word or segment variants."))
                form = QFormLayout()
                sb_start = QSpinBox()
                sb_start.setRange(1900, 2100)
                sb_start.setValue(1990)
                sb_stop = QSpinBox()
                sb_stop.setRange(1900, 2100)
                sb_stop.setValue(2025)
                chk_prefix = QCheckBox("Prepend (put year before word)")
                form.addRow("From year:", sb_start)
                form.addRow("To year:", sb_stop)
                form.addRow("", chk_prefix)
                lay.addLayout(form)
                btns = QDialogButtonBox(
                    QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
                )
                btns.accepted.connect(dlg.accept)
                btns.rejected.connect(dlg.reject)
                lay.addWidget(btns)
                if dlg.exec() != 1:
                    return

                start = sb_start.value()
                stop = sb_stop.value()
                if stop < start:
                    start, stop = stop, start
                prefix = chk_prefix.isChecked()

                if text:
                    variants = year_suffix_variants(text, start, stop, prefix)
                    self._add_variants_to_seg(variants)
                    self.txt_variant.clear()
                else:
                    si = self._si()
                    if si < 0 or si >= len(self._segments) or not self._segments[si]:
                        from PySide6.QtWidgets import QMessageBox
                        QMessageBox.information(
                            self, "No Variants",
                            "Type a word in the input, or add variants to the segment first."
                        )
                        return
                    new_variants: list[str] = []
                    for v in list(self._segments[si]):
                        new_variants.extend(year_suffix_variants(v, start, stop, prefix))
                    self._add_variants_to_seg(new_variants)

            def _expand_special(self) -> None:
                from PySide6.QtWidgets import (
                    QComboBox,
                    QDialog,
                    QDialogButtonBox,
                    QFormLayout,
                    QLabel,
                    QPlainTextEdit,
                    QVBoxLayout,
                )

                from portable_crypt_recovery.services.builders.password_builder import (
                    special_char_variants,
                )
                text = self.txt_variant.text().strip()

                dlg = QDialog(self)
                dlg.setWindowTitle("Special Character Variants")
                dlg.resize(360, 260)
                lay = QVBoxLayout(dlg)
                lay.addWidget(QLabel(
                    "Enter one suffix/prefix per line.\n"
                    "Each will be appended or prepended to the input word\n"
                    "(or to each existing variant if input is empty)."
                ))
                txt = QPlainTextEdit()
                txt.setPlaceholderText("!\n@\n#\n$\n!!\n123!\n!@#\n...")
                txt.setPlainText("!\n@\n#\n$\n!!\n123!\n!@#\n.\n_\n-")
                txt.setMaximumHeight(130)
                lay.addWidget(txt)
                form = QFormLayout()
                cmb_pos = QComboBox()
                cmb_pos.addItems(["Append (after word)", "Prepend (before word)", "Both"])
                form.addRow("Position:", cmb_pos)
                lay.addLayout(form)
                btns = QDialogButtonBox(
                    QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
                )
                btns.accepted.connect(dlg.accept)
                btns.rejected.connect(dlg.reject)
                lay.addWidget(btns)
                if dlg.exec() != 1:
                    return

                chars = [
                    line for line in txt.toPlainText().splitlines()
                    if line  # keep even if just spaces — user may want them
                ]
                if not chars:
                    return

                pos_map = ["append", "prepend", "both"]
                pos = pos_map[cmb_pos.currentIndex()]

                if text:
                    variants = special_char_variants(text, chars, pos)
                    self._add_variants_to_seg(variants)
                    self.txt_variant.clear()
                else:
                    si = self._si()
                    if si < 0 or si >= len(self._segments) or not self._segments[si]:
                        from PySide6.QtWidgets import QMessageBox
                        QMessageBox.information(
                            self, "No Variants",
                            "Type a word in the input, or add variants to the segment first."
                        )
                        return
                    new_variants: list[str] = []
                    for v in list(self._segments[si]):
                        new_variants.extend(special_char_variants(v, chars, pos))
                    self._add_variants_to_seg(new_variants)

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
                dlg.resize(420, 300)
                lay = QVBoxLayout(dlg)
                lay.addWidget(QLabel("Paste variants — one per line.  Blank lines are ignored."))
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
                    self.lbl_count.setStyleSheet("font-weight: bold; font-size: 13px; color: gray;")
                    self.preview_list.addItem("(add segments and variants to see a preview)")
                    return

                upper = count_candidates(active)

                if upper > 10_000_000:
                    self.lbl_count.setText(f"Candidates: ~{upper:,}  ⛔ exceeds 10 M hard limit")
                    self.lbl_count.setStyleSheet(
                        "font-weight: bold; font-size: 13px; color: #cc3333;"
                    )
                    self.preview_list.addItem("(too many to preview — reduce variants)")
                    return

                if upper > 1_000_000:
                    self.lbl_count.setText(
                        f"Candidates: ~{upper:,}  ⚠ requires confirmation to generate"
                    )
                    self.lbl_count.setStyleSheet(
                        "font-weight: bold; font-size: 13px; color: #cc5500;"
                    )
                    self.preview_list.addItem("(preview skipped for very large lists)")
                    return

                candidates = combine_segments(active)
                real = len(candidates)
                if real > 100_000:
                    self.lbl_count.setText(f"Candidates: {real:,}  ⚠ large list")
                    self.lbl_count.setStyleSheet(
                        "font-weight: bold; font-size: 13px; color: #cc8800;"
                    )
                else:
                    self.lbl_count.setText(f"Candidates: {real:,}")
                    self.lbl_count.setStyleSheet(
                        "font-weight: bold; font-size: 13px; color: #22aa44;"
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

                nickname = self.txt_nickname.text().strip()

                try:
                    from portable_crypt_recovery.services.builders.password_builder import (
                        PasswordLimitBlocked,
                        PasswordLimitConfirmRequired,
                        build_generated_password_source,
                    )
                    try:
                        src = build_generated_password_source(
                            active, ws, force=False, nickname=nickname
                        )
                    except PasswordLimitConfirmRequired as exc:
                        reply = QMessageBox.question(
                            self, "Large Candidate List",
                            str(exc) + "\n\nGenerate anyway?",
                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                            QMessageBox.StandardButton.No,
                        )
                        if reply != QMessageBox.StandardButton.Yes:
                            return
                        src = build_generated_password_source(
                            active, ws, force=True, nickname=nickname
                        )
                    except PasswordLimitBlocked as exc:
                        QMessageBox.critical(
                            self, "Candidate Limit Exceeded",
                            str(exc) + "\n\nReduce the number of candidates to continue."
                        )
                        return

                    display = f'"{nickname}"' if nickname else src.workspace_relative_path.split("/")[-1]
                    QMessageBox.information(
                        self, "Wordlist Saved",
                        f"{src.candidate_count:,} candidates saved.\n"
                        f"Wordlist: {display}\n\n"
                        "Select it in Jobs → Password Source → Workspace wordlist."
                    )
                    self.txt_nickname.clear()
                    self._refresh_list()

                except Exception as exc:
                    QMessageBox.critical(self, "Generation Failed", str(exc))

            # ------------------------------------------------------------------
            # Saved wordlists  (named _refresh_list for main_window auto-refresh)
            # ------------------------------------------------------------------

            def _refresh_list(self) -> None:
                from PySide6.QtWidgets import QListWidgetItem

                from portable_crypt_recovery.services.builders.password_builder import (
                    load_wordlist_meta,
                )
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
                    meta = load_wordlist_meta(p)
                    nickname = meta.get("nickname", "")
                    count = meta.get("candidate_count")
                    if count is None:
                        try:
                            count = sum(
                                1 for _ in p.open("r", encoding="utf-8", errors="replace")
                            )
                        except OSError:
                            count = 0
                    if nickname:
                        label = f"{nickname}  —  {count:,} passwords"
                    else:
                        label = f"{p.name}  —  {count:,} passwords"
                    item = QListWidgetItem(label)
                    item.setData(256, str(p))
                    item.setData(257, nickname)
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
                items = self.saved_list.selectedItems()
                if not items:
                    QMessageBox.information(self, "Delete", "Select one or more wordlists first.")
                    return
                paths = [
                    item.data(256) for item in items if item.data(256) is not None
                ]
                names = "\n".join(
                    item.data(257) or Path(item.data(256)).name
                    for item in items if item.data(256)
                )
                reply = QMessageBox.question(
                    self, "Delete Wordlists",
                    f"Permanently delete {len(paths)} wordlist(s)?\n\n{names}",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No,
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return
                errors: list[str] = []
                for path_str in paths:
                    try:
                        p = Path(path_str)
                        p.unlink(missing_ok=True)
                        # Also remove sidecar
                        p.with_suffix(".meta.json").unlink(missing_ok=True)
                    except Exception as exc:
                        errors.append(f"{path_str}: {exc}")
                if errors:
                    QMessageBox.critical(
                        self, "Delete Failed", "\n".join(errors)
                    )
                self._refresh_list()

            def _rename_wordlist(self) -> None:
                from pathlib import Path  # noqa: PLC0415

                from PySide6.QtWidgets import QInputDialog, QMessageBox

                from portable_crypt_recovery.services.builders.password_builder import (
                    rename_wordlist_nickname,
                )
                item = self.saved_list.currentItem()
                if not item or item.data(256) is None:
                    QMessageBox.information(
                        self, "Rename", "Select a wordlist to rename."
                    )
                    return
                path_str = item.data(256)
                current_name = item.data(257) or Path(path_str).name
                new_name, ok = QInputDialog.getText(
                    self,
                    "Rename Wordlist",
                    "Enter a new name for this wordlist:",
                    text=current_name,
                )
                if not ok or not new_name.strip():
                    return
                try:
                    rename_wordlist_nickname(Path(path_str), new_name.strip())
                    self._refresh_list()
                except Exception as exc:
                    QMessageBox.critical(self, "Rename Failed", str(exc))

        return _PasswordBuilderView()
