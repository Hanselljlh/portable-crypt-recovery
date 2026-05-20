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

                # ---- Filter row 1: Brand | Algorithm | Volume Type | Generation ----
                filter_row = QHBoxLayout()
                filter_row.setSpacing(6)

                # Brand
                grp_brand = QGroupBox("Brand")
                _bl = QVBoxLayout(grp_brand)
                _bl.setSpacing(2)
                _bl.setContentsMargins(6, 4, 6, 4)
                self.chk_vc = QCheckBox("VeraCrypt")
                self.chk_vc.setChecked(True)
                self.chk_tc = QCheckBox("TrueCrypt")
                self.chk_tc.setChecked(True)
                _bl.addWidget(self.chk_vc)
                _bl.addWidget(self.chk_tc)
                filter_row.addWidget(grp_brand)

                # Algorithm
                grp_algo = QGroupBox("Algorithm (KDF / Hash)")
                _al = QVBoxLayout(grp_algo)
                _al.setSpacing(2)
                _al.setContentsMargins(6, 4, 6, 4)
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
                _algo_row1 = QHBoxLayout()
                _algo_row1.setSpacing(8)
                for _w in [self.chk_sha512, self.chk_ripemd, self.chk_sha256]:
                    _algo_row1.addWidget(_w)
                _algo_row1.addStretch()
                _algo_row2 = QHBoxLayout()
                _algo_row2.setSpacing(8)
                for _w in [self.chk_whirlpool, self.chk_streebog]:
                    _algo_row2.addWidget(_w)
                _algo_row2.addStretch()
                _al.addLayout(_algo_row1)
                _al.addLayout(_algo_row2)
                filter_row.addWidget(grp_algo, 1)

                # Volume type
                grp_volume = QGroupBox("Volume Type")
                _vl = QVBoxLayout(grp_volume)
                _vl.setSpacing(2)
                _vl.setContentsMargins(6, 4, 6, 4)
                self.chk_standard = QCheckBox("Standard")
                self.chk_standard.setChecked(True)
                self.chk_boot = QCheckBox("Boot / System")
                self.chk_boot.setChecked(True)
                _vl.addWidget(self.chk_standard)
                _vl.addWidget(self.chk_boot)
                filter_row.addWidget(grp_volume)

                # Generation
                grp_gen = QGroupBox("Generation")
                _gl = QVBoxLayout(grp_gen)
                _gl.setSpacing(2)
                _gl.setContentsMargins(6, 4, 6, 4)
                self.chk_current = QCheckBox("Current")
                self.chk_current.setChecked(True)
                self.chk_legacy = QCheckBox("Legacy")
                self.chk_legacy.setChecked(True)
                _gl.addWidget(self.chk_current)
                _gl.addWidget(self.chk_legacy)
                filter_row.addWidget(grp_gen)

                builder_layout.addLayout(filter_row)

                # ---- Filter row 2: Encryption Type (full-width, all cipher combinations) ----
                # Each cascade level = one Hashcat mode that covers all ciphers in that group.
                # Camellia and Kuznyechik are VeraCrypt-only (added in VC 1.17 / 1.19).
                grp_cipher = QGroupBox("Encryption Type")
                _cil = QVBoxLayout(grp_cipher)
                _cil.setSpacing(3)
                _cil.setContentsMargins(6, 4, 6, 4)

                _cnote = QLabel(
                    "All ciphers at the same cascade level share one Hashcat mode — checking any"
                    " cipher in a group includes that level's modes."
                    "  † = VeraCrypt only (not available in TrueCrypt)."
                )
                _cnote.setStyleSheet("font-size: 10px; color: #888;")
                _cnote.setWordWrap(True)
                _cil.addWidget(_cnote)

                # Single cipher row (cascade=1, XTS 512-bit)
                _r1 = QHBoxLayout()
                _r1.setSpacing(8)
                _r1.addWidget(QLabel("Single:"))
                self.chk_aes = QCheckBox("AES")
                self.chk_aes.setChecked(True)
                self.chk_camellia = QCheckBox("Camellia †")
                self.chk_camellia.setChecked(True)
                self.chk_kuznyechik = QCheckBox("Kuznyechik †")
                self.chk_kuznyechik.setChecked(True)
                self.chk_serpent = QCheckBox("Serpent")
                self.chk_serpent.setChecked(True)
                self.chk_twofish = QCheckBox("Twofish")
                self.chk_twofish.setChecked(True)
                for _w in [
                    self.chk_aes, self.chk_camellia, self.chk_kuznyechik,
                    self.chk_serpent, self.chk_twofish,
                ]:
                    _r1.addWidget(_w)
                _r1.addStretch()
                _cil.addLayout(_r1)

                # Two-cipher row A — classic (TC + VC)
                _r2a = QHBoxLayout()
                _r2a.setSpacing(8)
                _r2a.addWidget(QLabel("Two-cipher:"))
                self.chk_at = QCheckBox("AES-Twofish")
                self.chk_at.setChecked(True)
                self.chk_sa = QCheckBox("Serpent-AES")
                self.chk_sa.setChecked(True)
                self.chk_ts = QCheckBox("Twofish-Serpent")
                self.chk_ts.setChecked(True)
                for _w in [self.chk_at, self.chk_sa, self.chk_ts]:
                    _r2a.addWidget(_w)
                _r2a.addStretch()
                _cil.addLayout(_r2a)

                # Two-cipher row B — VeraCrypt-only combinations
                _r2b = QHBoxLayout()
                _r2b.setSpacing(8)
                _r2b.addSpacing(78)  # align under row A ciphers
                self.chk_ck = QCheckBox("Camellia-Kuznyechik †")
                self.chk_ck.setChecked(True)
                self.chk_cs = QCheckBox("Camellia-Serpent †")
                self.chk_cs.setChecked(True)
                self.chk_ka = QCheckBox("Kuznyechik-AES †")
                self.chk_ka.setChecked(True)
                self.chk_ks = QCheckBox("Kuznyechik-Serpent †")
                self.chk_ks.setChecked(True)
                self.chk_kt = QCheckBox("Kuznyechik-Twofish †")
                self.chk_kt.setChecked(True)
                self.chk_tk = QCheckBox("Twofish-Kuznyechik †")
                self.chk_tk.setChecked(True)
                for _w in [
                    self.chk_ck, self.chk_cs, self.chk_ka,
                    self.chk_ks, self.chk_kt, self.chk_tk,
                ]:
                    _r2b.addWidget(_w)
                _r2b.addStretch()
                _cil.addLayout(_r2b)

                # Three-cipher row A — classic (TC + VC)
                _r3a = QHBoxLayout()
                _r3a.setSpacing(8)
                _r3a.addWidget(QLabel("Three-cipher:"))
                self.chk_ats = QCheckBox("AES-Twofish-Serpent")
                self.chk_ats.setChecked(True)
                _r3a.addWidget(self.chk_ats)
                _r3a.addStretch()
                _cil.addLayout(_r3a)

                # Three-cipher row B — VeraCrypt-only combinations
                _r3b = QHBoxLayout()
                _r3b.setSpacing(8)
                _r3b.addSpacing(90)  # align under row A ciphers
                self.chk_ckt = QCheckBox("Camellia-Kuznyechik-Twofish †")
                self.chk_ckt.setChecked(True)
                self.chk_kat = QCheckBox("Kuznyechik-AES-Twofish †")
                self.chk_kat.setChecked(True)
                self.chk_ksc = QCheckBox("Kuznyechik-Serpent-Camellia †")
                self.chk_ksc.setChecked(True)
                self.chk_sta = QCheckBox("Serpent-Twofish-AES †")
                self.chk_sta.setChecked(True)
                self.chk_tsa = QCheckBox("Twofish-Serpent-AES †")
                self.chk_tsa.setChecked(True)
                for _w in [
                    self.chk_ckt, self.chk_kat, self.chk_ksc,
                    self.chk_sta, self.chk_tsa,
                ]:
                    _r3b.addWidget(_w)
                _r3b.addStretch()
                _cil.addLayout(_r3b)

                builder_layout.addWidget(grp_cipher)

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
                    # single-cipher
                    self.chk_aes, self.chk_camellia, self.chk_kuznyechik,
                    self.chk_serpent, self.chk_twofish,
                    # two-cipher classic
                    self.chk_at, self.chk_sa, self.chk_ts,
                    # two-cipher VC-only
                    self.chk_ck, self.chk_cs, self.chk_ka,
                    self.chk_ks, self.chk_kt, self.chk_tk,
                    # three-cipher classic
                    self.chk_ats,
                    # three-cipher VC-only
                    self.chk_ckt, self.chk_kat, self.chk_ksc,
                    self.chk_sta, self.chk_tsa,
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

                want_c1 = (
                    self.chk_aes.isChecked()
                    or self.chk_camellia.isChecked()
                    or self.chk_kuznyechik.isChecked()
                    or self.chk_serpent.isChecked()
                    or self.chk_twofish.isChecked()
                )
                want_c2 = (
                    self.chk_at.isChecked() or self.chk_sa.isChecked()
                    or self.chk_ts.isChecked() or self.chk_ck.isChecked()
                    or self.chk_cs.isChecked() or self.chk_ka.isChecked()
                    or self.chk_ks.isChecked() or self.chk_kt.isChecked()
                    or self.chk_tk.isChecked()
                )
                want_c3 = (
                    self.chk_ats.isChecked() or self.chk_ckt.isChecked()
                    or self.chk_kat.isChecked() or self.chk_ksc.isChecked()
                    or self.chk_sta.isChecked() or self.chk_tsa.isChecked()
                )
                c_want = {1: want_c1, 2: want_c2, 3: want_c3}
                if not c_want.get(entry.cipher_cascade, True):
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
                try:
                    save_named_hash_set(app_state.workspace_root, hms)
                except Exception as exc:
                    QMessageBox.critical(
                        self, "Save Error",
                        f"Could not save hash set:\n{exc}\n\n"
                        "Check workspace folder permissions.",
                    )
                    return
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

            def _refresh_list(self) -> None:
                """Called by main_window on navigation to keep saved sets current."""
                self._refresh_saved_list()

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
                try:
                    save_named_hash_set(get_app_state().workspace_root, hms)
                except Exception as exc:
                    QMessageBox.critical(self, "Rename Error", f"Could not rename hash set:\n{exc}")
                    return
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
