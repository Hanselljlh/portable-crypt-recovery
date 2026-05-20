"""Hash Sets view — build and save named collections of Hashcat modes."""

from __future__ import annotations


class HashSetsView:  # pragma: no cover
    """Browse, filter, and save named hash mode sets."""

    def __new__(cls):
        from PySide6.QtWidgets import (
            QCheckBox,
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

        class _HashSetsView(QWidget):
            def __init__(self) -> None:
                super().__init__()
                from PySide6.QtCore import Qt

                layout = QVBoxLayout(self)
                layout.setContentsMargins(8, 8, 8, 8)

                splitter = QSplitter(Qt.Orientation.Vertical)

                # ----------------------------------------------------------------
                # Top pane: filter + checklist builder
                # ----------------------------------------------------------------
                builder_widget = QWidget()
                builder_layout = QVBoxLayout(builder_widget)
                builder_layout.setContentsMargins(0, 0, 0, 0)

                filter_group = QGroupBox("Filter Modes")
                filter_layout = QVBoxLayout(filter_group)

                # Row 1: Brand + Algorithm
                row1 = QHBoxLayout()
                row1.addWidget(QLabel("Brand:"))
                self.chk_vc = QCheckBox("VeraCrypt")
                self.chk_vc.setChecked(True)
                self.chk_tc = QCheckBox("TrueCrypt")
                self.chk_tc.setChecked(True)
                row1.addWidget(self.chk_vc)
                row1.addWidget(self.chk_tc)
                row1.addSpacing(20)

                row1.addWidget(QLabel("Algorithm:"))
                self.chk_sha512 = QCheckBox("SHA-512")
                self.chk_sha512.setChecked(True)
                self.chk_ripemd = QCheckBox("RIPEMD-160")
                self.chk_ripemd.setChecked(True)
                self.chk_sha256 = QCheckBox("SHA-256")
                self.chk_sha256.setChecked(True)
                self.chk_whirlpool = QCheckBox("Whirlpool")
                self.chk_whirlpool.setChecked(True)
                self.chk_streebog = QCheckBox("Streebog-512")
                self.chk_streebog.setChecked(True)
                for _w in [
                    self.chk_sha512, self.chk_ripemd, self.chk_sha256,
                    self.chk_whirlpool, self.chk_streebog,
                ]:
                    row1.addWidget(_w)
                row1.addStretch()
                filter_layout.addLayout(row1)

                # Row 2: Cascade + Volume type + Generation
                row2 = QHBoxLayout()
                row2.addWidget(QLabel("Cascade:"))
                self.chk_c1 = QCheckBox("Single (×1)")
                self.chk_c1.setChecked(True)
                self.chk_c2 = QCheckBox("Cascade ×2")
                self.chk_c2.setChecked(True)
                self.chk_c3 = QCheckBox("Cascade ×3")
                self.chk_c3.setChecked(True)
                row2.addWidget(self.chk_c1)
                row2.addWidget(self.chk_c2)
                row2.addWidget(self.chk_c3)
                row2.addSpacing(20)

                row2.addWidget(QLabel("Volume:"))
                self.chk_standard = QCheckBox("Standard")
                self.chk_standard.setChecked(True)
                self.chk_boot = QCheckBox("Boot/System")
                self.chk_boot.setChecked(True)
                row2.addWidget(self.chk_standard)
                row2.addWidget(self.chk_boot)
                row2.addSpacing(20)

                row2.addWidget(QLabel("Generation:"))
                self.chk_current = QCheckBox("Current")
                self.chk_current.setChecked(True)
                self.chk_legacy = QCheckBox("Legacy")
                self.chk_legacy.setChecked(True)
                row2.addWidget(self.chk_current)
                row2.addWidget(self.chk_legacy)
                row2.addStretch()
                filter_layout.addLayout(row2)

                builder_layout.addWidget(filter_group)

                # Mode checklist
                self.mode_list = QListWidget()
                self.mode_list.setMinimumHeight(200)
                builder_layout.addWidget(self.mode_list, 1)

                # Quick-select buttons + checked count
                qsel_row = QHBoxLayout()
                self.btn_check_all = QPushButton("Check All")
                self.btn_uncheck_all = QPushButton("Uncheck All")
                self.btn_check_filtered = QPushButton("Check Visible")
                self.btn_uncheck_filtered = QPushButton("Uncheck Visible")
                for _b in [
                    self.btn_check_all, self.btn_uncheck_all,
                    self.btn_check_filtered, self.btn_uncheck_filtered,
                ]:
                    qsel_row.addWidget(_b)
                qsel_row.addStretch()
                self._lbl_count = QLabel("0/0 checked")
                qsel_row.addWidget(self._lbl_count)
                builder_layout.addLayout(qsel_row)

                # Save row
                save_row = QHBoxLayout()
                save_row.addWidget(QLabel("Set name:"))
                self.txt_set_name = QLineEdit()
                self.txt_set_name.setPlaceholderText("e.g. VeraCrypt SHA-512 only")
                save_row.addWidget(self.txt_set_name, 1)
                self.btn_save = QPushButton("Save Checked as Set")
                save_row.addWidget(self.btn_save)
                builder_layout.addLayout(save_row)

                splitter.addWidget(builder_widget)

                # ----------------------------------------------------------------
                # Bottom pane: saved sets
                # ----------------------------------------------------------------
                saved_widget = QWidget()
                saved_layout = QVBoxLayout(saved_widget)
                saved_layout.setContentsMargins(0, 0, 0, 0)
                saved_layout.addWidget(QLabel("Saved Hash Sets:"))

                self.saved_list = QListWidget()
                saved_layout.addWidget(self.saved_list, 1)

                saved_btn_row = QHBoxLayout()
                self.btn_load = QPushButton("Load into Checklist")
                self.btn_rename = QPushButton("Rename…")
                self.btn_delete_set = QPushButton("Delete")
                for _b in [self.btn_load, self.btn_rename, self.btn_delete_set]:
                    saved_btn_row.addWidget(_b)
                saved_btn_row.addStretch()
                saved_layout.addLayout(saved_btn_row)

                splitter.addWidget(saved_widget)
                splitter.setSizes([420, 200])
                layout.addWidget(splitter)

                # Wire filter checkboxes
                for _chk in [
                    self.chk_vc, self.chk_tc,
                    self.chk_sha512, self.chk_ripemd, self.chk_sha256,
                    self.chk_whirlpool, self.chk_streebog,
                    self.chk_c1, self.chk_c2, self.chk_c3,
                    self.chk_standard, self.chk_boot,
                    self.chk_current, self.chk_legacy,
                ]:
                    _chk.toggled.connect(self._apply_filters)

                self.btn_check_all.clicked.connect(self._check_all)
                self.btn_uncheck_all.clicked.connect(self._uncheck_all)
                self.btn_check_filtered.clicked.connect(self._check_filtered)
                self.btn_uncheck_filtered.clicked.connect(self._uncheck_filtered)
                self.btn_save.clicked.connect(self._save_set)
                self.btn_load.clicked.connect(self._load_set)
                self.btn_rename.clicked.connect(self._rename_set)
                self.btn_delete_set.clicked.connect(self._delete_set)

                self._all_entries: list = []
                self._populate_mode_list()
                self._refresh_saved_list()

            # ----------------------------------------------------------------
            # Mode list population and filtering
            # ----------------------------------------------------------------

            def _populate_mode_list(self) -> None:
                from PySide6.QtCore import Qt
                from PySide6.QtWidgets import QListWidgetItem

                from portable_crypt_recovery.services.builders.hash_mode_builder import (
                    algo_from_label,
                    all_mode_entries,
                )

                self._all_entries = all_mode_entries()
                self.mode_list.clear()
                for entry in self._all_entries:
                    algo = algo_from_label(entry.label)
                    tags = []
                    if entry.is_legacy:
                        tags.append("legacy")
                    if entry.is_system:
                        tags.append("boot")
                    tag_str = f"  [{', '.join(tags)}]" if tags else ""
                    fam = "VC" if entry.family == "veracrypt" else "TC"
                    text = (
                        f"{entry.mode:>6}  {fam}  {algo}  ×{entry.cipher_cascade}"
                        f"  {entry.label}{tag_str}"
                    )
                    item = QListWidgetItem(text)
                    item.setCheckState(Qt.CheckState.Checked)
                    item.setData(256, entry)
                    self.mode_list.addItem(item)

                self._apply_filters()

            def _matches_filters(self, entry) -> bool:
                from portable_crypt_recovery.services.builders.hash_mode_builder import (
                    algo_from_label,
                )

                if entry.family == "veracrypt" and not self.chk_vc.isChecked():
                    return False
                if entry.family == "truecrypt" and not self.chk_tc.isChecked():
                    return False

                algo = algo_from_label(entry.label)
                algo_map = {
                    "SHA-512": self.chk_sha512,
                    "SHA-256": self.chk_sha256,
                    "RIPEMD-160": self.chk_ripemd,
                    "Whirlpool": self.chk_whirlpool,
                    "Streebog-512": self.chk_streebog,
                }
                chk = algo_map.get(algo)
                if chk is not None and not chk.isChecked():
                    return False

                c_map = {1: self.chk_c1, 2: self.chk_c2, 3: self.chk_c3}
                cc_chk = c_map.get(entry.cipher_cascade)
                if cc_chk is not None and not cc_chk.isChecked():
                    return False

                if entry.is_system and not self.chk_boot.isChecked():
                    return False
                if not entry.is_system and not self.chk_standard.isChecked():
                    return False

                if entry.is_legacy and not self.chk_legacy.isChecked():
                    return False
                return entry.is_legacy or self.chk_current.isChecked()

            def _apply_filters(self) -> None:
                for i in range(self.mode_list.count()):
                    item = self.mode_list.item(i)
                    entry = item.data(256)
                    item.setHidden(not self._matches_filters(entry))
                self._update_count()

            def _update_count(self) -> None:
                from PySide6.QtCore import Qt

                checked = sum(
                    1 for i in range(self.mode_list.count())
                    if (
                        not self.mode_list.item(i).isHidden()
                        and self.mode_list.item(i).checkState() == Qt.CheckState.Checked
                    )
                )
                visible = sum(
                    1 for i in range(self.mode_list.count())
                    if not self.mode_list.item(i).isHidden()
                )
                self._lbl_count.setText(f"{checked}/{visible} checked")

            # ----------------------------------------------------------------
            # Quick-select helpers
            # ----------------------------------------------------------------

            def _set_check_state(self, checked: bool, visible_only: bool = False) -> None:
                from PySide6.QtCore import Qt

                state = Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked
                for i in range(self.mode_list.count()):
                    item = self.mode_list.item(i)
                    if visible_only and item.isHidden():
                        continue
                    item.setCheckState(state)
                self._update_count()

            def _check_all(self) -> None:
                self._set_check_state(True)

            def _uncheck_all(self) -> None:
                self._set_check_state(False)

            def _check_filtered(self) -> None:
                self._set_check_state(True, visible_only=True)

            def _uncheck_filtered(self) -> None:
                self._set_check_state(False, visible_only=True)

            # ----------------------------------------------------------------
            # Save / Load / Rename / Delete
            # ----------------------------------------------------------------

            def _save_set(self) -> None:
                from PySide6.QtCore import Qt
                from PySide6.QtWidgets import QMessageBox

                from portable_crypt_recovery.app.app_state import get_app_state
                from portable_crypt_recovery.core.ids import new_id
                from portable_crypt_recovery.models.hash_mode_set import HashModeSet
                from portable_crypt_recovery.services.builders.hash_mode_builder import (
                    save_named_hash_set,
                )

                app_state = get_app_state()
                if not app_state.is_workspace_open():
                    QMessageBox.warning(self, "No Workspace", "Open a workspace first.")
                    return

                name = self.txt_set_name.text().strip()
                if not name:
                    QMessageBox.warning(self, "No Name", "Enter a name for this set.")
                    return

                entries = [
                    self.mode_list.item(i).data(256)
                    for i in range(self.mode_list.count())
                    if (
                        self.mode_list.item(i).checkState() == Qt.CheckState.Checked
                        and self.mode_list.item(i).data(256) is not None
                    )
                ]
                if not entries:
                    QMessageBox.warning(self, "No Modes", "Check at least one mode before saving.")
                    return

                hms = HashModeSet(
                    mode_set_id=new_id("modeset"),
                    nickname=name,
                    entries=entries,
                )
                save_named_hash_set(app_state.workspace_root, hms)
                self.txt_set_name.clear()
                self._refresh_saved_list()
                QMessageBox.information(
                    self, "Saved",
                    f"Hash set '{name}' saved with {len(entries)} mode(s).",
                )

            def _refresh_saved_list(self) -> None:
                from PySide6.QtWidgets import QListWidgetItem

                from portable_crypt_recovery.app.app_state import get_app_state
                from portable_crypt_recovery.services.builders.hash_mode_builder import (
                    list_named_hash_sets,
                )

                self.saved_list.clear()
                app_state = get_app_state()
                if not app_state.is_workspace_open():
                    return

                for hms in list_named_hash_sets(app_state.workspace_root):
                    n = len(hms.entries)
                    item = QListWidgetItem(
                        f"{hms.nickname}  ({n} mode{'s' if n != 1 else ''})"
                    )
                    item.setData(256, hms)
                    self.saved_list.addItem(item)

            def _load_set(self) -> None:
                from PySide6.QtCore import Qt
                from PySide6.QtWidgets import QMessageBox

                item = self.saved_list.currentItem()
                if not item:
                    QMessageBox.information(self, "Load", "Select a saved set first.")
                    return
                hms = item.data(256)
                if not hms:
                    return

                mode_nums = {e.mode for e in hms.entries}
                for i in range(self.mode_list.count()):
                    entry = self.mode_list.item(i).data(256)
                    is_match = entry is not None and entry.mode in mode_nums
                    self.mode_list.item(i).setCheckState(
                        Qt.CheckState.Checked if is_match else Qt.CheckState.Unchecked
                    )
                    if is_match:
                        self.mode_list.item(i).setHidden(False)

                self._update_count()
                QMessageBox.information(
                    self, "Loaded",
                    f"Set '{hms.nickname}' loaded — {len(mode_nums)} mode(s) checked.",
                )

            def _rename_set(self) -> None:
                from PySide6.QtWidgets import QInputDialog, QMessageBox

                from portable_crypt_recovery.app.app_state import get_app_state
                from portable_crypt_recovery.services.builders.hash_mode_builder import (
                    save_named_hash_set,
                )

                item = self.saved_list.currentItem()
                if not item:
                    QMessageBox.information(self, "Rename", "Select a set to rename.")
                    return
                hms = item.data(256)
                if not hms:
                    return

                new_name, ok = QInputDialog.getText(
                    self, "Rename Set", "New name:", text=hms.nickname
                )
                if not ok or not new_name.strip():
                    return

                hms.nickname = new_name.strip()
                save_named_hash_set(get_app_state().workspace_root, hms)
                self._refresh_saved_list()

            def _delete_set(self) -> None:
                from PySide6.QtWidgets import QMessageBox

                from portable_crypt_recovery.app.app_state import get_app_state
                from portable_crypt_recovery.services.builders.hash_mode_builder import (
                    delete_named_hash_set,
                )

                item = self.saved_list.currentItem()
                if not item:
                    QMessageBox.warning(self, "Delete", "Select a set to delete.")
                    return
                hms = item.data(256)
                if not hms:
                    return

                reply = QMessageBox.question(
                    self, "Delete Set",
                    f"Delete hash set '{hms.nickname}'?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No,
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return

                delete_named_hash_set(get_app_state().workspace_root, hms.mode_set_id)
                self._refresh_saved_list()

        return _HashSetsView()
