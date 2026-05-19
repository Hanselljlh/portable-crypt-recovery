"""Queue view — list of queued tasks and queue controls."""

from __future__ import annotations


class QueueView:  # pragma: no cover
    """Queued task list with Start/Pause/Stop/Resume/Skip/Restart controls."""

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
                self._job_list_follow = False  # auto-scroll task list to running task
                self._log_follow = True        # auto-scroll log to bottom for live task
                self._log_task_id = ""         # task ID currently displayed in log panel
                self._collapsed_drafts: set[str] = set()  # draft IDs whose rows are hidden
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
                self.lbl_running = QLabel("No task running")
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
                self.lbl_log_header = QLabel("Select a task to view its log")
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
                self.job_list.itemClicked.connect(self._on_job_list_item_clicked)

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
                """Update follow flag when user scrolls the job list.

                Only fires for user-initiated scrolls; programmatic scrolls
                block signals around setValue so this handler is not called.
                """
                sb = self.job_list.verticalScrollBar()
                if sb.maximum() == 0:
                    return  # list fits on screen; follow state not meaningful
                self._job_list_follow = value >= sb.maximum()

            def _on_log_slider_pressed(self) -> None:
                """User grabbed the log scrollbar — stop auto-scrolling the log."""
                self._log_follow = False

            def _on_log_scroll_changed(self, value: int) -> None:
                """Update log follow flag based on user scroll position.

                Only fires for user-initiated scrolls; programmatic scrolls
                block signals around setValue so this handler is not called.
                """
                sb = self.txt_log.verticalScrollBar()
                if sb.maximum() == 0:
                    return  # content fits on screen; follow state not meaningful
                self._log_follow = value >= sb.maximum()

            def _on_job_list_item_clicked(self, item) -> None:
                """Toggle expand/collapse when user clicks a group header row."""
                draft_id = item.data(257)   # group-header rows store draft_id here
                if draft_id is not None:
                    if draft_id in self._collapsed_drafts:
                        self._collapsed_drafts.discard(draft_id)
                    else:
                        self._collapsed_drafts.add(draft_id)
                    self._refresh_list()

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
                    QMessageBox.warning(self, "No Tasks", "No tasks in queue. Create drafts and expand them first.")
                    return

                pending = [
                    qs.tasks[tid]
                    for tid in qs.task_order
                    if tid in qs.tasks and qs.tasks[tid].status == "pending"
                ]
                if not pending:
                    QMessageBox.information(self, "Nothing to Run", "No pending tasks in queue.")
                    return

                # Show busy indicator while building commands and starting the runner
                from PySide6.QtCore import Qt
                from PySide6.QtWidgets import QApplication, QProgressDialog
                progress = QProgressDialog(
                    f"Preparing {len(pending)} task(s)…", None, 0, 0, self
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

                # Deduplication: skip jobs whose (header_id, effective_mode)
                # pair has already been seen.  Without this, every draft that
                # targets the same header will re-run the same hashcat mode
                # against the same header file — identical work with no benefit.
                # effective_mode accounts for the 294xx→137xx substitution so
                # we don't run both the current and legacy variant.
                from portable_crypt_recovery.core.timestamps import utc_now_iso as _now
                from portable_crypt_recovery.services.hashcat.command_builder import (
                    _CURRENT_TO_LEGACY,
                )

                seen_header_mode: set[tuple[str, int]] = set()
                errors: list[str] = []
                for task in pending:
                    eff_mode = _CURRENT_TO_LEGACY.get(task.hashcat_mode, task.hashcat_mode) \
                        if ignore_cuda else task.hashcat_mode
                    key = (task.header_id, eff_mode)
                    if key in seen_header_mode:
                        task.status = "skipped"
                        task.updated_timestamp = _now()
                        continue
                    seen_header_mode.add(key)
                    try:
                        task.command_array = build_command_with_devices(
                            task, hashcat_exe, ws, device_ids,
                            use_optimized_kernels=use_opt,
                            use_cpu_opencl=use_cpu_opencl,
                            ignore_cuda=ignore_cuda,
                        )
                    except CommandBuilderError as exc:
                        errors.append(f"{task.task_id[:8]}: {exc}")

                if errors:
                    progress.close()
                    QMessageBox.warning(
                        self, "Command Build Errors",
                        f"{len(errors)} task(s) could not build a command:\n" + "\n".join(errors[:5])
                    )

                # Save updated command arrays back to disk
                atomic_write_json(queue_file, qs.to_dict())

                # Startup waste warning
                if pending:
                    from portable_crypt_recovery.services.hashcat.startup_estimator import (
                        queue_efficiency_report,
                    )
                    report = queue_efficiency_report(pending)
                    if report["warn"]:
                        _reply = QMessageBox.question(
                            self,
                            "Startup Overhead Warning",
                            report["message"] + "\n\nStart queue anyway?",
                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                            QMessageBox.StandardButton.Yes,
                        )
                        if _reply != QMessageBox.StandardButton.Yes:
                            progress.close()
                            self._update_button_states("stopped")
                            return

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
                    self.lbl_status.setText("Stopping after current task…")

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
                self.lbl_running.setText("No task running")
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

                task_ids = [it.data(256) for it in selected if it.data(256)]
                if not task_ids:
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
                for task_id in task_ids:
                    if task_id in qs.tasks:
                        qs.tasks[task_id].status = new_status
                        qs.tasks[task_id].updated_timestamp = utc_now_iso()
                        if new_status == "pending":
                            qs.tasks[task_id].command_array = []
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

                count = len(qs.task_order)
                if count == 0:
                    QMessageBox.information(self, "Clear Queue", "Queue is already empty.")
                    return

                reply = QMessageBox.question(
                    self, "Clear Queue",
                    f"Remove all {count} task(s) from the queue?\n\n"
                    "This cannot be undone. Tasks will need to be re-sent from the Jobs tab.",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No,
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return

                qs.tasks.clear()
                qs.task_order.clear()
                qs.current_running_task = None
                atomic_write_json(queue_file, qs.to_dict())
                state.job_count = 0
                self.txt_log.clear()
                self.lbl_log_header.setText("Select a task to view its log")
                self._refresh_list()

            def _copy_command(self) -> None:
                from PySide6.QtWidgets import QApplication

                item = self.job_list.currentItem()
                if item is None:
                    self.lbl_log_header.setText("Select a task first to copy its command.")
                    return

                import json

                from portable_crypt_recovery.app.app_state import get_app_state
                from portable_crypt_recovery.models.queue_state import QueueState

                task_id = item.data(256)
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

                task = qs.tasks.get(task_id)
                if task is None:
                    return

                # Prefer the command logged in the .log file — it is the exact
                # command that was passed to hashcat when the task actually ran.
                # The command_array stored in queue-state.json is rebuilt every
                # time the queue starts, so it reflects current settings, not
                # necessarily what produced this task's output.
                cmd_str: str | None = None
                source = "log"
                log_abs = state.workspace_root / task.log_path
                if log_abs.exists():
                    try:
                        for line in log_abs.read_text(
                            encoding="utf-8", errors="replace"
                        ).splitlines():
                            if line.startswith("command     : "):
                                cmd_str = line[len("command     : "):]
                                break
                    except OSError:
                        pass

                # Fall back to command_array (for pending/unrun tasks)
                if not cmd_str:
                    if not task.command_array:
                        self.lbl_log_header.setText(
                            "No command built yet — start the queue to generate commands."
                        )
                        return
                    # Quote any argument that contains a space so the result is
                    # pasteable into PowerShell / CMD without modification.
                    parts: list[str] = []
                    for arg in task.command_array:
                        parts.append(f'"{arg}"' if " " in arg else arg)
                    cmd_str = " ".join(parts)
                    source = "queue-state"

                clipboard = QApplication.clipboard()
                clipboard.setText(cmd_str)
                self.lbl_log_header.setText(
                    f"✓ Hashcat command copied ({source})"
                )

            # ------------------------------------------------------------------
            # Job selection → log viewer
            # ------------------------------------------------------------------

            def _on_job_selected(self, current, _previous) -> None:
                """Load and display log + command array for the selected task."""
                import json

                from portable_crypt_recovery.app.app_state import get_app_state
                from portable_crypt_recovery.models.queue_state import QueueState

                if current is None:
                    self.lbl_log_header.setText("Select a task to view its log")
                    self.txt_log.clear()
                    return

                task_id = current.data(256)
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

                task = qs.tasks.get(task_id)
                if task is None:
                    return

                # Track whether this is a fresh task selection or a poll refresh
                # for the same task that's already displayed.
                is_new_task = (task_id != self._log_task_id)
                self._log_task_id = task_id
                if is_new_task:
                    # User clicked a different task — reset follow state
                    self._log_follow = True

                # Terminal tasks never gain new log content after finishing, so
                # there is nothing to refresh on a poll tick.  Skip the reload
                # entirely so the user's scroll position is undisturbed.
                _TERMINAL = {"cracked", "exhausted", "failed", "skipped", "aborted"}
                if not is_new_task and task.status in _TERMINAL:
                    return

                # Save scroll position before setPlainText wipes it
                log_sb = self.txt_log.verticalScrollBar()
                saved_log_pos = log_sb.value()

                lines: list[str] = []

                # ---- CRACKED BANNER (top, hard to miss) ----
                if task.status == "cracked":
                    pw = task.cracked_password
                    if not pw:
                        # Fall back to reading the outfile directly
                        try:
                            outfile_abs = state.workspace_root / task.outfile_path
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
                    outfile_rel = task.outfile_path
                    lines.append(f"  OUTFILE  : {outfile_rel}")
                    lines.append("=" * 60)
                    lines.append("")

                # Command — read from the log file so it matches what actually ran.
                # Fall back to command_array for pending tasks that haven't run yet.
                log_abs = state.workspace_root / task.log_path
                displayed_cmd: str | None = None
                if log_abs.exists():
                    try:
                        for _line in log_abs.read_text(
                            encoding="utf-8", errors="replace"
                        ).splitlines():
                            if _line.startswith("command     : "):
                                displayed_cmd = _line[len("command     : "):]
                                break
                    except OSError:
                        pass
                if displayed_cmd is None and task.command_array:
                    displayed_cmd = " ".join(task.command_array)
                lines.append("=== COMMAND (actual hashcat invocation) ===")
                if displayed_cmd:
                    lines.append(displayed_cmd)
                else:
                    lines.append("(not yet built — send to queue and start to generate)")
                lines.append("")

                # Log file
                status_label = task.status.upper()
                self.lbl_log_header.setText(
                    f"Task {task_id[:8]}  |  mode {task.hashcat_mode}"
                    f"  |  [{status_label}]  |  log: {task.log_path}"
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

                # Block scrollbar signals around setPlainText + scroll positioning
                # so the internal Qt scroll-reset doesn't accidentally flip
                # _log_follow.  Only user-initiated wheel/drag events (which
                # arrive outside this block) should change follow state.
                log_sb.blockSignals(True)
                self.txt_log.setPlainText("\n".join(lines))
                # setPlainText resets scroll to 0; apply smart scroll:
                # - New task selected: scroll per status and (re-)enable following
                # - Same task, following enabled: scroll per status
                # - Same task, user scrolled away: restore their previous position
                if is_new_task or self._log_follow:
                    if task.status == "cracked":
                        log_sb.setValue(0)
                    else:
                        log_sb.setValue(log_sb.maximum())
                else:
                    # Restore user's reading position (content may have grown,
                    # so clamp to new maximum just in case)
                    log_sb.setValue(min(saved_log_pos, log_sb.maximum()))
                log_sb.blockSignals(False)

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

                # Update running task label
                current_id = qs.current_running_task
                if current_id and current_id in qs.tasks:
                    task = qs.tasks[current_id]
                    self.lbl_running.setText(
                        f"Running: {task.session_name}  mode={task.hashcat_mode}"
                    )
                else:
                    self.lbl_running.setText("No task running")

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

                # --- Group tasks by draft (preserving task order) ---
                # Build ordered list of (draft_id, draft_label) groups
                seen_drafts: list[tuple[str, str]] = []
                seen_draft_ids: set[str] = set()
                for task_id in qs.task_order:
                    task = qs.tasks.get(task_id)
                    if task is None:
                        continue
                    did = task.draft_id or ""
                    if did not in seen_draft_ids:
                        seen_draft_ids.add(did)
                        seen_drafts.append((did, task.draft_label or did or "Ungrouped tasks"))

                # Count status per draft for the header summary
                draft_status_counts: dict[str, dict[str, int]] = {}
                for task_id in qs.task_order:
                    task = qs.tasks.get(task_id)
                    if task is None:
                        continue
                    did = task.draft_id or ""
                    draft_status_counts.setdefault(did, {})
                    draft_status_counts[did][task.status] = (
                        draft_status_counts[did].get(task.status, 0) + 1
                    )

                # --- Render: group header then (optionally) tasks for each draft ---
                for draft_id, draft_label in seen_drafts:
                    # Count tasks and build a short status summary
                    sc = draft_status_counts.get(draft_id, {})
                    total = sum(sc.values())
                    parts = []
                    for st in ("running", "pending", "cracked", "exhausted",
                               "aborted", "failed", "paused", "skipped"):
                        n = sc.get(st, 0)
                        if n:
                            parts.append(f"{n} {st}")
                    summary = "  ·  ".join(parts) if parts else "0 tasks"

                    is_collapsed = draft_id in self._collapsed_drafts
                    triangle = "▶" if is_collapsed else "▼"
                    sep = QListWidgetItem(
                        f"{triangle}  {draft_label}  ({total} tasks: {summary})"
                    )
                    # ItemIsEnabled makes it clickable (for toggle) but not
                    # selectable as a regular task row.
                    sep.setFlags(Qt.ItemFlag.ItemIsEnabled)
                    sep.setData(257, draft_id)   # mark as group header
                    sep.setBackground(QBrush(QColor("#1e2a3a")))
                    sep.setForeground(QBrush(QColor("#88b8e8")))
                    self.job_list.addItem(sep)

                    if is_collapsed:
                        continue   # children hidden; skip child rows

                    for task_id in qs.task_order:
                        task = qs.tasks.get(task_id)
                        if task is None:
                            continue
                        if (task.draft_id or "") != draft_id:
                            continue
                        pim_label = f"PIM={task.pim_value}" if task.pim_mode == "custom" else "default PIM"
                        label = (
                            f"  [{task.status.upper():<14}]  "
                            f"mode={task.hashcat_mode}  {pim_label}  "
                            f"session={task.session_name}"
                        )
                        list_item = QListWidgetItem(label)
                        list_item.setData(256, task_id)
                        color = _bg.get(task.status)
                        if color:
                            list_item.setBackground(QBrush(color))
                        fg = _fg.get(task.status)
                        if fg:
                            list_item.setForeground(QBrush(fg))
                        self.job_list.addItem(list_item)
                        if task_id == current_data:
                            self.job_list.setCurrentItem(list_item)

                # Auto-scroll: jump to running task only when following;
                # otherwise restore the user's previous scroll position.
                # Block signals so setValue doesn't flip _job_list_follow.
                running_item = None
                for i in range(self.job_list.count()):
                    it = self.job_list.item(i)
                    if it and it.data(256) == qs.current_running_task:
                        running_item = it
                        break
                jsb = self.job_list.verticalScrollBar()
                jsb.blockSignals(True)
                if running_item and self._job_list_follow:
                    from PySide6.QtWidgets import QAbstractItemView
                    self.job_list.scrollToItem(
                        running_item, QAbstractItemView.ScrollHint.EnsureVisible
                    )
                else:
                    jsb.setValue(scroll_pos)
                jsb.blockSignals(False)

                # --- Progress bar + tasks remaining counter ---
                total_jobs = len(qs.task_order)
                pending_jobs = sum(
                    1 for tid in qs.task_order
                    if qs.tasks.get(tid) and qs.tasks[tid].status in ("pending", "running")
                )
                done_jobs = total_jobs - pending_jobs
                self.progress_bar.setValue(
                    int(done_jobs * 100 / total_jobs) if total_jobs > 0 else 0
                )
                if total_jobs > 0:
                    remaining_text = (
                        f"{pending_jobs} remaining  /  {total_jobs} total"
                        if pending_jobs > 0
                        else f"All {total_jobs} task(s) done"
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
