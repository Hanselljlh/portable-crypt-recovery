"""Jobs view — create job drafts and expand them to the queue."""

from __future__ import annotations


class JobsView:  # pragma: no cover
    """List of job drafts with New / Expand / Delete actions."""

    def __new__(cls):
        from PySide6.QtWidgets import (
            QHBoxLayout,
            QLabel,
            QListWidget,
            QPushButton,
            QVBoxLayout,
            QWidget,
        )

        class _JobsView(QWidget):
            def __init__(self) -> None:
                super().__init__()
                layout = QVBoxLayout(self)

                toolbar = QHBoxLayout()
                self.btn_new = QPushButton("New Job Draft...")
                self.btn_expand = QPushButton("Send to Queue")
                self.btn_delete = QPushButton("Delete Selected")
                self.btn_delete_all = QPushButton("Delete All")
                toolbar.addWidget(self.btn_new)
                toolbar.addWidget(self.btn_expand)
                toolbar.addWidget(self.btn_delete)
                toolbar.addWidget(self.btn_delete_all)
                toolbar.addStretch()
                layout.addLayout(toolbar)

                from PySide6.QtWidgets import QAbstractItemView
                self.job_list = QListWidget()
                self.job_list.setSelectionMode(
                    QAbstractItemView.SelectionMode.ExtendedSelection
                )
                layout.addWidget(self.job_list, 1)

                info = QLabel(
                    "Create a job draft by selecting a target, header, hash modes, PIM, "
                    "and password source. Then expand it to generate individual queue jobs."
                )
                info.setWordWrap(True)
                layout.addWidget(info)

                self.btn_new.clicked.connect(self._new_draft)
                self.btn_expand.clicked.connect(self._expand_to_queue)
                self.btn_delete.clicked.connect(self._delete_draft)
                self.btn_delete_all.clicked.connect(self._delete_all_drafts)

                self._refresh_list()

            # ------------------------------------------------------------------
            # New draft
            # ------------------------------------------------------------------

            def _new_draft(self) -> None:
                from PySide6.QtWidgets import QMessageBox

                from portable_crypt_recovery.app.app_state import get_app_state

                state = get_app_state()
                if not state.is_workspace_open():
                    QMessageBox.warning(
                        self,
                        "No Workspace",
                        "Open or create a workspace before creating job drafts.",
                    )
                    return

                dlg = _NewJobDraftDialog(parent=self, workspace_root=state.workspace_root)
                if dlg.exec() != 1 or dlg.draft is None:
                    return

                # Persist the draft
                self._save_draft(dlg.draft, state)
                self._refresh_list()
                QMessageBox.information(
                    self,
                    "Draft Saved",
                    f"Job draft '{dlg.draft.get('label', '')}' saved.\n"
                    "Select it and click 'Expand to Queue' to generate queue jobs.",
                )

            def _save_draft(self, draft: dict, state) -> None:
                import json

                from portable_crypt_recovery.core.atomic_write import atomic_write_json

                drafts_file = state.workspace_root / "jobs" / "drafts.json"
                drafts_file.parent.mkdir(parents=True, exist_ok=True)
                try:
                    existing = json.loads(drafts_file.read_text(encoding="utf-8"))
                except Exception:
                    existing = {"schema_version": 1, "drafts": []}
                existing["drafts"].append(draft)
                atomic_write_json(drafts_file, existing)

            # ------------------------------------------------------------------
            # Expand to queue
            # ------------------------------------------------------------------

            def _expand_to_queue(self) -> None:
                from PySide6.QtCore import Qt
                from PySide6.QtWidgets import QApplication, QMessageBox, QProgressDialog

                from portable_crypt_recovery.app.app_state import get_app_state

                selected = self.job_list.selectedItems()
                if not selected:
                    QMessageBox.information(self, "Send to Queue", "Select a draft first.")
                    return

                state = get_app_state()

                progress = QProgressDialog(
                    f"Building queue jobs for {len(selected)} draft(s)…", None, 0, 0, self
                )
                progress.setWindowTitle("Please Wait")
                progress.setWindowModality(Qt.WindowModality.WindowModal)
                progress.setMinimumDuration(0)
                progress.setValue(0)
                progress.show()
                QApplication.processEvents()

                total_count = 0
                errors: list[str] = []
                sent_drafts: list[tuple[dict, int]] = []
                for item in selected:
                    draft = item.data(256)
                    if not draft:
                        continue
                    try:
                        count = self._do_expand(draft, state)
                        total_count += count
                        sent_drafts.append((draft, count))
                    except Exception as exc:
                        errors.append(f"{draft.get('label', '?')}: {exc}")

                progress.close()

                if errors:
                    QMessageBox.warning(
                        self, "Some Expansions Failed",
                        "\n".join(errors[:5])
                    )

                state.job_count += total_count
                for draft, count in sent_drafts:
                    self._mark_draft_sent(draft, count, state)
                self._refresh_list()

                if total_count:
                    QMessageBox.information(
                        self,
                        "Jobs Added to Queue",
                        f"{total_count} job(s) from {len(sent_drafts)} draft(s) sent to the queue.\n\n"
                        "Switch to the Queue tab to see them.",
                    )

            def _do_expand(self, draft: dict, state) -> int:
                import json
                from pathlib import Path

                from portable_crypt_recovery.core.atomic_write import atomic_write_json
                from portable_crypt_recovery.models.queue_state import QueueState
                from portable_crypt_recovery.services.builders.final_job_expander import expand_jobs
                from portable_crypt_recovery.services.builders.hash_mode_builder import (
                    build_mode_set,
                )
                from portable_crypt_recovery.services.builders.keyfile_builder import (
                    build_keyfile_combinations,
                    import_keyfile,
                )
                from portable_crypt_recovery.services.builders.password_builder import (
                    build_manual_password_source,
                    build_wordlist_source,
                )
                from portable_crypt_recovery.services.builders.pim_builder import (
                    build_default_pim_set,
                    build_pim_set,
                )

                ws = state.workspace_root

                # Hash modes
                include_legacy = (draft.get("hash_mode_strategy") != "current_only")
                mode_set = build_mode_set(
                    family=draft.get("family", "unknown"),
                    candidate_type=draft.get("candidate_type", "normal_volume_header"),
                    target_id=draft["target_id"],
                    header_id=draft["header_id"],
                    include_legacy=include_legacy,
                )
                if not mode_set.entries:
                    raise ValueError("No hash modes available for this family/header combination.")

                # PIM
                pim_mode = draft.get("pim_mode", "default")
                if pim_mode == "custom":
                    pim_set = build_pim_set(
                        draft.get("pim_raw_input", ""),
                        workspace_root=ws,
                        force=False,
                    )
                else:
                    pim_set = build_default_pim_set()

                # Keyfiles
                keyfile_paths = draft.get("keyfile_paths", [])
                keyfile_sets = None
                if keyfile_paths:
                    entries = [import_keyfile(Path(p), ws) for p in keyfile_paths]
                    keyfile_sets = build_keyfile_combinations(entries, max_per_set=len(entries))

                # Password source
                pw_type = draft.get("password_source_type", "manual")
                if pw_type == "wordlist":
                    wl_path = Path(draft.get("password_wordlist_path", ""))
                    password_source = build_wordlist_source(wl_path, ws)
                else:
                    raw = draft.get("password_manual_text", "")
                    passwords = [line for line in raw.splitlines() if line.strip()]
                    if not passwords:
                        raise ValueError("Password list is empty.")
                    password_source = build_manual_password_source(passwords, ws)

                jobs = expand_jobs(
                    target_id=draft["target_id"],
                    header_id=draft["header_id"],
                    mode_set=mode_set,
                    pim_set=pim_set,
                    keyfile_sets=keyfile_sets,
                    password_source=password_source,
                    workspace_root=ws,
                )

                # Persist to queue/queue-state.json
                queue_file = ws / "queue" / "queue-state.json"
                queue_file.parent.mkdir(parents=True, exist_ok=True)
                try:
                    qs = QueueState.from_dict(
                        json.loads(queue_file.read_text(encoding="utf-8"))
                    )
                except Exception:
                    qs = QueueState()

                for job in jobs:
                    job.draft_id = draft.get("draft_id", "")
                    job.draft_label = draft.get("label", "")
                    qs.jobs[job.job_id] = job
                    qs.queue_order.append(job.job_id)

                atomic_write_json(queue_file, qs.to_dict())
                return len(jobs)

            def _mark_draft_sent(self, draft: dict, count: int, state) -> None:
                import json

                from portable_crypt_recovery.core.atomic_write import atomic_write_json
                drafts_file = state.workspace_root / "jobs" / "drafts.json"
                try:
                    data = json.loads(drafts_file.read_text(encoding="utf-8"))
                    for d in data.get("drafts", []):
                        if d.get("draft_id") == draft.get("draft_id"):
                            d["sent"] = True
                            d["sent_job_count"] = count
                    atomic_write_json(drafts_file, data)
                except Exception:
                    pass

            # ------------------------------------------------------------------
            # Delete draft
            # ------------------------------------------------------------------

            def _delete_draft(self) -> None:
                import json

                from PySide6.QtWidgets import QMessageBox

                from portable_crypt_recovery.app.app_state import get_app_state
                from portable_crypt_recovery.core.atomic_write import atomic_write_json

                selected = self.job_list.selectedItems()
                if not selected:
                    QMessageBox.warning(self, "Delete", "Select a draft first.")
                    return

                drafts = [it.data(256) for it in selected if it.data(256)]
                if not drafts:
                    return

                names_str = "\n".join(
                    f"  • {d.get('label', d.get('draft_id', '?'))}" for d in drafts
                )
                reply = QMessageBox.question(
                    self,
                    "Delete Draft(s)",
                    f"Delete {len(drafts)} draft(s)?\n{names_str}",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No,
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return

                ids_to_remove = {d.get("draft_id") for d in drafts}
                state = get_app_state()
                drafts_file = state.workspace_root / "jobs" / "drafts.json"
                try:
                    existing = json.loads(drafts_file.read_text(encoding="utf-8"))
                    existing["drafts"] = [
                        d for d in existing["drafts"]
                        if d.get("draft_id") not in ids_to_remove
                    ]
                    atomic_write_json(drafts_file, existing)
                except Exception:
                    pass
                self._refresh_list()

            def _delete_all_drafts(self) -> None:
                import json

                from PySide6.QtWidgets import QMessageBox

                from portable_crypt_recovery.app.app_state import get_app_state
                from portable_crypt_recovery.core.atomic_write import atomic_write_json

                state = get_app_state()
                if not state.is_workspace_open():
                    return

                drafts_file = state.workspace_root / "jobs" / "drafts.json"
                try:
                    data = json.loads(drafts_file.read_text(encoding="utf-8"))
                except Exception:
                    data = {"schema_version": 1, "drafts": []}

                count = len(data.get("drafts", []))
                if count == 0:
                    QMessageBox.information(self, "Delete All", "No drafts to delete.")
                    return

                reply = QMessageBox.question(
                    self,
                    "Delete All Drafts",
                    f"Delete all {count} draft(s)?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No,
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return

                try:
                    data["drafts"] = []
                    atomic_write_json(drafts_file, data)
                except Exception as exc:
                    QMessageBox.critical(self, "Delete All", f"Failed:\n{exc}")
                    return

                self._refresh_list()

            # ------------------------------------------------------------------
            # List
            # ------------------------------------------------------------------

            def _refresh_list(self) -> None:
                import json
                from pathlib import Path

                from PySide6.QtCore import QSize
                from PySide6.QtGui import QBrush, QColor
                from PySide6.QtWidgets import QListWidgetItem

                from portable_crypt_recovery.app.app_state import get_app_state

                self.job_list.clear()
                state = get_app_state()
                if not state.is_workspace_open():
                    return

                drafts_file = state.workspace_root / "jobs" / "drafts.json"
                if not drafts_file.exists():
                    return

                try:
                    data = json.loads(drafts_file.read_text(encoding="utf-8"))
                    for d in data.get("drafts", []):
                        sent = d.get("sent", False)
                        sent_count = d.get("sent_job_count", 0)
                        est_count = d.get("estimated_job_count", 0)

                        # --- Line 1: sent badge + name + family ---
                        if sent:
                            badge = f"✓ {sent_count} jobs sent  "
                        elif est_count:
                            badge = f"○ ~{est_count} jobs  "
                        else:
                            badge = "○ not sent  "
                        family = d.get("family", "unknown")
                        name = d.get("label", d.get("draft_id", "?"))
                        ctype = d.get("candidate_type", "normal_volume_header")
                        ctype_short = (
                            ctype.replace("_volume_header", "").replace("_", " ").strip()
                            or ctype
                        )
                        line1 = f"{badge}{name}  [{family}]  ·  {ctype_short}"

                        # --- Line 2: settings detail ---
                        strategy = (
                            "all modes"
                            if d.get("hash_mode_strategy") != "current_only"
                            else "current modes only"
                        )
                        pim = (
                            "default PIM"
                            if d.get("pim_mode") == "default"
                            else f"PIM: {d.get('pim_raw_input', '')}"
                        )
                        pw_type = d.get("password_source_type", "manual")
                        if pw_type == "wordlist":
                            wl = d.get("password_wordlist_path", "")
                            pw_detail = f"wordlist: {Path(wl).name}" if wl else "wordlist: (none)"
                        else:
                            raw = d.get("password_manual_text", "")
                            n = len([ln for ln in raw.splitlines() if ln.strip()])
                            pw_detail = f"manual: {n} password{'s' if n != 1 else ''}"
                        kf = d.get("keyfile_paths", [])
                        kf_detail = f"  ·  {len(kf)} keyfile{'s' if len(kf) != 1 else ''}"
                        line2 = f"    {strategy}  ·  {pim}  ·  {pw_detail}{kf_detail}"

                        item = QListWidgetItem(f"{line1}\n{line2}")
                        item.setData(256, d)
                        item.setSizeHint(QSize(0, 48))
                        if sent:
                            item.setForeground(QBrush(QColor("#8888aa")))
                        self.job_list.addItem(item)
                except Exception:
                    pass

        return _JobsView()


# ---------------------------------------------------------------------------
# New Job Draft dialog (module-level so it can be referenced)
# ---------------------------------------------------------------------------

class _NewJobDraftDialog:  # pragma: no cover
    def __new__(cls, parent=None, workspace_root=None):
        from PySide6.QtWidgets import (
            QComboBox,
            QDialog,
            QDialogButtonBox,
            QFileDialog,
            QGroupBox,
            QHBoxLayout,
            QLabel,
            QLineEdit,
            QListWidget,
            QPlainTextEdit,
            QPushButton,
            QRadioButton,
            QVBoxLayout,
        )

        class _Dlg(QDialog):
            def __init__(self, parent=None, workspace_root=None) -> None:
                super().__init__(parent)
                self.setWindowTitle("New Job Draft")
                self.resize(680, 700)
                self._workspace_root = workspace_root
                self.draft = None

                layout = QVBoxLayout(self)

                # Target + Header selection
                tgt_group = QGroupBox("Target & Header")
                tgt_layout = QVBoxLayout(tgt_group)
                row1 = QHBoxLayout()
                row1.addWidget(QLabel("Target:"))
                self.cmb_target = QComboBox()
                row1.addWidget(self.cmb_target, 1)
                tgt_layout.addLayout(row1)
                row2 = QHBoxLayout()
                row2.addWidget(QLabel("Header:"))
                self.cmb_header = QComboBox()
                row2.addWidget(self.cmb_header, 1)
                tgt_layout.addLayout(row2)
                layout.addWidget(tgt_group)

                # Hash modes
                mode_group = QGroupBox("Hash Mode Strategy")
                mode_layout = QVBoxLayout(mode_group)
                self.rad_all = QRadioButton("Try all valid modes (current + legacy) — recommended")
                self.rad_current = QRadioButton("Current modes only (no legacy)")
                self.rad_all.setChecked(True)
                mode_layout.addWidget(self.rad_all)
                mode_layout.addWidget(self.rad_current)
                layout.addWidget(mode_group)

                # PIM
                pim_group = QGroupBox("PIM (Personal Iterations Multiplier)")
                pim_layout = QVBoxLayout(pim_group)
                self.rad_pim_default = QRadioButton("Use default PIM — recommended")
                self.rad_pim_custom = QRadioButton("Custom PIM values:")
                self.rad_pim_default.setChecked(True)
                pim_layout.addWidget(self.rad_pim_default)
                pim_row = QHBoxLayout()
                pim_row.addWidget(self.rad_pim_custom)
                self.txt_pim = QLineEdit()
                self.txt_pim.setPlaceholderText("e.g. 485, 500-510")
                self.txt_pim.setEnabled(False)
                pim_row.addWidget(self.txt_pim, 1)
                pim_layout.addLayout(pim_row)
                pim_layout.addWidget(QLabel(
                    "Default PIM is correct for standard volumes. Only set custom if you know the PIM."
                ))
                layout.addWidget(pim_group)

                # Password source
                pw_group = QGroupBox("Password Source")
                pw_layout = QVBoxLayout(pw_group)
                self.rad_pw_manual = QRadioButton("Manual password list (one per line):")
                self.rad_pw_wordlist = QRadioButton("External wordlist file:")
                self.rad_pw_manual.setChecked(True)
                pw_layout.addWidget(self.rad_pw_manual)
                self.txt_passwords = QPlainTextEdit()
                self.txt_passwords.setPlaceholderText("Enter one password per line")
                self.txt_passwords.setMaximumHeight(120)
                pw_layout.addWidget(self.txt_passwords)
                pw_layout.addWidget(self.rad_pw_wordlist)
                wl_row = QHBoxLayout()
                self.txt_wordlist = QLineEdit()
                self.txt_wordlist.setPlaceholderText("Path to wordlist file...")
                self.txt_wordlist.setEnabled(False)
                btn_browse_wl = QPushButton("Browse...")
                btn_browse_wl.clicked.connect(self._browse_wordlist)
                wl_row.addWidget(self.txt_wordlist)
                wl_row.addWidget(btn_browse_wl)
                pw_layout.addLayout(wl_row)
                layout.addWidget(pw_group)

                # Keyfiles (optional)
                kf_group = QGroupBox("Keyfiles (optional)")
                kf_layout = QVBoxLayout(kf_group)
                self.kf_list = QListWidget()
                self.kf_list.setMaximumHeight(80)
                kf_layout.addWidget(self.kf_list)
                kf_btn_row = QHBoxLayout()
                btn_add_kf = QPushButton("Add Keyfile...")
                btn_remove_kf = QPushButton("Remove Selected")
                btn_add_kf.clicked.connect(self._add_keyfile)
                btn_remove_kf.clicked.connect(self._remove_keyfile)
                kf_btn_row.addWidget(btn_add_kf)
                kf_btn_row.addWidget(btn_remove_kf)
                kf_btn_row.addStretch()
                kf_layout.addLayout(kf_btn_row)
                layout.addWidget(kf_group)

                # Buttons
                buttons = QDialogButtonBox(
                    QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
                )
                buttons.accepted.connect(self._on_accept)
                buttons.rejected.connect(self.reject)
                layout.addWidget(buttons)

                # Wire signals
                self.rad_pim_custom.toggled.connect(
                    lambda checked: self.txt_pim.setEnabled(checked)
                )
                self.rad_pw_wordlist.toggled.connect(self._on_pw_type_changed)
                self.cmb_target.currentIndexChanged.connect(self._on_target_changed)

                self._load_targets()

            def _load_targets(self) -> None:
                import json
                self.cmb_target.clear()
                if not self._workspace_root:
                    return
                targets_file = self._workspace_root / "targets" / "targets.json"
                try:
                    data = json.loads(targets_file.read_text(encoding="utf-8"))
                    for t in data.get("targets", []):
                        label = f"{t.get('display_name', '?')} [{t.get('container_family', 'unknown')}]"
                        self.cmb_target.addItem(label, userData=t)
                except Exception:
                    pass
                self._on_target_changed(0)

            def _on_target_changed(self, _index: int) -> None:
                self.cmb_header.clear()
                tgt = self.cmb_target.currentData()
                if not tgt or not self._workspace_root:
                    return
                target_id = tgt.get("target_id", "")
                from portable_crypt_recovery.services.headers.metadata import (
                    list_header_ids,
                    load_header_metadata,
                )
                for hid in list_header_ids(self._workspace_root):
                    try:
                        h = load_header_metadata(self._workspace_root, hid)
                        if h.target_id == target_id:
                            self.cmb_header.addItem(
                                f"{h.candidate_type}  |  {h.header_id[:8]}",
                                userData=h,
                            )
                    except Exception:
                        pass

            def _on_pw_type_changed(self, checked: bool) -> None:
                self.txt_passwords.setEnabled(not checked)
                self.txt_wordlist.setEnabled(checked)

            def _browse_wordlist(self) -> None:
                path, _ = QFileDialog.getOpenFileName(
                    self, "Select Wordlist File", "", "Text Files (*.txt);;All Files (*.*)"
                )
                if path:
                    self.txt_wordlist.setText(path)

            def _add_keyfile(self) -> None:
                from PySide6.QtWidgets import QListWidgetItem
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

            def _on_accept(self) -> None:
                from PySide6.QtWidgets import QMessageBox

                from portable_crypt_recovery.core.ids import new_id
                from portable_crypt_recovery.core.timestamps import utc_now_iso

                tgt = self.cmb_target.currentData()
                if not tgt:
                    QMessageBox.warning(self, "Missing Target", "Please select a target.")
                    return
                header_obj = self.cmb_header.currentData()
                if not header_obj:
                    QMessageBox.warning(self, "Missing Header", "No headers available for this target.")
                    return

                pw_type = "wordlist" if self.rad_pw_wordlist.isChecked() else "manual"
                if pw_type == "wordlist":
                    if not self.txt_wordlist.text().strip():
                        QMessageBox.warning(self, "No Wordlist", "Please select a wordlist file.")
                        return
                else:
                    if not self.txt_passwords.toPlainText().strip():
                        QMessageBox.warning(self, "No Passwords", "Please enter at least one password.")
                        return

                keyfile_paths = [
                    self.kf_list.item(i).data(256)
                    for i in range(self.kf_list.count())
                ]

                target_name = tgt.get("display_name", "?")
                candidate_type = header_obj.candidate_type if hasattr(header_obj, "candidate_type") else "normal_volume_header"

                # Estimate job count (mode × pim × kf combos)
                estimated_job_count = 0
                try:
                    from portable_crypt_recovery.services.builders.hash_mode_builder import (
                        build_mode_set,
                    )
                    from portable_crypt_recovery.services.builders.pim_builder import (
                        build_default_pim_set,
                        build_pim_set,
                    )
                    mode_set = build_mode_set(
                        family=tgt.get("container_family", "unknown"),
                        candidate_type=candidate_type,
                        target_id=tgt["target_id"],
                        header_id=header_obj.header_id,
                        include_legacy=not self.rad_current.isChecked(),
                    )
                    mode_count = len(mode_set.entries)
                    if self.rad_pim_custom.isChecked():
                        pim_set = build_pim_set(
                            self.txt_pim.text().strip(),
                            workspace_root=self._workspace_root,
                            force=False,
                        )
                        pim_count = max(len(pim_set.values), 1)
                    else:
                        pim_set = build_default_pim_set()
                        # default PIM = 1 implicit job per mode
                        pim_count = 1
                    n_kf = len(keyfile_paths)
                    kf_count = max(1, (2 ** n_kf) - 1) if n_kf > 0 else 1
                    estimated_job_count = mode_count * pim_count * kf_count
                except Exception:
                    estimated_job_count = 0

                self.draft = {
                    "draft_id": new_id("draft"),
                    "label": f"{target_name} — {candidate_type}",
                    "target_id": tgt["target_id"],
                    "header_id": header_obj.header_id,
                    "family": tgt.get("container_family", "unknown"),
                    "candidate_type": candidate_type,
                    "hash_mode_strategy": "current_only" if self.rad_current.isChecked() else "all",
                    "pim_mode": "custom" if self.rad_pim_custom.isChecked() else "default",
                    "pim_raw_input": self.txt_pim.text().strip(),
                    "password_source_type": pw_type,
                    "password_manual_text": self.txt_passwords.toPlainText(),
                    "password_wordlist_path": self.txt_wordlist.text().strip(),
                    "keyfile_paths": keyfile_paths,
                    "estimated_job_count": estimated_job_count,
                    "created_timestamp": utc_now_iso(),
                }
                self.accept()

        return _Dlg(parent, workspace_root)
