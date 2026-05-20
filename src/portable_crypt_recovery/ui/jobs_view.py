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
                self.btn_edit = QPushButton("Edit...")
                self.btn_duplicate = QPushButton("Duplicate")
                self.btn_expand = QPushButton("Send to Queue")
                self.btn_delete = QPushButton("Delete Selected")
                self.btn_delete_all = QPushButton("Delete All")
                for _b in [
                    self.btn_new, self.btn_edit, self.btn_duplicate,
                    self.btn_expand, self.btn_delete, self.btn_delete_all,
                ]:
                    toolbar.addWidget(_b)
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
                self.btn_edit.clicked.connect(self._edit_draft)
                self.btn_duplicate.clicked.connect(self._duplicate_draft)
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

            # ------------------------------------------------------------------
            # Duplicate draft
            # ------------------------------------------------------------------

            def _duplicate_draft(self) -> None:
                import copy

                from PySide6.QtWidgets import QMessageBox

                from portable_crypt_recovery.app.app_state import get_app_state
                from portable_crypt_recovery.core.ids import new_id
                from portable_crypt_recovery.core.timestamps import utc_now_iso

                selected = self.job_list.selectedItems()
                if not selected:
                    QMessageBox.information(self, "Duplicate", "Select a draft first.")
                    return
                if len(selected) > 1:
                    QMessageBox.information(
                        self, "Duplicate", "Select one draft to duplicate."
                    )
                    return
                draft = selected[0].data(256)
                if not draft:
                    return

                new_draft = copy.deepcopy(draft)
                new_draft["draft_id"] = new_id("draft")
                new_draft["label"] = draft.get("label", "draft") + " (copy)"
                new_draft["created_timestamp"] = utc_now_iso()
                new_draft.pop("sent", None)
                new_draft.pop("sent_job_count", None)

                state = get_app_state()
                self._save_draft(new_draft, state)
                self._refresh_list()

            # ------------------------------------------------------------------
            # Edit draft
            # ------------------------------------------------------------------

            def _edit_draft(self) -> None:
                from PySide6.QtWidgets import QMessageBox

                from portable_crypt_recovery.app.app_state import get_app_state

                selected = self.job_list.selectedItems()
                if not selected:
                    QMessageBox.information(self, "Edit", "Select a draft to edit.")
                    return
                if len(selected) > 1:
                    QMessageBox.information(
                        self, "Edit", "Select one draft to edit."
                    )
                    return
                draft = selected[0].data(256)
                if not draft:
                    return

                state = get_app_state()
                dlg = _NewJobDraftDialog(
                    parent=self,
                    workspace_root=state.workspace_root,
                    draft_data=draft,
                )
                if dlg.exec() != 1 or dlg.draft is None:
                    return

                # Preserve sent status when updating a sent draft
                if draft.get("sent"):
                    dlg.draft.setdefault("sent", True)
                    dlg.draft.setdefault("sent_job_count", draft.get("sent_job_count", 0))

                self._replace_draft(draft["draft_id"], dlg.draft, state)
                self._refresh_list()

            def _replace_draft(self, old_draft_id: str, new_draft: dict, state) -> None:
                import json

                from portable_crypt_recovery.core.atomic_write import atomic_write_json

                drafts_file = state.workspace_root / "jobs" / "drafts.json"
                try:
                    data = json.loads(drafts_file.read_text(encoding="utf-8"))
                    drafts = data.get("drafts", [])
                    replaced = False
                    for i, d in enumerate(drafts):
                        if d.get("draft_id") == old_draft_id:
                            drafts[i] = new_draft
                            replaced = True
                            break
                    if not replaced:
                        drafts.append(new_draft)
                    data["drafts"] = drafts
                    atomic_write_json(drafts_file, data)
                except Exception:
                    pass

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

                from portable_crypt_recovery.services.headers.metadata import load_header_metadata

                # Support both new multi-header drafts and old single-header drafts
                header_ids: list[str] = draft.get("header_ids") or [draft.get("header_id", "")]
                header_ids = [h for h in header_ids if h]  # strip empties
                if not header_ids:
                    raise ValueError("Draft has no header IDs.")

                include_legacy = (draft.get("hash_mode_strategy") != "current_only")

                # PIM (shared across all headers)
                pim_mode = draft.get("pim_mode", "default")
                if pim_mode == "custom":
                    pim_set = build_pim_set(
                        draft.get("pim_raw_input", ""),
                        workspace_root=ws,
                        force=False,
                    )
                else:
                    pim_set = build_default_pim_set()

                # Keyfiles (shared across all headers)
                keyfile_paths = draft.get("keyfile_paths", [])
                keyfile_sets = None
                if keyfile_paths:
                    entries = [import_keyfile(Path(p), ws) for p in keyfile_paths]
                    keyfile_sets = build_keyfile_combinations(entries, max_per_set=len(entries))

                # Password source (shared across all headers)
                pw_type = draft.get("password_source_type", "manual")
                if pw_type in ("wordlist", "workspace_wordlist"):
                    wl_path = Path(draft.get("password_wordlist_path", ""))
                    password_source = build_wordlist_source(wl_path, ws)
                else:
                    raw = draft.get("password_manual_text", "")
                    passwords = [line for line in raw.splitlines() if line.strip()]
                    if not passwords:
                        raise ValueError("Password list is empty.")
                    password_source = build_manual_password_source(passwords, ws)

                # Load queue state once
                queue_file = ws / "queue" / "queue-state.json"
                queue_file.parent.mkdir(parents=True, exist_ok=True)
                try:
                    qs = QueueState.from_dict(
                        json.loads(queue_file.read_text(encoding="utf-8"))
                    )
                except Exception:
                    qs = QueueState()

                all_jobs: list = []
                for header_id in header_ids:
                    # Resolve candidate_type and per-header hints from stored metadata
                    header_meta = None
                    try:
                        header_meta = load_header_metadata(ws, header_id)
                        candidate_type = header_meta.candidate_type
                    except Exception:
                        candidate_type = draft.get("candidate_type", "normal_volume_header")

                    mode_set = build_mode_set(
                        family=draft.get("family", "unknown"),
                        candidate_type=candidate_type,
                        target_id=draft["target_id"],
                        header_id=header_id,
                        include_legacy=include_legacy,
                    )
                    # Filter to user-selected modes when strategy is "specific"
                    if draft.get("hash_mode_strategy") == "specific":
                        specific_nums = set(draft.get("hash_mode_numbers", []))
                        mode_set.entries = [
                            e for e in mode_set.entries if e.mode in specific_nums
                        ]
                    if not mode_set.entries:
                        continue  # skip headers with no valid modes

                    # Build the ordered list of keyfile iterations to expand.
                    # When keyfiles are present, always try without any keyfile
                    # first — it's the cheapest way to rule out "no keyfile needed".
                    # Then follow with every keyfile combination.
                    kf_iterations: list = [None]  # no-keyfile attempt always first
                    if keyfile_sets:
                        kf_iterations += list(keyfile_sets)

                    for kf_iter in kf_iterations:
                        # Persist the KeyfileSet JSON so command_builder and
                        # cracked_package can resolve it at runtime.
                        if kf_iter is not None:
                            kf_list_dir = ws / "generated" / "keyfile-lists"
                            kf_list_dir.mkdir(parents=True, exist_ok=True)
                            kf_json_path = kf_list_dir / f"{kf_iter.set_id}.json"
                            if not kf_json_path.exists():
                                atomic_write_json(kf_json_path, kf_iter.to_dict())

                        iter_sets = None if kf_iter is None else [kf_iter]
                        jobs = expand_jobs(
                            target_id=draft["target_id"],
                            header_id=header_id,
                            mode_set=mode_set,
                            pim_set=pim_set,
                            keyfile_sets=iter_sets,
                            password_source=password_source,
                            workspace_root=ws,
                        )

                        for task in jobs:
                            task.draft_id = draft.get("draft_id", "")
                            task.draft_label = draft.get("label", "")
                            qs.tasks[task.task_id] = task
                            qs.task_order.append(task.task_id)
                            all_jobs.append(task)

                if not all_jobs:
                    raise ValueError("No hash modes available for any selected header.")

                # Optional: collapse adjacent PIM tasks into range tasks
                if state.hashcat_setup.batch_adjacent_pims:
                    from portable_crypt_recovery.services.builders.pim_range_grouper import (
                        group_adjacent_pim_ranges,
                    )
                    all_jobs = group_adjacent_pim_ranges(all_jobs)
                    # Re-register ranged tasks in queue state (they replaced originals)
                    qs.tasks = {}
                    qs.task_order = []
                    for task in all_jobs:
                        qs.tasks[task.task_id] = task
                        qs.task_order.append(task.task_id)

                atomic_write_json(queue_file, qs.to_dict())
                return len(all_jobs)

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
                        header_ids_list = d.get("header_ids") or [d.get("header_id", "")]
                        n_headers = len([h for h in header_ids_list if h])
                        if n_headers > 1:
                            hdr_badge = f"{n_headers} headers"
                        else:
                            ctype = d.get("candidate_type", "normal_volume_header")
                            hdr_badge = (
                                ctype.replace("_volume_header", "").replace("_", " ").strip()
                                or ctype
                            )
                        line1 = f"{badge}{name}  [{family}]  ·  {hdr_badge}"

                        # --- Line 2: settings detail ---
                        _hms = d.get("hash_mode_strategy", "all")
                        if _hms == "specific":
                            _n = len(d.get("hash_mode_numbers", []))
                            strategy = f"{_n} specific mode{'s' if _n != 1 else ''}"
                        elif _hms == "current_only":
                            strategy = "current modes only"
                        else:
                            strategy = "all modes"
                        pim = (
                            "default PIM"
                            if d.get("pim_mode") == "default"
                            else f"PIM: {d.get('pim_raw_input', '')}"
                        )
                        pw_type = d.get("password_source_type", "manual")
                        if pw_type == "wordlist":
                            wl = d.get("password_wordlist_path", "")
                            pw_detail = f"wordlist: {Path(wl).name}" if wl else "wordlist: (none)"
                        elif pw_type == "workspace_wordlist":
                            wl = d.get("password_wordlist_path", "")
                            if wl:
                                from portable_crypt_recovery.services.builders.password_builder import (  # noqa: PLC0415
                                    load_wordlist_nickname,
                                )
                                _nick = load_wordlist_nickname(Path(wl))
                                pw_detail = f"pw-builder: {_nick or Path(wl).name}"
                            else:
                                pw_detail = "pw-builder: (none)"
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
    def __new__(cls, parent=None, workspace_root=None, draft_data=None):
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
            QScrollArea,
            QVBoxLayout,
            QWidget,
        )

        class _Dlg(QDialog):
            def __init__(self, parent=None, workspace_root=None, draft_data=None) -> None:
                super().__init__(parent)
                self._workspace_root = workspace_root
                self.draft = None
                is_edit = draft_data is not None
                self._is_new_draft = not is_edit
                self.setWindowTitle("Edit Job Draft" if is_edit else "New Job Draft")
                self.resize(720, 860)

                outer = QVBoxLayout(self)
                scroll = QScrollArea()
                scroll.setWidgetResizable(True)
                _container = QWidget()
                layout = QVBoxLayout(_container)
                scroll.setWidget(_container)
                outer.addWidget(scroll, 1)

                # Target + Header selection
                tgt_group = QGroupBox("Target & Headers")
                tgt_layout = QVBoxLayout(tgt_group)
                row1 = QHBoxLayout()
                row1.addWidget(QLabel("Target:"))
                self.cmb_target = QComboBox()
                row1.addWidget(self.cmb_target, 1)
                tgt_layout.addLayout(row1)
                tgt_layout.addWidget(QLabel(
                    "Headers (all selected by default — deselect any you want to skip):"
                ))
                from PySide6.QtWidgets import QAbstractItemView
                self.lst_headers = QListWidget()
                self.lst_headers.setSelectionMode(
                    QAbstractItemView.SelectionMode.ExtendedSelection
                )
                self.lst_headers.setMaximumHeight(100)
                tgt_layout.addWidget(self.lst_headers)
                layout.addWidget(tgt_group)

                # Hash modes
                mode_group = QGroupBox("Hash Mode Strategy")
                mode_layout = QVBoxLayout(mode_group)

                # Load saved hash set shortcut
                hs_pick_row = QHBoxLayout()
                self._btn_load_hash_set = QPushButton("Load Saved Hash Set →")
                hs_pick_row.addWidget(self._btn_load_hash_set)
                hs_pick_row.addStretch()
                mode_layout.addLayout(hs_pick_row)

                self._lbl_hash_hint = QLabel()
                self._lbl_hash_hint.setStyleSheet(
                    "color: #66aaff; font-size: 11px; padding: 2px 0;"
                )
                self._lbl_hash_hint.setWordWrap(True)
                self._lbl_hash_hint.setVisible(False)
                mode_layout.addWidget(self._lbl_hash_hint)

                self.rad_all = QRadioButton("Try all valid modes (current + legacy) — recommended")
                self.rad_current = QRadioButton("Current modes only (no legacy)")
                self.rad_specific = QRadioButton("Select specific modes:")
                self.rad_all.setChecked(True)
                mode_layout.addWidget(self.rad_all)
                mode_layout.addWidget(self.rad_current)
                mode_layout.addWidget(self.rad_specific)
                # Checklist for specific-mode selection (hidden until rad_specific is chosen)
                self.mode_checklist = QListWidget()
                self.mode_checklist.setMinimumHeight(360)
                self.mode_checklist.setVisible(False)
                mode_layout.addWidget(self.mode_checklist)
                mode_btn_row = QHBoxLayout()
                self.btn_modes_all = QPushButton("Check All")
                self.btn_modes_none = QPushButton("Uncheck All")
                self.btn_modes_vc = QPushButton("VeraCrypt Only")
                self.btn_modes_tc = QPushButton("TrueCrypt Only")
                self.btn_cascade_1 = QPushButton("Single Cipher")
                self.btn_cascade_2 = QPushButton("Cascade ×2")
                self.btn_cascade_3 = QPushButton("Cascade ×3")
                self._mode_btns = [
                    self.btn_modes_all, self.btn_modes_none,
                    self.btn_modes_vc, self.btn_modes_tc,
                    self.btn_cascade_1, self.btn_cascade_2, self.btn_cascade_3,
                ]
                for _b in self._mode_btns:
                    mode_btn_row.addWidget(_b)
                    _b.setVisible(False)
                mode_btn_row.addStretch()
                mode_layout.addLayout(mode_btn_row)
                layout.addWidget(mode_group)

                # PIM
                pim_group = QGroupBox("PIM (Personal Iterations Multiplier)")
                pim_layout = QVBoxLayout(pim_group)

                # Load saved PIM set shortcut
                pim_pick_row = QHBoxLayout()
                self._btn_load_pim_set = QPushButton("Load Saved PIM Set →")
                pim_pick_row.addWidget(self._btn_load_pim_set)
                pim_pick_row.addStretch()
                pim_layout.addLayout(pim_pick_row)

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
                self.rad_pw_workspace = QRadioButton("Workspace wordlist (Password Builder):")
                pw_layout.addWidget(self.rad_pw_workspace)
                ws_row = QHBoxLayout()
                self.cmb_ws_wordlist = QComboBox()
                self.cmb_ws_wordlist.setEnabled(False)
                self.cmb_ws_wordlist.setMinimumWidth(260)
                self._btn_refresh_ws = QPushButton("Refresh")
                self._btn_refresh_ws.clicked.connect(self._refresh_workspace_wordlists)
                ws_row.addWidget(self.cmb_ws_wordlist, 1)
                ws_row.addWidget(self._btn_refresh_ws)
                pw_layout.addLayout(ws_row)
                layout.addWidget(pw_group)

                # Keyfiles (optional)
                kf_group = QGroupBox("Keyfiles (optional)")
                kf_layout = QVBoxLayout(kf_group)

                # Load saved keyfile set shortcut
                kf_pick_row = QHBoxLayout()
                self._btn_load_kf_set = QPushButton("Load Saved Keyfile Set →")
                kf_pick_row.addWidget(self._btn_load_kf_set)
                kf_pick_row.addStretch()
                kf_layout.addLayout(kf_pick_row)

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

                # Buttons (outside scroll area so they're always visible)
                buttons = QDialogButtonBox(
                    QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
                )
                buttons.accepted.connect(self._on_accept)
                buttons.rejected.connect(self.reject)
                outer.addWidget(buttons)

                # Wire signals
                self.rad_pim_custom.toggled.connect(
                    lambda checked: self.txt_pim.setEnabled(checked)
                )
                self.rad_pw_manual.toggled.connect(lambda _: self._on_pw_type_changed())
                self.rad_pw_wordlist.toggled.connect(lambda _: self._on_pw_type_changed())
                self.rad_pw_workspace.toggled.connect(lambda _: self._on_pw_type_changed())
                self.rad_specific.toggled.connect(self._on_mode_strategy_changed)
                self.btn_modes_all.clicked.connect(lambda: self._set_all_mode_checks(True))
                self.btn_modes_none.clicked.connect(lambda: self._set_all_mode_checks(False))
                self.btn_modes_vc.clicked.connect(lambda: self._set_family_mode_checks("veracrypt"))
                self.btn_modes_tc.clicked.connect(lambda: self._set_family_mode_checks("truecrypt"))
                self.btn_cascade_1.clicked.connect(lambda: self._set_cascade_mode_checks(1))
                self.btn_cascade_2.clicked.connect(lambda: self._set_cascade_mode_checks(2))
                self.btn_cascade_3.clicked.connect(lambda: self._set_cascade_mode_checks(3))
                self.cmb_target.currentIndexChanged.connect(self._on_target_changed)
                self._btn_load_hash_set.clicked.connect(self._load_hash_set_picker)
                self._btn_load_pim_set.clicked.connect(self._load_pim_set_picker)
                self._btn_load_kf_set.clicked.connect(self._load_kf_set_picker)

                self._load_targets()
                if draft_data:
                    self._prefill(draft_data)

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
                from PySide6.QtWidgets import QListWidgetItem

                self.lst_headers.clear()
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
                            ctype_short = (
                                h.candidate_type
                                .replace("_volume_header", "")
                                .replace("_", " ")
                                .strip()
                                or h.candidate_type
                            )
                            item = QListWidgetItem(
                                f"{ctype_short}  |  {h.header_id[:8]}"
                            )
                            item.setData(256, h)
                            self.lst_headers.addItem(item)
                    except Exception:
                        pass
                # Default: select all headers
                self.lst_headers.selectAll()
                # Rebuild specific-mode checklist when target changes
                if hasattr(self, "rad_specific") and self.rad_specific.isChecked():
                    self._rebuild_mode_checklist()
                # Auto-apply wizard-generated hash set for new drafts
                if getattr(self, "_is_new_draft", False):
                    self._auto_apply_suggested_hash_set()

            def _auto_apply_suggested_hash_set(self) -> None:
                """Pre-select wizard-generated hash set for the current target headers."""
                from PySide6.QtCore import Qt

                from portable_crypt_recovery.services.builders.hash_mode_builder import (
                    load_named_hash_set,
                )

                # Collect a suggested_mode_set_id from loaded headers
                suggested_id = ""
                for i in range(self.lst_headers.count()):
                    h = self.lst_headers.item(i).data(256)
                    if h:
                        sid = getattr(h, "suggested_mode_set_id", "")
                        if sid:
                            suggested_id = sid
                            break

                if not suggested_id or not self._workspace_root:
                    # No suggested set — reset to "all modes" and hide hint label
                    self.rad_all.setChecked(True)
                    self._lbl_hash_hint.setVisible(False)
                    return

                hms = load_named_hash_set(self._workspace_root, suggested_id)
                if not hms:
                    self.rad_all.setChecked(True)
                    self._lbl_hash_hint.setVisible(False)
                    return

                # Switch to specific mode, rebuild checklist, apply set
                self.rad_specific.setChecked(True)
                self._rebuild_mode_checklist()
                mode_nums = {e.mode for e in hms.entries}
                for i in range(self.mode_checklist.count()):
                    entry = self.mode_checklist.item(i).data(256)
                    self.mode_checklist.item(i).setCheckState(
                        Qt.CheckState.Checked
                        if (entry and entry.mode in mode_nums)
                        else Qt.CheckState.Unchecked
                    )

                n = len(hms.entries)
                self._lbl_hash_hint.setText(
                    f"✓ {n} mode{'s' if n != 1 else ''} pre-selected from wizard hints"
                    f" ({hms.nickname})  —  change below to override."
                )
                self._lbl_hash_hint.setVisible(True)

            def _on_mode_strategy_changed(self, checked: bool) -> None:
                """Show or hide the specific-mode checklist."""
                self.mode_checklist.setVisible(checked)
                for _b in self._mode_btns:
                    _b.setVisible(checked)
                if checked:
                    self._rebuild_mode_checklist()

            def _rebuild_mode_checklist(self) -> None:
                """Populate the mode checklist from the current target + all headers."""
                from PySide6.QtCore import Qt
                from PySide6.QtWidgets import QListWidgetItem

                from portable_crypt_recovery.services.builders.hash_mode_builder import (
                    build_mode_set,
                )

                self.mode_checklist.clear()
                tgt = self.cmb_target.currentData()
                if not tgt:
                    return

                selected_items = self.lst_headers.selectedItems()
                header_items = selected_items if selected_items else [
                    self.lst_headers.item(i) for i in range(self.lst_headers.count())
                ]

                seen: set[int] = set()
                for hi in header_items:
                    h = hi.data(256) if hi else None
                    if not h:
                        continue
                    ctype = getattr(h, "candidate_type", "normal_volume_header")
                    ms = build_mode_set(
                        family=tgt.get("container_family", "unknown"),
                        candidate_type=ctype,
                        target_id=tgt.get("target_id", ""),
                        header_id=h.header_id,
                        include_legacy=True,
                    )
                    for entry in ms.entries:
                        if entry.mode not in seen:
                            seen.add(entry.mode)
                            legacy_tag = "  [legacy]" if entry.is_legacy else ""
                            label = f"{entry.mode:>6}  {entry.label}{legacy_tag}"
                            item = QListWidgetItem(label)
                            item.setCheckState(Qt.CheckState.Checked)
                            item.setData(256, entry)
                            self.mode_checklist.addItem(item)

            def _set_all_mode_checks(self, checked: bool) -> None:
                from PySide6.QtCore import Qt
                state = Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked
                for i in range(self.mode_checklist.count()):
                    self.mode_checklist.item(i).setCheckState(state)

            def _set_family_mode_checks(self, family: str) -> None:
                from PySide6.QtCore import Qt
                for i in range(self.mode_checklist.count()):
                    item = self.mode_checklist.item(i)
                    entry = item.data(256)
                    is_match = entry is not None and entry.family == family
                    item.setCheckState(
                        Qt.CheckState.Checked if is_match else Qt.CheckState.Unchecked
                    )

            def _set_cascade_mode_checks(self, cascade: int) -> None:
                """Check only modes matching the given cipher cascade level (1/2/3)."""
                from PySide6.QtCore import Qt
                for i in range(self.mode_checklist.count()):
                    item = self.mode_checklist.item(i)
                    entry = item.data(256)
                    is_match = entry is not None and entry.cipher_cascade == cascade
                    item.setCheckState(
                        Qt.CheckState.Checked if is_match else Qt.CheckState.Unchecked
                    )

            def _prefill(self, draft: dict) -> None:
                """Pre-fill dialog fields from an existing draft dict (for Edit mode)."""
                from PySide6.QtCore import Qt
                from PySide6.QtWidgets import QListWidgetItem

                # --- Target ---
                target_id = draft.get("target_id", "")
                for i in range(self.cmb_target.count()):
                    t = self.cmb_target.itemData(i)
                    if t and t.get("target_id") == target_id:
                        self.cmb_target.setCurrentIndex(i)  # triggers _on_target_changed
                        break

                # --- Headers ---
                wanted_ids = set(
                    draft.get("header_ids")
                    or ([draft["header_id"]] if draft.get("header_id") else [])
                )
                for i in range(self.lst_headers.count()):
                    item = self.lst_headers.item(i)
                    h = item.data(256)
                    item.setSelected(h is not None and h.header_id in wanted_ids)

                # --- Hash mode strategy ---
                strat = draft.get("hash_mode_strategy", "all")
                if strat == "current_only":
                    self.rad_current.setChecked(True)
                elif strat == "specific":
                    self.rad_specific.setChecked(True)   # triggers _rebuild_mode_checklist
                    mode_nums = set(draft.get("hash_mode_numbers", []))
                    for i in range(self.mode_checklist.count()):
                        item = self.mode_checklist.item(i)
                        entry = item.data(256)
                        item.setCheckState(
                            Qt.CheckState.Checked
                            if (entry and entry.mode in mode_nums)
                            else Qt.CheckState.Unchecked
                        )
                else:
                    self.rad_all.setChecked(True)

                # --- PIM ---
                if draft.get("pim_mode") == "custom":
                    self.rad_pim_custom.setChecked(True)
                    self.txt_pim.setText(draft.get("pim_raw_input", ""))
                else:
                    self.rad_pim_default.setChecked(True)

                # --- Password source ---
                _pw_src = draft.get("password_source_type", "manual")
                if _pw_src == "wordlist":
                    self.rad_pw_wordlist.setChecked(True)
                    self.txt_wordlist.setText(draft.get("password_wordlist_path", ""))
                elif _pw_src == "workspace_wordlist":
                    self.rad_pw_workspace.setChecked(True)
                    self._refresh_workspace_wordlists()
                    _saved_wl = draft.get("password_wordlist_path", "")
                    for _i in range(self.cmb_ws_wordlist.count()):
                        _d = self.cmb_ws_wordlist.itemData(_i)
                        if _d is not None and str(_d) == _saved_wl:
                            self.cmb_ws_wordlist.setCurrentIndex(_i)
                            break
                else:
                    self.rad_pw_manual.setChecked(True)
                    self.txt_passwords.setPlainText(draft.get("password_manual_text", ""))

                # --- Keyfiles ---
                self.kf_list.clear()
                for path in draft.get("keyfile_paths", []):
                    item = QListWidgetItem(path)
                    item.setData(256, path)
                    self.kf_list.addItem(item)

            def _on_pw_type_changed(self) -> None:
                is_manual = self.rad_pw_manual.isChecked()
                is_wordlist = self.rad_pw_wordlist.isChecked()
                is_workspace = self.rad_pw_workspace.isChecked()
                self.txt_passwords.setEnabled(is_manual)
                self.txt_wordlist.setEnabled(is_wordlist)
                self.cmb_ws_wordlist.setEnabled(is_workspace)
                if is_workspace and self.cmb_ws_wordlist.count() == 0:
                    self._refresh_workspace_wordlists()

            def _browse_wordlist(self) -> None:
                path, _ = QFileDialog.getOpenFileName(
                    self, "Select Wordlist File", "", "Text Files (*.txt);;All Files (*.*)"
                )
                if path:
                    self.txt_wordlist.setText(path)

            def _refresh_workspace_wordlists(self) -> None:
                """Populate the workspace wordlist combo from generated/wordlists/*.txt."""
                from pathlib import Path

                from portable_crypt_recovery.services.builders.password_builder import (
                    load_wordlist_meta,
                )
                prev = self.cmb_ws_wordlist.currentData()
                self.cmb_ws_wordlist.clear()
                if not self._workspace_root:
                    return
                wl_dir = self._workspace_root / "generated" / "wordlists"
                if not wl_dir.exists():
                    return
                restore_idx = 0
                for idx, f in enumerate(sorted(wl_dir.glob("*.txt"))):
                    meta = load_wordlist_meta(f)
                    nickname = meta.get("nickname", "")
                    count = meta.get("candidate_count")
                    if count is None:
                        try:
                            count = sum(1 for _ in f.open("r", encoding="utf-8", errors="replace"))
                        except OSError:
                            count = 0
                    count_str = f"{count:,} passwords"
                    label = f"{nickname}  ({count_str})" if nickname else f"{f.name}  ({count_str})"
                    self.cmb_ws_wordlist.addItem(label, userData=f)
                    if prev is not None and Path(prev) == f:
                        restore_idx = idx
                if self.cmb_ws_wordlist.count() > 0:
                    self.cmb_ws_wordlist.setCurrentIndex(restore_idx)

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

            # ------------------------------------------------------------------
            # Set pickers (load saved sets into the dialog)
            # ------------------------------------------------------------------

            def _load_hash_set_picker(self) -> None:
                from PySide6.QtWidgets import QMessageBox

                from portable_crypt_recovery.app.app_state import get_app_state
                from portable_crypt_recovery.services.builders.hash_mode_builder import (
                    list_named_hash_sets,
                )

                app_state = get_app_state()
                if not app_state.is_workspace_open():
                    QMessageBox.warning(self, "No Workspace", "Open a workspace first.")
                    return

                sets = list_named_hash_sets(app_state.workspace_root)
                if not sets:
                    QMessageBox.information(
                        self, "No Hash Sets",
                        "No saved hash sets found.\n"
                        "Build and save one in the Hash Sets screen.",
                    )
                    return

                items = [
                    {"label": f"{s.nickname}  ({len(s.entries)} modes)", "data": s}
                    for s in sets
                ]
                dlg = _NamedSetPicker(parent=self, items=items, title="Load Saved Hash Set")
                if dlg.exec() != 1:
                    return
                hms = dlg.selected
                if not hms:
                    return

                # Switch to specific mode and populate checklist
                self.rad_specific.setChecked(True)
                self._rebuild_mode_checklist()

                from PySide6.QtCore import Qt as _Qt
                mode_nums = {e.mode for e in hms.entries}
                for i in range(self.mode_checklist.count()):
                    entry = self.mode_checklist.item(i).data(256)
                    self.mode_checklist.item(i).setCheckState(
                        _Qt.CheckState.Checked
                        if (entry and entry.mode in mode_nums)
                        else _Qt.CheckState.Unchecked
                    )

            def _load_pim_set_picker(self) -> None:
                from PySide6.QtWidgets import QMessageBox

                from portable_crypt_recovery.app.app_state import get_app_state
                from portable_crypt_recovery.services.builders.pim_builder import (
                    list_named_pim_sets,
                )

                app_state = get_app_state()
                if not app_state.is_workspace_open():
                    QMessageBox.warning(self, "No Workspace", "Open a workspace first.")
                    return

                sets = list_named_pim_sets(app_state.workspace_root)
                if not sets:
                    QMessageBox.information(
                        self, "No PIM Sets",
                        "No saved PIM sets found.\n"
                        "Build and save one in the PIM Sets screen.",
                    )
                    return

                def _detail(ps):
                    if ps.pim_mode == "default":
                        return "default PIM"
                    n = len(ps.values)
                    return f"{n} value{'s' if n != 1 else ''}"

                items = [
                    {"label": f"{s.nickname}  ({_detail(s)})", "data": s}
                    for s in sets
                ]
                dlg = _NamedSetPicker(parent=self, items=items, title="Load Saved PIM Set")
                if dlg.exec() != 1:
                    return
                ps = dlg.selected
                if not ps:
                    return

                if ps.pim_mode == "default":
                    self.rad_pim_default.setChecked(True)
                    self.txt_pim.clear()
                else:
                    self.rad_pim_custom.setChecked(True)
                    self.txt_pim.setText(", ".join(str(v) for v in ps.values))

            def _load_kf_set_picker(self) -> None:
                from PySide6.QtWidgets import QListWidgetItem, QMessageBox

                from portable_crypt_recovery.app.app_state import get_app_state
                from portable_crypt_recovery.services.builders.keyfile_builder import (
                    list_named_keyfile_sets,
                )

                app_state = get_app_state()
                if not app_state.is_workspace_open():
                    QMessageBox.warning(self, "No Workspace", "Open a workspace first.")
                    return

                sets = list_named_keyfile_sets(app_state.workspace_root)
                if not sets:
                    QMessageBox.information(
                        self, "No Keyfile Sets",
                        "No saved keyfile sets found.\n"
                        "Build and save one in the Keyfile Sets screen.",
                    )
                    return

                items = [
                    {
                        "label": (
                            f"{s.nickname}  ({len(s.entries)} file"
                            f"{'s' if len(s.entries) != 1 else ''})"
                        ),
                        "data": s,
                    }
                    for s in sets
                ]
                dlg = _NamedSetPicker(parent=self, items=items, title="Load Saved Keyfile Set")
                if dlg.exec() != 1:
                    return
                ks = dlg.selected
                if not ks:
                    return

                self.kf_list.clear()
                for entry in ks.entries:
                    path_str = entry.original_path or entry.normalized_workspace_path
                    kf_item = QListWidgetItem(path_str)
                    kf_item.setData(256, path_str)
                    self.kf_list.addItem(kf_item)

            def _on_accept(self) -> None:
                from PySide6.QtWidgets import QMessageBox

                from portable_crypt_recovery.core.ids import new_id
                from portable_crypt_recovery.core.timestamps import utc_now_iso

                tgt = self.cmb_target.currentData()
                if not tgt:
                    QMessageBox.warning(self, "Missing Target", "Please select a target.")
                    return

                selected_header_items = self.lst_headers.selectedItems()
                if not selected_header_items:
                    QMessageBox.warning(
                        self, "No Headers Selected",
                        "Select at least one header to crack."
                    )
                    return
                header_objs = [it.data(256) for it in selected_header_items if it.data(256)]
                if not header_objs:
                    QMessageBox.warning(self, "Missing Header", "No headers available for this target.")
                    return

                if self.rad_pw_wordlist.isChecked():
                    pw_type = "wordlist"
                    wl_path = self.txt_wordlist.text().strip()
                    if not wl_path:
                        QMessageBox.warning(self, "No Wordlist", "Please select a wordlist file.")
                        return
                elif self.rad_pw_workspace.isChecked():
                    pw_type = "workspace_wordlist"
                    _ws_data = self.cmb_ws_wordlist.currentData()
                    wl_path = str(_ws_data) if _ws_data else ""
                    if not wl_path:
                        QMessageBox.warning(
                            self, "No Wordlist",
                            "No workspace wordlist selected.\n"
                            "Generate one in the Passwords panel first, then click Refresh."
                        )
                        return
                else:
                    pw_type = "manual"
                    wl_path = ""
                    if not self.txt_passwords.toPlainText().strip():
                        QMessageBox.warning(self, "No Passwords", "Please enter at least one password.")
                        return

                keyfile_paths = [
                    self.kf_list.item(i).data(256)
                    for i in range(self.kf_list.count())
                ]

                target_name = tgt.get("display_name", "?")
                header_ids = [h.header_id for h in header_objs]
                candidate_types = [
                    getattr(h, "candidate_type", "normal_volume_header")
                    for h in header_objs
                ]

                # Build a readable label
                if len(header_objs) == 1:
                    ctype_short = (
                        candidate_types[0]
                        .replace("_volume_header", "")
                        .replace("_", " ")
                        .strip()
                        or candidate_types[0]
                    )
                    draft_label = f"{target_name} — {ctype_short}"
                else:
                    type_shorts = [
                        ct.replace("_volume_header", "").replace("_", " ").strip() or ct
                        for ct in candidate_types
                    ]
                    draft_label = f"{target_name} — {len(header_objs)} headers ({', '.join(type_shorts)})"

                # Resolve hash mode strategy and specific mode list
                if self.rad_specific.isChecked():
                    from PySide6.QtCore import Qt as _Qt2
                    hash_mode_numbers = [
                        self.mode_checklist.item(i).data(256).mode
                        for i in range(self.mode_checklist.count())
                        if (
                            self.mode_checklist.item(i).checkState() == _Qt2.CheckState.Checked
                            and self.mode_checklist.item(i).data(256) is not None
                        )
                    ]
                    if not hash_mode_numbers:
                        QMessageBox.warning(
                            self, "No Modes Selected",
                            "Select at least one hash mode before saving."
                        )
                        return
                    hash_mode_strategy = "specific"
                elif self.rad_current.isChecked():
                    hash_mode_strategy = "current_only"
                    hash_mode_numbers = []
                else:
                    hash_mode_strategy = "all"
                    hash_mode_numbers = []

                # Estimate job count (headers × modes per header × pim × kf combos)
                estimated_job_count = 0
                try:
                    from portable_crypt_recovery.services.builders.hash_mode_builder import (
                        build_mode_set,
                    )
                    from portable_crypt_recovery.services.builders.pim_builder import (
                        build_pim_set,
                    )
                    total_modes = 0
                    if hash_mode_strategy == "specific":
                        specific_set = set(hash_mode_numbers)
                        for h_obj in header_objs:
                            ctype = getattr(h_obj, "candidate_type", "normal_volume_header")
                            ms = build_mode_set(
                                family=tgt.get("container_family", "unknown"),
                                candidate_type=ctype,
                                target_id=tgt["target_id"],
                                header_id=h_obj.header_id,
                                include_legacy=True,
                            )
                            total_modes += sum(1 for e in ms.entries if e.mode in specific_set)
                    else:
                        include_legacy = (hash_mode_strategy != "current_only")
                        for h_obj in header_objs:
                            ctype = getattr(h_obj, "candidate_type", "normal_volume_header")
                            ms = build_mode_set(
                                family=tgt.get("container_family", "unknown"),
                                candidate_type=ctype,
                                target_id=tgt["target_id"],
                                header_id=h_obj.header_id,
                                include_legacy=include_legacy,
                            )
                            total_modes += len(ms.entries)
                    if self.rad_pim_custom.isChecked():
                        pim_set = build_pim_set(
                            self.txt_pim.text().strip(),
                            workspace_root=self._workspace_root,
                            force=False,
                        )
                        pim_count = max(len(pim_set.values), 1)
                    else:
                        pim_count = 1
                    # kf_count: no-keyfile attempt (always 1) + all non-empty combos
                    # = 2^n  (e.g. 0 keyfiles→1, 1 keyfile→2, 2 keyfiles→4)
                    n_kf = len(keyfile_paths)
                    kf_count = 2 ** n_kf
                    estimated_job_count = total_modes * pim_count * kf_count
                except Exception:
                    estimated_job_count = 0

                self.draft = {
                    "draft_id": new_id("draft"),
                    "label": draft_label,
                    "target_id": tgt["target_id"],
                    "header_ids": header_ids,
                    # Keep single-header fields for backward compat with old drafts
                    "header_id": header_ids[0],
                    "family": tgt.get("container_family", "unknown"),
                    "candidate_type": candidate_types[0],
                    "hash_mode_strategy": hash_mode_strategy,
                    # Populated only when strategy == "specific"; empty list otherwise.
                    "hash_mode_numbers": hash_mode_numbers,
                    "pim_mode": "custom" if self.rad_pim_custom.isChecked() else "default",
                    "pim_raw_input": self.txt_pim.text().strip(),
                    "password_source_type": pw_type,
                    "password_manual_text": self.txt_passwords.toPlainText(),
                    "password_wordlist_path": wl_path if pw_type in ("wordlist", "workspace_wordlist") else self.txt_wordlist.text().strip(),
                    "keyfile_paths": keyfile_paths,
                    "estimated_job_count": estimated_job_count,
                    "created_timestamp": utc_now_iso(),
                }
                self.accept()

        return _Dlg(parent, workspace_root, draft_data)


