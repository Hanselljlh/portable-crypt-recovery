"""PIM Sets view — build and save named PIM configurations."""

from __future__ import annotations


class PimSetsView:  # pragma: no cover
    """Build and save reusable named PIM sets."""

    def __new__(cls):
        from PySide6.QtWidgets import (
            QGroupBox,
            QHBoxLayout,
            QLabel,
            QLineEdit,
            QListWidget,
            QPlainTextEdit,
            QPushButton,
            QRadioButton,
            QSplitter,
            QVBoxLayout,
            QWidget,
        )

        class _PimSetsView(QWidget):
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

                builder_group = QGroupBox("PIM Configuration")
                bg_layout = QVBoxLayout(builder_group)

                bg_layout.addWidget(QLabel(
                    "Enter PIM values or ranges (comma / newline separated).  "
                    "Example: 485, 500-510"
                ))

                self.rad_default = QRadioButton("Use default PIM — recommended for most volumes")
                self.rad_custom = QRadioButton("Custom PIM values:")
                self.rad_default.setChecked(True)
                bg_layout.addWidget(self.rad_default)
                bg_layout.addWidget(self.rad_custom)

                self.txt_pim = QPlainTextEdit()
                self.txt_pim.setPlaceholderText("e.g. 485\n500-510\n1000")
                self.txt_pim.setMaximumHeight(100)
                self.txt_pim.setEnabled(False)
                bg_layout.addWidget(self.txt_pim)

                notes_row = QHBoxLayout()
                notes_row.addWidget(QLabel("Notes:"))
                self.txt_notes = QLineEdit()
                self.txt_notes.setPlaceholderText("Optional notes about this PIM set")
                notes_row.addWidget(self.txt_notes, 1)
                bg_layout.addLayout(notes_row)

                save_row = QHBoxLayout()
                save_row.addWidget(QLabel("Set name:"))
                self.txt_set_name = QLineEdit()
                self.txt_set_name.setPlaceholderText("e.g. Known PIM range")
                save_row.addWidget(self.txt_set_name, 1)
                self.btn_save = QPushButton("Save as Set")
                save_row.addWidget(self.btn_save)
                bg_layout.addLayout(save_row)

                builder_layout.addWidget(builder_group)
                builder_layout.addStretch()
                splitter.addWidget(builder_widget)

                # ----------------------------------------------------------------
                # Bottom pane: saved sets
                # ----------------------------------------------------------------
                saved_widget = QWidget()
                saved_layout = QVBoxLayout(saved_widget)
                saved_layout.setContentsMargins(0, 0, 0, 0)
                saved_layout.addWidget(QLabel("Saved PIM Sets:"))

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
                splitter.setSizes([280, 220])
                layout.addWidget(splitter)

                # Wire signals
                self.rad_custom.toggled.connect(
                    lambda checked: self.txt_pim.setEnabled(checked)
                )
                self.btn_save.clicked.connect(self._save_set)
                self.btn_load.clicked.connect(self._load_set)
                self.btn_rename.clicked.connect(self._rename_set)
                self.btn_delete_set.clicked.connect(self._delete_set)

                self._refresh_saved_list()

            # ----------------------------------------------------------------
            # Save / Load / Rename / Delete
            # ----------------------------------------------------------------

            def _save_set(self) -> None:
                from PySide6.QtWidgets import QMessageBox

                from portable_crypt_recovery.app.app_state import get_app_state
                from portable_crypt_recovery.core.ids import new_id
                from portable_crypt_recovery.models.pim_set import PimSet
                from portable_crypt_recovery.services.builders.pim_builder import (
                    expand_pim_input,
                    save_named_pim_set,
                )

                app_state = get_app_state()
                if not app_state.is_workspace_open():
                    QMessageBox.warning(self, "No Workspace", "Open a workspace first.")
                    return

                name = self.txt_set_name.text().strip()
                if not name:
                    QMessageBox.warning(self, "No Name", "Enter a name for this set.")
                    return

                if self.rad_default.isChecked():
                    ps = PimSet(
                        pim_set_id=new_id("pimset"),
                        nickname=name,
                        pim_mode="default",
                        values=[],
                        notes=self.txt_notes.text().strip(),
                    )
                    detail = "default PIM"
                else:
                    raw = self.txt_pim.toPlainText().strip()
                    if not raw:
                        QMessageBox.warning(self, "No PIM Values", "Enter at least one PIM value.")
                        return
                    try:
                        values = expand_pim_input(raw)
                    except Exception as exc:
                        QMessageBox.critical(self, "Invalid PIM", str(exc))
                        return
                    ps = PimSet(
                        pim_set_id=new_id("pimset"),
                        nickname=name,
                        pim_mode="custom",
                        values=values,
                        notes=self.txt_notes.text().strip(),
                    )
                    detail = f"{len(values)} value{'s' if len(values) != 1 else ''}"

                try:
                    save_named_pim_set(app_state.workspace_root, ps)
                except Exception as exc:
                    QMessageBox.critical(
                        self, "Save Error",
                        f"Could not save PIM set:\n{exc}\n\n"
                        "Check workspace folder permissions.",
                    )
                    return
                self.txt_set_name.clear()
                self._refresh_saved_list()
                QMessageBox.information(self, "Saved", f"PIM set '{name}' saved ({detail}).")

            def _refresh_saved_list(self) -> None:
                from PySide6.QtWidgets import QListWidgetItem

                from portable_crypt_recovery.app.app_state import get_app_state
                from portable_crypt_recovery.services.builders.pim_builder import (
                    list_named_pim_sets,
                )

                self.saved_list.clear()
                app_state = get_app_state()
                if not app_state.is_workspace_open():
                    return

                for ps in list_named_pim_sets(app_state.workspace_root):
                    if ps.pim_mode == "default":
                        detail = "default PIM"
                    else:
                        n = len(ps.values)
                        detail = f"{n} value{'s' if n != 1 else ''}"
                    notes_tag = f"  — {ps.notes}" if ps.notes else ""
                    item = QListWidgetItem(f"{ps.nickname}  ({detail}){notes_tag}")
                    item.setData(256, ps)
                    self.saved_list.addItem(item)

            def _refresh_list(self) -> None:
                """Called by main_window on navigation to keep saved sets current."""
                self._refresh_saved_list()

            def _load_set(self) -> None:
                from PySide6.QtWidgets import QMessageBox

                item = self.saved_list.currentItem()
                if not item:
                    QMessageBox.information(self, "Load", "Select a saved set first.")
                    return
                ps = item.data(256)
                if not ps:
                    return

                if ps.pim_mode == "default":
                    self.rad_default.setChecked(True)
                    self.txt_pim.clear()
                else:
                    self.rad_custom.setChecked(True)
                    self.txt_pim.setPlainText(", ".join(str(v) for v in ps.values))

                self.txt_notes.setText(ps.notes or "")
                self.txt_set_name.setText(ps.nickname)

            def _rename_set(self) -> None:
                from PySide6.QtWidgets import QInputDialog, QMessageBox

                from portable_crypt_recovery.app.app_state import get_app_state
                from portable_crypt_recovery.services.builders.pim_builder import (
                    save_named_pim_set,
                )

                item = self.saved_list.currentItem()
                if not item:
                    QMessageBox.information(self, "Rename", "Select a set to rename.")
                    return
                ps = item.data(256)
                if not ps:
                    return

                new_name, ok = QInputDialog.getText(
                    self, "Rename Set", "New name:", text=ps.nickname
                )
                if not ok or not new_name.strip():
                    return

                ps.nickname = new_name.strip()
                try:
                    save_named_pim_set(get_app_state().workspace_root, ps)
                except Exception as exc:
                    QMessageBox.critical(self, "Rename Error", f"Could not rename PIM set:\n{exc}")
                    return
                self._refresh_saved_list()

            def _delete_set(self) -> None:
                from PySide6.QtWidgets import QMessageBox

                from portable_crypt_recovery.app.app_state import get_app_state
                from portable_crypt_recovery.services.builders.pim_builder import (
                    delete_named_pim_set,
                )

                item = self.saved_list.currentItem()
                if not item:
                    QMessageBox.warning(self, "Delete", "Select a set to delete.")
                    return
                ps = item.data(256)
                if not ps:
                    return

                reply = QMessageBox.question(
                    self, "Delete PIM Set",
                    f"Delete PIM set '{ps.nickname}'?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No,
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return

                delete_named_pim_set(get_app_state().workspace_root, ps.pim_set_id)
                self._refresh_saved_list()

        return _PimSetsView()
