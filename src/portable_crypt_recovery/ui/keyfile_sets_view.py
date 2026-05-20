"""Keyfile Sets view — build and save named keyfile configurations."""

from __future__ import annotations


class KeyfileSetsView:  # pragma: no cover
    """Build and save reusable named keyfile sets."""

    def __new__(cls):
        from PySide6.QtWidgets import (
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

        class _KeyfileSetsView(QWidget):
            def __init__(self) -> None:
                super().__init__()
                from PySide6.QtCore import Qt

                layout = QVBoxLayout(self)
                layout.setContentsMargins(8, 8, 8, 8)

                splitter = QSplitter(Qt.Orientation.Vertical)

                # ----------------------------------------------------------------
                # Top pane: builder
                # ----------------------------------------------------------------
                builder_widget = QWidget()
                builder_layout = QVBoxLayout(builder_widget)
                builder_layout.setContentsMargins(0, 0, 0, 0)

                builder_group = QGroupBox("Keyfile Set Builder")
                bg_layout = QVBoxLayout(builder_group)

                bg_layout.addWidget(QLabel(
                    "Add keyfiles to this set.  When saved, each file will be normalized "
                    "and stored in the workspace.  Use 'Load Saved Keyfile Set' in Job "
                    "drafts to apply the set."
                ))

                self.kf_list = QListWidget()
                self.kf_list.setMinimumHeight(100)
                bg_layout.addWidget(self.kf_list, 1)

                kf_btn_row = QHBoxLayout()
                self.btn_add_kf = QPushButton("Add Keyfile(s)…")
                self.btn_remove_kf = QPushButton("Remove Selected")
                self.btn_clear_kf = QPushButton("Clear All")
                for _b in [self.btn_add_kf, self.btn_remove_kf, self.btn_clear_kf]:
                    kf_btn_row.addWidget(_b)
                kf_btn_row.addStretch()
                bg_layout.addLayout(kf_btn_row)

                notes_row = QHBoxLayout()
                notes_row.addWidget(QLabel("Notes:"))
                self.txt_notes = QLineEdit()
                self.txt_notes.setPlaceholderText("Optional notes about this keyfile set")
                notes_row.addWidget(self.txt_notes, 1)
                bg_layout.addLayout(notes_row)

                save_row = QHBoxLayout()
                save_row.addWidget(QLabel("Set name:"))
                self.txt_set_name = QLineEdit()
                self.txt_set_name.setPlaceholderText("e.g. USB keyfiles")
                save_row.addWidget(self.txt_set_name, 1)
                self.btn_save = QPushButton("Save as Set")
                save_row.addWidget(self.btn_save)
                bg_layout.addLayout(save_row)

                builder_layout.addWidget(builder_group)
                splitter.addWidget(builder_widget)

                # ----------------------------------------------------------------
                # Bottom pane: saved sets
                # ----------------------------------------------------------------
                saved_widget = QWidget()
                saved_layout = QVBoxLayout(saved_widget)
                saved_layout.setContentsMargins(0, 0, 0, 0)
                saved_layout.addWidget(QLabel("Saved Keyfile Sets:"))

                self.saved_list = QListWidget()
                saved_layout.addWidget(self.saved_list, 1)

                saved_btn_row = QHBoxLayout()
                self.btn_load = QPushButton("Load into Builder")
                self.btn_rename = QPushButton("Rename…")
                self.btn_delete_set = QPushButton("Delete")
                for _b in [self.btn_load, self.btn_rename, self.btn_delete_set]:
                    saved_btn_row.addWidget(_b)
                saved_btn_row.addStretch()
                saved_layout.addLayout(saved_btn_row)

                splitter.addWidget(saved_widget)
                splitter.setSizes([320, 220])
                layout.addWidget(splitter)

                # Wire signals
                self.btn_add_kf.clicked.connect(self._add_keyfiles)
                self.btn_remove_kf.clicked.connect(self._remove_keyfile)
                self.btn_clear_kf.clicked.connect(self._clear_keyfiles)
                self.btn_save.clicked.connect(self._save_set)
                self.btn_load.clicked.connect(self._load_set)
                self.btn_rename.clicked.connect(self._rename_set)
                self.btn_delete_set.clicked.connect(self._delete_set)

                self._refresh_saved_list()

            # ----------------------------------------------------------------
            # Keyfile list management
            # ----------------------------------------------------------------

            def _add_keyfiles(self) -> None:
                from PySide6.QtWidgets import QFileDialog, QListWidgetItem

                paths, _ = QFileDialog.getOpenFileNames(
                    self, "Select Keyfile(s)", "", "All Files (*.*)"
                )
                existing = {
                    self.kf_list.item(i).data(256)
                    for i in range(self.kf_list.count())
                }
                for path in paths:
                    if path and path not in existing:
                        item = QListWidgetItem(path)
                        item.setData(256, path)
                        self.kf_list.addItem(item)
                        existing.add(path)

            def _remove_keyfile(self) -> None:
                row = self.kf_list.currentRow()
                if row >= 0:
                    self.kf_list.takeItem(row)

            def _clear_keyfiles(self) -> None:
                self.kf_list.clear()

            # ----------------------------------------------------------------
            # Save / Load / Rename / Delete
            # ----------------------------------------------------------------

            def _save_set(self) -> None:
                from pathlib import Path

                from PySide6.QtWidgets import QMessageBox

                from portable_crypt_recovery.app.app_state import get_app_state
                from portable_crypt_recovery.core.ids import new_id
                from portable_crypt_recovery.models.keyfile_set import KeyfileSet
                from portable_crypt_recovery.services.builders.keyfile_builder import (
                    import_keyfile,
                    save_named_keyfile_set,
                )

                app_state = get_app_state()
                if not app_state.is_workspace_open():
                    QMessageBox.warning(self, "No Workspace", "Open a workspace first.")
                    return

                name = self.txt_set_name.text().strip()
                if not name:
                    QMessageBox.warning(self, "No Name", "Enter a name for this set.")
                    return

                paths = [
                    self.kf_list.item(i).data(256)
                    for i in range(self.kf_list.count())
                ]
                if not paths:
                    QMessageBox.warning(self, "No Keyfiles", "Add at least one keyfile.")
                    return

                # Normalize and import each keyfile
                entries = []
                errors = []
                for p in paths:
                    try:
                        entry = import_keyfile(Path(p), app_state.workspace_root)
                        entries.append(entry)
                    except Exception as exc:
                        errors.append(f"{p}: {exc}")

                if errors:
                    QMessageBox.warning(
                        self, "Import Errors",
                        "Some keyfiles could not be imported:\n" + "\n".join(errors[:5]),
                    )
                if not entries:
                    return

                ks = KeyfileSet(
                    set_id=new_id("kfset"),
                    nickname=name,
                    entries=entries,
                    notes=self.txt_notes.text().strip(),
                )
                save_named_keyfile_set(app_state.workspace_root, ks)
                self.txt_set_name.clear()
                self._refresh_saved_list()
                QMessageBox.information(
                    self, "Saved",
                    f"Keyfile set '{name}' saved with {len(entries)} file(s).",
                )

            def _refresh_saved_list(self) -> None:
                from PySide6.QtWidgets import QListWidgetItem

                from portable_crypt_recovery.app.app_state import get_app_state
                from portable_crypt_recovery.services.builders.keyfile_builder import (
                    list_named_keyfile_sets,
                )

                self.saved_list.clear()
                app_state = get_app_state()
                if not app_state.is_workspace_open():
                    return

                for ks in list_named_keyfile_sets(app_state.workspace_root):
                    n = len(ks.entries)
                    notes_tag = f"  — {ks.notes}" if ks.notes else ""
                    item = QListWidgetItem(
                        f"{ks.nickname}  ({n} file{'s' if n != 1 else ''}){notes_tag}"
                    )
                    item.setData(256, ks)
                    self.saved_list.addItem(item)

            def _load_set(self) -> None:
                from PySide6.QtWidgets import QListWidgetItem, QMessageBox

                item = self.saved_list.currentItem()
                if not item:
                    QMessageBox.information(self, "Load", "Select a saved set first.")
                    return
                ks = item.data(256)
                if not ks:
                    return

                self.kf_list.clear()
                for entry in ks.entries:
                    display = entry.original_path or entry.normalized_workspace_path
                    kf_item = QListWidgetItem(display)
                    kf_item.setData(256, entry.original_path)
                    self.kf_list.addItem(kf_item)

                self.txt_notes.setText(ks.notes or "")
                self.txt_set_name.setText(ks.nickname)

            def _rename_set(self) -> None:
                from PySide6.QtWidgets import QInputDialog, QMessageBox

                from portable_crypt_recovery.app.app_state import get_app_state
                from portable_crypt_recovery.services.builders.keyfile_builder import (
                    save_named_keyfile_set,
                )

                item = self.saved_list.currentItem()
                if not item:
                    QMessageBox.information(self, "Rename", "Select a set to rename.")
                    return
                ks = item.data(256)
                if not ks:
                    return

                new_name, ok = QInputDialog.getText(
                    self, "Rename Set", "New name:", text=ks.nickname
                )
                if not ok or not new_name.strip():
                    return

                ks.nickname = new_name.strip()
                save_named_keyfile_set(get_app_state().workspace_root, ks)
                self._refresh_saved_list()

            def _delete_set(self) -> None:
                from PySide6.QtWidgets import QMessageBox

                from portable_crypt_recovery.app.app_state import get_app_state
                from portable_crypt_recovery.services.builders.keyfile_builder import (
                    delete_named_keyfile_set,
                )

                item = self.saved_list.currentItem()
                if not item:
                    QMessageBox.warning(self, "Delete", "Select a set to delete.")
                    return
                ks = item.data(256)
                if not ks:
                    return

                reply = QMessageBox.question(
                    self, "Delete Keyfile Set",
                    f"Delete keyfile set '{ks.nickname}'?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No,
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return

                delete_named_keyfile_set(get_app_state().workspace_root, ks.set_id)
                self._refresh_saved_list()

        return _KeyfileSetsView()
