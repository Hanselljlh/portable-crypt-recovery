"""Targets view — list and manage recovery targets."""

from __future__ import annotations


class TargetsView:  # pragma: no cover
    """List of targets with Add/View/Remove actions."""

    def __new__(cls):
        from PySide6.QtWidgets import (
            QHBoxLayout,
            QLabel,
            QListWidget,
            QListWidgetItem,
            QPushButton,
            QVBoxLayout,
            QWidget,
        )

        class _TargetsView(QWidget):
            def __init__(self) -> None:
                super().__init__()
                layout = QVBoxLayout(self)

                # Toolbar
                toolbar = QHBoxLayout()
                self.btn_add = QPushButton("Add Volume...")
                self.btn_view_headers = QPushButton("View Headers")
                self.btn_remove = QPushButton("Remove Target")
                toolbar.addWidget(self.btn_add)
                toolbar.addWidget(self.btn_view_headers)
                toolbar.addWidget(self.btn_remove)
                toolbar.addStretch()
                layout.addLayout(toolbar)

                # Target list
                self.target_list = QListWidget()
                layout.addWidget(self.target_list, 1)

                future_lbl = QLabel(
                    "Raw physical disk/drive/partition access: Future (not available in v1)"
                )
                future_lbl.setStyleSheet("color: gray; font-style: italic;")
                layout.addWidget(future_lbl)

                self.btn_add.clicked.connect(self._open_add_wizard)
                self.btn_view_headers.clicked.connect(self._view_headers)
                self.btn_remove.clicked.connect(self._remove_target)

                self._refresh_list()

            # ------------------------------------------------------------------
            # Add volume
            # ------------------------------------------------------------------

            def _open_add_wizard(self) -> None:
                from PySide6.QtWidgets import QMessageBox

                from portable_crypt_recovery.app.app_state import get_app_state
                from portable_crypt_recovery.ui.add_volume_wizard import AddVolumeWizard

                state = get_app_state()
                if not state.is_workspace_open():
                    QMessageBox.warning(
                        self,
                        "No Workspace",
                        "Open or create a workspace (Settings → Workspace) before adding targets.",
                    )
                    return

                wizard = AddVolumeWizard(parent=self)
                if wizard.exec() != 1 or wizard.result_data is None:
                    return

                self._process_wizard_result(wizard.result_data, state)

            def _process_wizard_result(self, result, state) -> None:
                from pathlib import Path

                from PySide6.QtWidgets import QMessageBox

                from portable_crypt_recovery.core.atomic_write import atomic_write_json
                from portable_crypt_recovery.core.ids import new_id
                from portable_crypt_recovery.core.timestamps import utc_now_iso
                from portable_crypt_recovery.models.header import Header
                from portable_crypt_recovery.models.target import Target
                from portable_crypt_recovery.services.headers import extraction, import_header
                from portable_crypt_recovery.services.headers.metadata import save_header_metadata
                from portable_crypt_recovery.workspace import cleanup_manifest

                source_path = Path(result.source_path)
                workspace_root = state.workspace_root
                now = utc_now_iso()

                # Create the target record
                target_id = new_id("target")
                target = Target(
                    target_id=target_id,
                    display_name=source_path.name,
                    original_path=str(source_path),
                    source_type=result.source_type,
                    container_family=result.container_family,
                    ownership_confirmed=True,
                    created_timestamp=now,
                    updated_timestamp=now,
                )

                # Extract or import headers
                extracted_headers: list[Header] = []
                errors: list[str] = []

                if result.source_type == "extracted_header":
                    # Import the file directly as a pre-extracted header
                    try:
                        header = import_header.import_header_file(
                            source=source_path,
                            workspace_root=workspace_root,
                            target_id=target_id,
                        )
                        extracted_headers.append(header)
                    except Exception as exc:
                        errors.append(f"Import failed: {exc}")
                else:
                    # Extract from the container/image
                    try:
                        candidates = extraction.extract_candidates(
                            source=source_path,
                            include_normal=result.extract_normal,
                            include_hidden=result.extract_hidden,
                            include_system=result.extract_system,
                        )
                    except Exception as exc:
                        QMessageBox.critical(
                            self,
                            "Extraction Failed",
                            f"Could not read source file:\n{exc}",
                        )
                        return

                    if not candidates:
                        QMessageBox.warning(
                            self,
                            "No Headers Extracted",
                            "No header candidates were selected or the file was too small.",
                        )
                        return

                    # Write each 512-byte candidate to headers/normalized/
                    for candidate in candidates:
                        header_id = new_id("header")
                        rel_path = f"headers/normalized/header_{header_id}.bin"
                        abs_path = workspace_root / rel_path
                        abs_path.parent.mkdir(parents=True, exist_ok=True)
                        abs_path.write_bytes(candidate.data)

                        header = Header(
                            header_id=header_id,
                            target_id=target_id,
                            source_type="extracted",
                            workspace_relative_path=rel_path,
                            size_bytes=len(candidate.data),
                            sha256=candidate.sha256,
                            extraction_timestamp=now,
                            candidate_type=candidate.candidate_type,
                        )
                        extracted_headers.append(header)

                if not extracted_headers and errors:
                    QMessageBox.critical(
                        self, "Error", "\n".join(errors)
                    )
                    return

                # Persist target to targets/targets.json
                targets_file = workspace_root / "targets" / "targets.json"
                try:
                    import json
                    existing = json.loads(targets_file.read_text(encoding="utf-8"))
                except Exception:
                    existing = {"schema_version": 1, "targets": []}
                existing["targets"].append(target.to_dict())
                atomic_write_json(targets_file, existing)

                # Persist each header's metadata + cleanup manifest entry
                for header in extracted_headers:
                    save_header_metadata(workspace_root, header)
                    cleanup_manifest.add_entry(
                        workspace_root,
                        relative_path=header.workspace_relative_path,
                        category="normalized-header",
                        description=f"{header.candidate_type} for target {target.display_name}",
                        created_by="targets_view",
                    )

                # Update in-memory counts
                state.target_count += 1
                state.header_count += len(extracted_headers)

                # Refresh list
                self._refresh_list()

                n = len(extracted_headers)
                err_note = "\n\nWarnings:\n" + "\n".join(errors) if errors else ""
                QMessageBox.information(
                    self,
                    "Volume Added",
                    f"Target '{target.display_name}' added.\n"
                    f"{n} header{'s' if n != 1 else ''} extracted and saved to workspace."
                    + err_note,
                )

            # ------------------------------------------------------------------
            # List management
            # ------------------------------------------------------------------

            def _refresh_list(self) -> None:
                import json

                from portable_crypt_recovery.app.app_state import get_app_state

                self.target_list.clear()
                state = get_app_state()
                if not state.is_workspace_open():
                    return

                targets_file = state.workspace_root / "targets" / "targets.json"
                if not targets_file.exists():
                    return

                try:
                    data = json.loads(targets_file.read_text(encoding="utf-8"))
                    for t in data.get("targets", []):
                        label = (
                            f"{t.get('display_name', 'Unknown')}  "
                            f"[{t.get('container_family', 'unknown')}]  "
                            f"— {t.get('source_type', '')}"
                        )
                        item = QListWidgetItem(label)
                        item.setData(256, t.get("target_id", ""))  # Qt.UserRole
                        self.target_list.addItem(item)
                except Exception:
                    pass

            # ------------------------------------------------------------------
            # View headers
            # ------------------------------------------------------------------

            def _view_headers(self) -> None:

                from PySide6.QtWidgets import QDialog, QLabel, QListWidget, QMessageBox, QVBoxLayout

                from portable_crypt_recovery.app.app_state import get_app_state
                from portable_crypt_recovery.services.headers.metadata import (
                    list_header_ids,
                    load_header_metadata,
                )

                item = self.target_list.currentItem()
                if item is None:
                    QMessageBox.information(self, "View Headers", "Select a target first.")
                    return

                state = get_app_state()
                target_id = item.data(256)

                # Load all headers for this target
                all_ids = list_header_ids(state.workspace_root)
                headers = []
                for hid in all_ids:
                    try:
                        h = load_header_metadata(state.workspace_root, hid)
                        if h.target_id == target_id:
                            headers.append(h)
                    except Exception:
                        pass

                if not headers:
                    QMessageBox.information(
                        self, "View Headers", "No headers found for this target."
                    )
                    return

                dlg = QDialog(self)
                dlg.setWindowTitle(f"Headers — {item.text()}")
                dlg.resize(560, 300)
                lay = QVBoxLayout(dlg)
                lst = QListWidget()
                for h in headers:
                    lst.addItem(
                        f"{h.candidate_type}  |  {h.workspace_relative_path}"
                        f"  |  sha256: {h.sha256[:16]}…"
                    )
                lay.addWidget(lst)
                lay.addWidget(QLabel(
                    "Headers are 512-byte normalized copies stored inside the workspace."
                ))
                dlg.exec()

            # ------------------------------------------------------------------
            # Remove target
            # ------------------------------------------------------------------

            def _remove_target(self) -> None:
                import json

                from PySide6.QtWidgets import QMessageBox

                from portable_crypt_recovery.app.app_state import get_app_state
                from portable_crypt_recovery.core.atomic_write import atomic_write_json

                item = self.target_list.currentItem()
                if item is None:
                    QMessageBox.warning(self, "Remove Target", "No target selected.")
                    return

                target = item.data(256)
                if target is None:
                    return

                display = target.get("display_name", target.get("target_id", "?"))
                reply = QMessageBox.question(
                    self,
                    "Remove Target",
                    f"Remove target '{display}'?\n\n"
                    "The target record will be deleted. Extracted header files in\n"
                    "headers/normalized/ and headers/metadata/ are NOT deleted\n"
                    "(use Workspace Cleanup to remove them).",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No,
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return

                state = get_app_state()
                if not state.is_workspace_open():
                    return

                targets_file = state.workspace_root / "targets" / "targets.json"
                try:
                    data = json.loads(targets_file.read_text(encoding="utf-8"))
                    tid = target.get("target_id", "")
                    data["targets"] = [
                        t for t in data.get("targets", [])
                        if t.get("target_id") != tid
                    ]
                    atomic_write_json(targets_file, data)
                    state.target_count = len(data["targets"])
                except Exception as exc:
                    QMessageBox.critical(self, "Remove Target", f"Failed to remove target:\n{exc}")
                    return

                self._refresh_targets()

        return _TargetsView()