# ---------------------------------------------------------------------------
# Generic named-set picker dialog (reused by hash / PIM / keyfile pickers)
# ---------------------------------------------------------------------------

class _NamedSetPicker:  # pragma: no cover
    """Simple list-picker dialog for selecting a saved named set."""

    def __new__(cls, parent=None, items=None, title="Select Set"):
        from PySide6.QtWidgets import (
            QDialog,
            QDialogButtonBox,
            QLabel,
            QListWidget,
            QListWidgetItem,
            QVBoxLayout,
        )

        class _Dlg(QDialog):
            def __init__(self, parent, items, title) -> None:
                super().__init__(parent)
                self.setWindowTitle(title)
                self.resize(440, 300)
                self.selected = None

                layout = QVBoxLayout(self)
                layout.addWidget(QLabel("Select a saved set:"))

                self._lst = QListWidget()
                for entry in (items or []):
                    item = QListWidgetItem(entry.get("label", "?"))
                    item.setData(256, entry.get("data"))
                    self._lst.addItem(item)
                layout.addWidget(self._lst, 1)

                buttons = QDialogButtonBox(
                    QDialogButtonBox.StandardButton.Ok
                    | QDialogButtonBox.StandardButton.Cancel
                )
                buttons.accepted.connect(self._on_accept)
                buttons.rejected.connect(self.reject)
                layout.addWidget(buttons)

                self._lst.itemDoubleClicked.connect(lambda _: self._on_accept())
                if self._lst.count() > 0:
                    self._lst.setCurrentRow(0)

            def _on_accept(self) -> None:
                item = self._lst.currentItem()
                if item:
                    self.selected = item.data(256)
                    self.accept()

        return _Dlg(parent, items, title)
