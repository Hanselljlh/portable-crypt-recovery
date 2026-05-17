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
                self._runner = None  # active QueueRunner or None
                layout = QVBoxLayout(self)

                # Queue controls
                controls_group = QGroupBox("Queue Controls")
                controls_layout = QHBoxLayout(controls_group)
                self.btn_start = QPushButton("Start Queue")
                self.btn_pause_now = QPushButton("Pause Now")
                self.btn_pause_after = QPushButton("Pause After Current")
                self.btn_stop_save = QPushButton("Stop & Save")
                self.btn_stop_discard = QPushButton("Stop & Discard")
                self.btn_resume = QPushButton("Resume")
                self.btn_skip = QPushButton("Skip Selected")
                self.btn_restart = QPushButton("Restart Selected")
                for btn in [
                    self.btn_start, self.btn_pause_now, self.btn_pause_after,
                    self.btn_stop_save, self.btn_stop_discard, self.btn_resume,
                    self.btn_skip, self.btn_restart,
                ]:
                    controls_layout.addWidget(btn)
                layout.addWidget(controls_group)

                # Status row
                self.lbl_status = QLabel("Queue stopped")
                self.lbl_running = QLabel("No job running")
                self.progress_bar = QProgressBar()
                self.progress_bar.setRange(0, 100)
                self.progress_bar.setValue(0)
                status_row = QHBoxLayout()
                status_row.addWidget(self.lbl_status)
                status_row.addStretch()
                status_row.addWidget(self.lbl_running)
                layout.addLayout(status_row)
                layout.addWidget(self.progress_bar)

                # Job list
                self.job_list = QListWidget()
                layout.addWidget(self.job_list, 1)

                # Wire buttons
                self.btn_start.clicked.connect(self._start_queue)
                self.btn_pause_now.clicked.connect(self._pause_now)
                self.btn_pause_after.clicked.connect(self._pause_after)
                self.btn_stop_save.clicked.connect(self._stop_save)
                self.btn_stop_discard.clicked.connect(self._stop_discard)
                self.btn_resume.clicked.connect(self._resume)
                self.btn_skip.clicked.connect(self._skip_selected)
                self.btn_restart.clicked.connect(self._restart_selected)

                # Poll timer
                self._timer = QTimer(self)
                self._timer.setInterval(2000)
                self._timer.timeout.connect(self._poll_status)

                self._refresh_list()
                self._update_button_states(queue_status="stopped")

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

                # Build command arrays for all pending jobs
                device_ids = state.hashcat_setup.selected_compute_devices or None
                errors: list[str] = []
                for job in pending:
                    if job.command_array:
                        continue  # already built
                    try:
                        job.command_array = build_command_with_devices(
                            job, hashcat_exe, ws, device_ids
                        )
                    except CommandBuilderError as exc:
                        errors.append(f"{job.job_id[:8]}: {exc}")

                if errors:
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
                    self._runner = None
                    QMessageBox.warning(
                        self, "Queue Locked",
                        "Another instance may be running (lock file exists). "
                        "Delete queue/queue.lock if you are sure no other instance is active."
                    )
                    return

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

                item = self.job_list.currentItem()
                if item is None:
                    return

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

                if job_id in qs.jobs:
                    from portable_crypt_recovery.core.timestamps import utc_now_iso
                    qs.jobs[job_id].status = new_status
                    qs.jobs[job_id].updated_timestamp = utc_now_iso()
                    atomic_write_json(queue_file, qs.to_dict())
                    self._refresh_list()

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

            def _refresh_list(self) -> None:
                import json

                from PySide6.QtWidgets import QListWidgetItem

                from portable_crypt_recovery.app.app_state import get_app_state
                from portable_crypt_recovery.models.queue_state import QueueState

                current_data = None
                item = self.job_list.currentItem()
                if item:
                    current_data = item.data(256)

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

                for job_id in qs.queue_order:
                    job = qs.jobs.get(job_id)
                    if job is None:
                        continue
                    pim_label = f"PIM={job.pim_value}" if job.pim_mode == "custom" else "default PIM"
                    label = (
                        f"[{job.status.upper():<14}]  "
                        f"mode={job.hashcat_mode}  {pim_label}  "
                        f"session={job.session_name}"
                    )
                    list_item = QListWidgetItem(label)
                    list_item.setData(256, job_id)
                    # Color by status
                    from PySide6.QtGui import QColor
                    color_map = {
                        "pending": None,
                        "running": QColor("#d4edda"),
                        "paused": QColor("#fff3cd"),
                        "cracked": QColor("#c3e6cb"),
                        "exhausted": QColor("#f8d7da"),
                        "failed": QColor("#f8d7da"),
                        "stopped_saved": QColor("#ffeeba"),
                        "skipped": QColor("#e2e3e5"),
                    }
                    color = color_map.get(job.status)
                    if color:
                        list_item.setBackground(color)
                    self.job_list.addItem(list_item)
                    if job_id == current_data:
                        self.job_list.setCurrentItem(list_item)

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

            def update_progress(self, percent: float, description: str = "") -> None:
                self.progress_bar.setValue(int(percent))
                if description:
                    self.lbl_running.setText(description)

        return _QueueView()
