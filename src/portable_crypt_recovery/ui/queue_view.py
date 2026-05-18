"""Queue view — list of queued jobs and queue controls."""

from __future__ import annotations


class QueueView:  # pragma: no cover
    """Queued job list with Start/Pause/Stop/Resume/Skip/Restart controls."""

    def __new__(cls):
        from PySide6.QtCore import QTimer
        from PySide6.QtWidgets import (
            QGroupBox,
            QHBoxLayout,
            QLabel,
            QListWidget,
            QProgressBar,
            QPushButton,
            QVBoxLayout,
            QWidget,
        )

        class _QueueView(QWidget):
            def __init__(self) -> None:
                super().__init__()
                self._runner = None      # active QueueRunner or None
                self._job_list_follow = True   # auto-scroll job list to running job
                self._log_follow = True        # auto-scroll log to bottom for live job
                self._log_job_id = ""          # job ID currently displayed in log panel
                layout = QVBoxLayout(self)

                # Queue controls
                controls_group = QGroupBox("Queue Controls")
                controls_layout = QHBoxLayout(controls_group)
                self.btn_start = QPushButton("Start Queue")
                self.btn_pause_now = QPushButton("Pause Now")
                self.btn_pause_after = QPushButton("Pause After Current")
                self.btn_stop_save = QPushButton("Stop & Re-queue")
                self.btn_stop_discard = QPushButton("Stop & Discard")
                self.btn_resume = QPushButton("Resume")
                self.btn_skip = QPushButton("Skip Selected")
                self.btn_restart = QPushButton("Restart Selected")
                self.btn_clear_queue = QPushButton("Clear Queue")
                self.btn_copy_cmd = QPushButton("Copy Command")
                for btn in [
                    self.btn_start, self.btn_pause_now, self.btn_pause_after,
                    self.btn_stop_save, self.btn_stop_discard, self.btn_resume,
                    self.btn_skip, self.btn_restart,
                    self.btn_clear_queue, self.btn_copy_cmd,
                ]:
                    controls_layout.addWidget(btn)
                layout.addWidget(controls_group)

                # Status row
                self.lbl_status = QLabel("Queue stopped")
                self.lbl_running = QLabel("No job running")
                self.lbl_remaining = QLabel("")
                self.progress_bar = QProgressBar()
                self.progress_bar.setRange(0, 100)
                self.progress_bar.setValue(0)
                status_row = QHBoxLayout()
                status_row.addWidget(self.lbl_status)
                status_row.addStretch()
                status_row.addWidget(self.lbl_remaining)
                status_row.addSpacing(16)
                status_row.addWidget(self.lbl_running)
                layout.addLayout(status_row)
                layout.addWidget(self.progress_bar)

                # Job list + log viewer in a splitter
                from PySide6.QtCore import Qt as _Qt
                from PySide6.QtWidgets import QPlainTextEdit, QSplitter
                splitter = QSplitter(_Qt.Orientation.Vertical)

                self.job_list = QListWidget()
                from PySide6.QtWidgets import QAbstractItemView
                self.job_list.setSelectionMode(
                    QAbstractItemView.SelectionMode.ExtendedSelection
                )
                splitter.addWidget(self.job_list)

                log_widget = QWidget()
                log_layout = QVBoxLayout(log_widget)
                log_layout.setContentsMargins(0, 4, 0, 0)
                self.lbl_log_header = QLabel("Select a job to view its log")
                self.lbl_log_header.setStyleSheet("color: gray; font-size: 11px;")
                log_layout.addWidget(self.lbl_log_header)
                self.txt_log = QPlainTextEdit()
                self.txt_log.setReadOnly(True)
                self.txt_log.setMaximumBlockCount(200)
                self.txt_log.setStyleSheet(
                    "font-family: Consolas, monospace; font-size: 11px;"
                )
                log_layout.addWidget(self.txt_log)
                splitter.addWidget(log_widget)

                splitter.setSizes([300, 200])
                layout.addWidget(splitter, 1)

                # Wire buttons
                self.btn_start.clicked.connect(self._start_queue)
                self.btn_pause_now.clicked.connect(self._pause_now)
                self.btn_pause_after.clicked.connect(self._pause_after)
                self.btn_stop_save.clicked.connect(self._stop_save)
                self.btn_stop_discard.clicked.connect(self._stop_discard)
                self.btn_resume.clicked.connect(self._resume)
                self.btn_skip.clicked.connect(self._skip_selected)
                self.btn_restart.clicked.connect(self._restart_selected)
                self.btn_clear_queue.clicked.connect(self._clear_queue)
                self.btn_copy_cmd.clicked.connect(self._copy_command)
                self.job_list.currentItemChanged.connect(self._on_job_selected)

                # Poll timer
                self._timer = QTimer(self)
                self._timer.setInterval(2000)
                self._timer.timeout.connect(self._poll_status)

                # Smart auto-scroll for job list:
                # sliderPressed = user grabbed bar → stop following
                # valueChanged at max = user scrolled to bottom → resume following
                self.job_list.verticalScrollBar().sliderPressed.connect(
                    self._on_job_list_slider_pressed
                )
                self.job_list.verticalScrollBar().valueChanged.connect(
                    self._on_job_list_scroll_changed
                )

                # Smart auto-scroll for log panel:
                # sliderPressed = user grabbed bar → stop following
                # valueChanged at max = user scrolled to bottom → resume following
                self.txt_log.verticalScrollBar().sliderPressed.connect(
                    self._on_log_slider_pressed
                )
                self.txt_log.verticalScrollBar().valueChanged.connect(
                    self._on_log_scroll_changed
                )

                self._refresh_list()
                self._update_button_states(queue_status="stopped")

            # ------------------------------------------------------------------
            # Smart auto-scroll helpers
            # ------------------------------------------------------------------

            def _on_job_list_slider_pressed(self) -> None:
                """User grabbed the job list scrollbar — stop following running job."""
                self._job_list_follow = False

            def _on_job_list_scroll_changed(self, value: int) -> None:
                """Re-enable follow when user scrolls back to the bottom of the job list."""
                sb = self.job_list.verticalScrollBar()
                if value >= sb.maximum():
                    self._job_list_follow = True

            def _on_log_slider_pressed(self) -> None:
                """User grabbed the log scrollbar — stop auto-scrolling the log."""
                self._log_follow = False

            def _on_log_scroll_changed(self, value: int) -> None:
                """Re-enable log follow when user scrolls back to the bottom."""
                sb = self.txt_log.verticalScrollBar()
                if value >= sb.maximum():
                    self._log_follow = True

            # ------------------------------------------------------------------
            # Start
            # ------------------------------------------------------------------

            def _start_queue(self) -> None:
                import json
                from pathlib import Path

                from PySide6.QtWidgets import QMessageBox

                from portable_crypt_recovery.app.app_state import get_app_state
                from portable_crypt_recovery.core.atomic_write import atomic_write_json
                from portable_crypt_recovery.models.queue_state import QueueState
                from portable_crypt_recovery.services.hashcat.command_builder import (
                    CommandBuilderError,
                    build_command_with_devices,
                )
                from portable_crypt_recovery.services.queue.queue_runner import QueueRunner

                state = get_app_state()
                if not state.is_workspace_open():
                    QMessageBox.warning(self, "No Workspace", "Open a workspace first.")
                    return
                if not state.is_hashcat_ready():
                    QMessageBox.warning(
                        self, "Hashcat Not Ready",
                        "Configure Hashcat in Settings before starting the queue."
                    )
                    return
                if self._runner is not None:
                    QMessageBox.information(self, "Already Running", "Queue is already active.")
                    return

                ws = state.workspace_root
                hashcat_exe = Path(state.hashcat_setup.executable_path)

                # Load queue state
                queue_file = ws / "queue" / "queue-state.json"
                try:
                    qs = QueueState.from_dict(
                        json.loads(queue_file.read_text(encoding="utf-8"))
                    )
                except Exception:
                    QMessageBox.warning(self, "No Jobs", "No jobs in queue. Create drafts and expand them first.")
                    return

                pending = [
                    qs.jobs[jid]
                    for jid in qs.queue_order
                    if jid in qs.jobs and qs.jobs[jid].status == "pending"
                ]
                if not pending:
                    QMessageBox.information(self, "Nothing to Run", "No pending jobs in queue.")
                    return

                # Show busy indicator while building commands and starting the runner
                from PySide6.QtCore import Qt
                from PySide6.QtWidgets import QApplication, QProgressDialog
                progress = QProgressDialog(
                    f"Preparing {len(pending)} job(s)…", None, 0, 0, self
                )
                progress.setWindowTitle("Starting Queue")
                progress.setWindowModality(Qt.WindowModality.WindowModal)
                progress.setMinimumDuration(0)
                progress.setValue(0)
                progress.show()
                QApplication.processEvents()

                # Always rebuild command arrays when starting the queue so that
                # any code changes (flags, paths) take effect immediately rather
                # than reusing a stale array stored in queue-state.json.
                device_ids = state.hashcat_setup.selected_device_ids or None
                use_opt = state.hashcat_setup.use_optimized_kernels
                use_cpu_opencl = state.hashcat_setup.use_cpu_opencl
                ignore_cuda = state.hashcat_setup.ignore_cuda
                errors: list[str] = []
                for job in pending:
                    try:
                        job.command_array = build_command_with_devices(
                            job, hashcat_exe, ws, device_ids,
                            use_optimized_kernels=use_opt,
                            use_cpu_opencl=use_cpu_opencl,
                            ignore_cuda=ignore_cuda,
                        )
                    except CommandBuilderError as exc:
                        errors.append(f"{job.job_id[:8]}: {exc}")

                if errors:
                    progress.close()
                    QMessageBox.warning(
                        self, "Command Build Errors",
                        f"{len(errors)} job(s) could not build a command:\n" + "\n".join(errors[:5])
                    )

                # Save updated command arrays back to disk
                atomic_write_json(queue_file, qs.to_dict())

                self._runner = QueueRunner(
                    workspace_root=ws,
                    queue_state=qs,
                    hashcat_executable=hashcat_exe,
                    on_status_update=lambda _: None,
                    behavior_after_crack=state.queue_behavior_after_crack,
                )
                if not self._runner.start():
                    progress.close()
                    self._runner = None
                    QMessageBox.warning(
                        self, "Queue Locked",
                        "Another instance may be running (lock file exists). "
                        "Delete queue/queue.lock if you are sure no other instance is active."
                    )
                    return

                progress.close()
                self._timer.start()
                self._update_button_states("running")
                self.lbl_status.setText("Queue running")

            # ------------------------------------------------------------------
            # Controls
            # ------------------------------------------------------------------

            def _pause_now(self) -> None:
                if self._runner:
                    self._runner.pause()
                    self._update_button_states("paused")
                    self.lbl_status.setText("Queue paused")

            def _pause_after(self) -> None:
                if self._runner:
                    self._runner.stop_after_current()
                    self.lbl_status.setText("Stopping after current job…")

            def _stop_save(self) -> None:
                if self._runner:
                    self._runner.stop_and_save()
                    self._on_queue_stopped()

            def _stop_discard(self) -> None:
                if self._runner:
                    self._runner.stop_and_discard()
                    self._on_queue_stopped()

            def _resume(self) -> None:
                if self._runner:
                    self._runner.resume()
                    self._update_button_states("running")
                    self.lbl_status.setText("Queue running")

            def _on_queue_stopped(self) -> None:
                self._runner = None
                self._timer.stop()
                self._update_button_states("stopped")
                self.lbl_status.setText("Queue stopped")
                self.lbl_running.setText("No job running")
                self.progress_bar.setValue(0)
                self._refresh_list()
                # Reset title to baseline (refresh_list will set it if jobs exist)
                from portable_crypt_recovery import __app_name__, __version__
                if not self.lbl_remaining.text():
                    self.window().setWindowTitle(f"{__app_name__} {__version__}")

            # ------------------------------------------------------------------
            # Skip / Restart individual jobs
            # ------------------------------------------------------------------

            def _skip_selected(self) -> None:
                self._set_selected_status("skipped")

            def _restart_selected(self) -> None:
                self._set_selected_status("pending")

            def _set_selected_status(self, new_status: str) -> None:
                import json

                from portable_crypt_recovery.app.app_state import get_app_state
                from portable_crypt_recovery.core.atomic_write import atomic_write_json
                from portable_crypt_recovery.models.queue_state import QueueState

                selected = self.job_list.selectedItems()
                if not selected:
                    return

                job_ids = [it.data(256) for it in selected if it.data(256)]
                if not job_ids:
                    return

                state = get_app_state()
                if not state.is_workspace_open():
                    return

                queue_file = state.workspace_root / "queue" / "queue-state.json"
                try:
                    qs = QueueState.from_dict(
                        json.loads(queue_file.read_text(encoding="utf-8"))
                    )
                except Exception:
                    return

                from portable_crypt_recovery.core.timestamps import utc_now_iso
                changed = False
                for job_id in job_ids:
                    if job_id in qs.jobs:
                        qs.jobs[job_id].status = new_status
                        qs.jobs[job_id].updated_timestamp = utc_now_iso()
                        if new_status == "pending":
                            qs.jobs[job_id].command_array = []
                        changed = True
                if changed:
                    atomic_write_json(queue_file, qs.to_dict())
                    self._refresh_list()

            def _clear_queue(self) -> None:
                import json

                from PySide6.QtWidgets import QMessageBox

                from portable_crypt_recovery.app.app_state import get_app_state
                from portable_crypt_recovery.core.atomic_write import atomic_write_json
                from portable_crypt_recovery.models.queue_state import QueueState

                if self._runner is not None:
                    QMessageBox.warning(
                        self, "Queue Active",
                        "Stop the queue before clearing it."
                    )
                    return

                state = get_app_state()
                if not state.is_workspace_open():
                    return

                queue_file = state.workspace_root / "queue" / "queue-state.json"
                try:
                    qs = QueueState.from_dict(
                        json.loads(queue_file.read_text(encoding="utf-8"))
                    )
                except Exception:
                    qs = QueueState()

                count = len(qs.queue_order)
                if count == 0:
                    QMessageBox.information(self, "Clear Queue", "Queue is already empty.")
                    return

                reply = QMessageBox.question(
                    self, "Clear Queue",
                    f"Remove all {count} job(s) from the queue?\n\n"
                    "This cannot be undone. Jobs will need to be re-sent from the Jobs tab.",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No,
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return

                qs.jobs.clear()
                qs.queue_order.clear()
                qs.current_running_job = None
                atomic_write_json(queue_file, qs.to_dict())
                state.job_count = 0
                self.txt_log.clear()
                self.lbl_log_header.setText("Select a job to view its log")
                self._refresh_list()

            def _copy_command(self) -> None:
                from PySide6.QtWidgets import QApplication

                item = self.job_list.currentItem()
                if item is None:
                    self.lbl_log_header.setText("Select a job first to copy its command.")
                    return

                import json

                from portable_crypt_recovery.app.app_state import get_app_state
                from portable_crypt_recovery.models.queue_state import QueueState

                job_id = item.data(256)
                state = get_app_state()
                if not state.is_workspace_open():
                    return

                queue_file = state.workspace_root / "queue" / "queue-state.json"
                try:
                    qs = QueueState.from_dict(
                        json.loads(queue_file.read_text(encoding="utf-8"))
                    )
                except Exception:
                    return

                job = qs.jobs.get(job_id)
                if job is None:
                    return

                if not job.command_array:
                    self.lbl_log_header.setText(
                        "No command built yet — start the queue to generate commands."
                    )
                    return

                cmd_str = " ".join(job.command_array)
                clipboard = QApplication.clipboard()
                clipboard.setText(cmd_str)
                self.lbl_log_header.setText(
                    f"✓ Command copied to clipboard  ({len(job.command_array)} args)"
                )

            # ------------------------------------------------------------------
            # Job selection → log viewer
            # ------------------------------------------------------------------

            def _on_job_selected(self, current, _previous) -> None:
                """Load and display log + command array for the selected job."""
                import json

                from portable_crypt_recovery.app.app_state import get_app_state
                from portable_crypt_recovery.models.queue_state import QueueState

                if current is None:
                    self.lbl_log_header.setText("Select a job to view its log")
                    self.txt_log.clear()
                    return

                job_id = current.data(256)
                state = get_app_state()
                if not state.is_workspace_open():
                    return

                queue_file = state.workspace_root / "queue" / "queue-state.json"
                try:
                    qs = QueueState.from_dict(
                        json.loads(queue_file.read_text(encoding="utf-8"))
                    )
                except Exception:
                    return

                job = qs.jobs.get(job_id)
                if job is None:
                    return

                # Track whether this is a fresh job selection or a poll refresh
                # for the same job that's already displayed.
                is_new_job = (job_id != self._log_job_id)
                self._log_job_id = job_id
                if is_new_job:
                    # User clicked a different job — reset follow state
                    self._log_follow = True

                # Save scroll position before setPlainText wipes it
                log_sb = self.txt_log.verticalScrollBar()
                saved_log_pos = log_sb.value()

                lines: list[str] = []

                # ---- CRACKED BANNER (top, hard to miss) ----
                if job.status == "cracked":
                    pw = job.cracked_password
                    if not pw:
                        # Fall back to reading the outfile directly
                        try:
                            outfile_abs = state.workspace_root / job.outfile_path
                            if outfile_abs.exists():
                                raw = outfile_abs.read_text(
                                    encoding="utf-8", errors="replace"
                                ).strip()
                                if raw and ":" in raw:
                                    pw = raw.split(":", 1)[-1]
                                elif raw:
                                    pw = raw
                        except OSError:
                            pass
                    lines.append("=" * 60)
                    lines.append("  *** CRACKED ***")
                    lines.append(f"  PASSWORD : {pw if pw else '(see outfile below)'}")
                    outfile_rel = job.outfile_path
                    lines.append(f"  OUTFILE  : {outfile_rel}")
                    lines.append("=" * 60)
                    lines.append("")

                # Command array
                if job.command_array:
                    lines.append("=== COMMAND ===")
                    lines.append(" ".join(job.command_array))
                    lines.append("")
                else:
                    lines.append("=== COMMAND ===")
                    lines.append("(not yet built — send to queue and start to generate)")
                    lines.append("")

                # Log file
                log_abs = state.workspace_root / job.log_path
                status_label = job.status.upper()
                self.lbl_log_header.setText(
                    f"Job {job_id[:8]}  |  mode {job.hashcat_mode}"
                    f"  |  [{status_label}]  |  log: {job.log_path}"
                )
                if log_abs.exists():
                    try:
                        log_lines = log_abs.read_text(
                            encoding="utf-8", errors="replace"
                        ).splitlines()
                        lines.append(f"=== LOG ({len(log_lines)} lines) ===")
                        lines += log_lines
                    except OSError as exc:
                        lines.append(f"(could not read log: {exc})")
                else:
                    lines.append("=== LOG ===")
                    lines.append(
                        f"(no log file at {log_abs})"
                    )

                self.txt_log.setPlainText("\n".join(lines))
                # setPlainText resets scroll to 0; apply smart scroll:
                # - New job selected: scroll per status and (re-)enable following
                # - Same job, following enabled: scroll per status
                # - Same job, user scrolled away: restore their previous position
                log_sb = self.txt_log.verticalScrollBar()
                if is_new_job or self._log_follow:
                    if job.status == "cracked":
                        log_sb.setValue(0)
                    else:
                        log_sb.setValue(log_sb.maximum())
                else:
                    # Restore user's reading position (content may have grown,
                    # so clamp to new maximum just in case)
                    log_sb.setValue(min(saved_log_pos, log_sb.maximum()))

            # ------------------------------------------------------------------
            # Polling / Refresh
            # ------------------------------------------------------------------

            def _poll_status(self) -> None:
                import json

                from portable_crypt_recovery.app.app_state import get_app_state
                from portable_crypt_recovery.models.queue_state import QueueState

                state = get_app_state()
                if not state.is_workspace_open():
                    return

                queue_file = state.workspace_root / "queue" / "queue-state.json"
                try:
                    qs = QueueState.from_dict(
                        json.loads(queue_file.read_text(encoding="utf-8"))
                    )
                except Exception:
                    return

                # Detect if runner finished
                if self._runner is not None and qs.status == "stopped":
                    self._on_queue_stopped()
                    return

                # Update running job label
                current_id = qs.current_running_job
                if current_id and current_id in qs.jobs:
                    job = qs.jobs[current_id]
                    self.lbl_running.setText(
                        f"Running: {job.session_name}  mode={job.hashcat_mode}"
                    )
                else:
                    self.lbl_running.setText("No job running")

                self._refresh_list()
                # Keep the log panel fresh for whichever job is selected
                self._on_job_selected(self.job_list.currentItem(), None)

            def _refresh_list(self) -> None:
                import json

                from PySide6.QtCore import Qt
                from PySide6.QtGui import QBrush, QColor
                from PySide6.QtWidgets import QListWidgetItem

                from portable_crypt_recovery.app.app_state import get_app_state
                from portable_crypt_recovery.models.queue_state import QueueState

                current_data = None
                item = self.job_list.currentItem()
                if item:
                    current_data = item.data(256)

                scroll_pos = self.job_list.verticalScrollBar().value()

                self.job_list.clear()
                state = get_app_state()
                if not state.is_workspace_open():
                    return

                queue_file = state.workspace_root / "queue" / "queue-state.json"
                if not queue_file.exists():
                    return

                try:
                    qs = QueueState.from_dict(
                        json.loads(queue_file.read_text(encoding="utf-8"))
                    )
                except Exception:
                    return

                # --- Color maps (dark-theme friendly) ---
                _bg = {
                    "pending":   None,
                    "running":   QColor("#1a3a2a"),
                    "paused":    QColor("#3a3010"),
                    "cracked":   QColor("#0f3020"),
                    "exhausted": QColor("#2a1a10"),   # orange-tinted: tried, no match
                    "aborted":   QColor("#2a2a10"),   # yellow-tinted: stopped, will re-run
                    "failed":    QColor("#3a1010"),   # red: error
                    "skipped":   QColor("#222228"),
                }
                _fg = {
                    "pending":   None,
                    "running":   QColor("#7fe0a0"),
                    "paused":    QColor("#f0c060"),
                    "cracked":   QColor("#50e090"),
                    "exhausted": QColor("#e0a060"),   # orange: tried, no match
                    "aborted":   QColor("#c0c060"),   # yellow: stopped, re-queued
                    "failed":    QColor("#e06060"),   # red: error
                    "skipped":   QColor("#8888aa"),
                }

                # --- Group jobs by draft (preserving queue order) ---
                # Build ordered list of (draft_id, draft_label) groups
                seen_drafts: list[tuple[str, str]] = []
                seen_draft_ids: set[str] = set()
                for job_id in qs.queue_order:
                    job = qs.jobs.get(job_id)
                    if job is None:
                        continue
                    did = job.draft_id or ""
                    if did not in seen_draft_ids:
                        seen_draft_ids.add(did)
                        seen_drafts.append((did, job.draft_label or did or "Ungrouped jobs"))

                # Count status per draft for the header summary
                draft_status_counts: dict[str, dict[str, int]] = {}
                for job_id in qs.queue_order:
                    job = qs.jobs.get(job_id)
                    if job is None:
                        continue
                    did = job.draft_id or ""
                    draft_status_counts.setdefault(did, {})
                    draft_status_counts[did][job.status] = (
                        draft_status_counts[did].get(job.status, 0) + 1
                    )

                # --- Render: separator header then jobs for each draft ---
                for draft_id, draft_label in seen_drafts:
                    # Count jobs and build a short status summary
                    sc = draft_status_counts.get(draft_id, {})
                    total = sum(sc.values())
                    parts = []
                    for st in ("running", "pending", "cracked", "exhausted",
                               "aborted", "failed", "paused", "skipped"):
                        n = sc.get(st, 0)
                        if n:
                            parts.append(f"{n} {st}")
                    summary = "  ·  ".join(parts) if parts else "0 jobs"

                    sep = QListWidgetItem(f"▶  {draft_label}  ({total} jobs: {summary})")
                    sep.setFlags(Qt.ItemFlag.NoItemFlags)   # not selectable
                    sep.setBackground(QBrush(QColor("#1e2a3a")))
                    sep.setForeground(QBrush(QColor("#88b8e8")))
                    self.job_list.addItem(sep)

                    for job_id in qs.queue_order:
                        job = qs.jobs.get(job_id)
                        if job is None:
                            continue
                        if (job.draft_id or "") != draft_id:
                            continue
                        pim_label = f"PIM={job.pim_value}" if job.pim_mode == "custom" else "default PIM"
                        label = (
                            f"  [{job.status.upper():<14}]  "
                            f"mode={job.hashcat_mode}  {pim_label}  "
                            f"session={job.session_name}"
                        )
                        list_item = QListWidgetItem(label)
                        list_item.setData(256, job_id)
                        color = _bg.get(job.status)
                        if color:
                            list_item.setBackground(QBrush(color))
                        fg = _fg.get(job.status)
                        if fg:
                            list_item.setForeground(QBrush(fg))
                        self.job_list.addItem(list_item)
                        if job_id == current_data:
                            self.job_list.setCurrentItem(list_item)

                # Auto-scroll: jump to running job only when following;
                # otherwise restore the user's previous scroll position.
                running_item = None
                for i in range(self.job_list.count()):
                    it = self.job_list.item(i)
                    if it and it.data(256) == qs.current_running_job:
                        running_item = it
                        break
                if running_item and self._job_list_follow:
                    from PySide6.QtWidgets import QAbstractItemView
                    self.job_list.scrollToItem(
                        running_item, QAbstractItemView.ScrollHint.EnsureVisible
                    )
                else:
                    self.job_list.verticalScrollBar().setValue(scroll_pos)

                # --- Jobs remaining counter ---
                total_jobs = len(qs.queue_order)
                pending_jobs = sum(
                    1 for jid in qs.queue_order
                    if qs.jobs.get(jid) and qs.jobs[jid].status in ("pending", "running")
                )
                done_jobs = total_jobs - pending_jobs
                if total_jobs > 0:
                    remaining_text = (
                        f"{pending_jobs} remaining  /  {total_jobs} total"
                        if pending_jobs > 0
                        else f"All {total_jobs} job(s) done"
                    )
                    self.lbl_remaining.setText(remaining_text)
                    # Update window title bar
                    from portable_crypt_recovery import __app_name__, __version__
                    title_suffix = (
                        f" — {pending_jobs} remaining"
                        if pending_jobs > 0
                        else f" — {done_jobs} done"
                    )
                    self.window().setWindowTitle(
                        f"{__app_name__} {__version__}{title_suffix}"
                    )
                else:
                    self.lbl_remaining.setText("")
                    from portable_crypt_recovery import __app_name__, __version__
                    self.window().setWindowTitle(f"{__app_name__} {__version__}")

            # ------------------------------------------------------------------
            # Button state management
            # ------------------------------------------------------------------

            def _update_button_states(self, queue_status: str) -> None:
                stopped = queue_status == "stopped"
                running = queue_status == "running"
                paused = queue_status == "paused"

                self.btn_start.setEnabled(stopped)
                self.btn_pause_now.setEnabled(running)
                self.btn_pause_after.setEnabled(running)
                self.btn_stop_save.setEnabled(running or paused)
                self.btn_stop_discard.setEnabled(running or paused)
                self.btn_resume.setEnabled(paused)
                self.btn_skip.setEnabled(True)
                self.btn_restart.setEnabled(True)
                self.btn_clear_queue.setEnabled(stopped)
                self.btn_copy_cmd.setEnabled(True)

            def update_progress(self, percent: float, description: str = "") -> None:
                self.progress_bar.setValue(int(percent))
                if description:
                    self.lbl_running.setText(description)

        return _QueueView()
