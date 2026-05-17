"""Dashboard view — shows workspace overview and status."""

from __future__ import annotations


class DashboardView:  # pragma: no cover
    """Dashboard showing workspace name, Hashcat status, counts, and recent activity."""

    def __new__(cls, app_state=None):
        from PySide6.QtWidgets import (
            QGroupBox,
            QHBoxLayout,
            QLabel,
            QListWidget,
            QPushButton,
            QSizePolicy,
            QVBoxLayout,
            QWidget,
        )
        from PySide6.QtCore import QTimer

        class _DashboardView(QWidget):
            def __init__(self, app_state=None) -> None:
                super().__init__()
                layout = QVBoxLayout(self)

                # Status row
                status_group = QGroupBox("Workspace")
                status_layout = QVBoxLayout(status_group)
                self.lbl_workspace = QLabel("No workspace open")
                self.lbl_hashcat = QLabel("Hashcat: Not configured")
                status_layout.addWidget(self.lbl_workspace)
                status_layout.addWidget(self.lbl_hashcat)
                layout.addWidget(status_group)

                # Counts row
                counts_group = QGroupBox("Status")
                counts_layout = QHBoxLayout(counts_group)
                self.lbl_targets = QLabel("Targets: 0")
                self.lbl_headers = QLabel("Headers: 0")
                self.lbl_jobs = QLabel("Jobs: 0")
                counts_layout.addWidget(self.lbl_targets)
                counts_layout.addWidget(self.lbl_headers)
                counts_layout.addWidget(self.lbl_jobs)
                layout.addWidget(counts_group)

                # Hashcat warning button
                self.btn_setup_hashcat = QPushButton("Open Settings → Hashcat Setup")
                self.btn_setup_hashcat.setVisible(True)
                self.btn_setup_hashcat.clicked.connect(self._go_to_settings)
                layout.addWidget(self.btn_setup_hashcat)

                # Recent activity
                activity_group = QGroupBox("Recent Activity")
                activity_layout = QVBoxLayout(activity_group)
                self.activity_list = QListWidget()
                activity_layout.addWidget(self.activity_list)
                layout.addWidget(activity_group, 1)

                # Auto-refresh every 5 seconds so counts stay current
                self._timer = QTimer(self)

                self._timer.setInterval(5000)
                self._timer.timeout.connect(self._auto_refresh)
                self._timer.start()

                self._auto_refresh()

            def _go_to_settings(self) -> None:
                # Walk up to the QMainWindow and switch nav to Settings (index 6)
                win = self.window()
                if hasattr(win, "nav"):
                    win.nav.setCurrentRow(6)

            def _auto_refresh(self) -> None:
                from portable_crypt_recovery.app.app_state import get_app_state
                self.refresh(get_app_state())

            def refresh(self, app_state) -> None:
                if app_state.workspace_root:
                    self.lbl_workspace.setText(
                        f"Workspace: {app_state.workspace_name} ({app_state.workspace_root})"
                    )
                else:
                    self.lbl_workspace.setText("No workspace open")

                if app_state.is_hashcat_ready():
                    self.lbl_hashcat.setText(
                        f"Hashcat: Ready ({app_state.hashcat_setup.version_string})"
                    )
                    self.btn_setup_hashcat.setVisible(False)
                else:
                    self.lbl_hashcat.setText("Hashcat: Not configured — see Settings")
                    self.btn_setup_hashcat.setVisible(True)

                self.lbl_targets.setText(f"Targets: {app_state.target_count}")
                self.lbl_headers.setText(f"Headers: {app_state.header_count}")
                self.lbl_jobs.setText(f"Jobs: {app_state.job_count}")

                # Populate recent activity from queue jobs
                if app_state.workspace_root:
                    self._load_recent_activity(app_state.workspace_root)

            def _load_recent_activity(self, workspace_root) -> None:
                import json
                from PySide6.QtWidgets import QListWidgetItem
                from portable_crypt_recovery.models.queue_state import QueueState

                self.activity_list.clear()
                queue_file = workspace_root / "queue" / "queue-state.json"
                if not queue_file.exists():
                    return
                try:
                    qs = QueueState.from_dict(
                        json.loads(queue_file.read_text(encoding="utf-8"))
                    )
                except Exception:
                    return

                # Show last 20 jobs by order, newest first
                recent = list(reversed(qs.queue_order[-20:]))
                for job_id in recent:
                    job = qs.jobs.get(job_id)
                    if job is None:
                        continue
                    self.activity_list.addItem(
                        f"[{job.status.upper():<14}]  mode={job.hashcat_mode}  "
                        f"session={job.session_name}"
                    )

        return _DashboardView(app_state)
