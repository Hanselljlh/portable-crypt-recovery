"""Queue view — list of queued jobs and queue controls."""

from __future__ import annotations


class QueueView:  # pragma: no cover
    """Queued job list with Start/Pause/Stop/Resume/Skip/Restart controls."""

    def __new__(cls):
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
                layout = QVBoxLayout(self)

                # Queue controls
                controls_group = QGroupBox("Queue Controls")
                controls_layout = QHBoxLayout(controls_group)
                self.btn_start = QPushButton("Start Queue")
                self.btn_pause_now = QPushButton("Pause Now")
                self.btn_pause_after = QPushButton("Pause After Current")
                self.btn_stop_save = QPushButton("Stop and Save")
                self.btn_stop_discard = QPushButton("Stop and Discard")
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

                # Progress
                self.lbl_running = QLabel("No job running")
                self.progress_bar = QProgressBar()
                self.progress_bar.setRange(0, 100)
                self.progress_bar.setValue(0)
                layout.addWidget(self.lbl_running)
                layout.addWidget(self.progress_bar)

                # Job list
                self.job_list = QListWidget()
                layout.addWidget(self.job_list, 1)

                # Wire buttons (stubs — actual logic needs queue_runner)
                self.btn_start.clicked.connect(self._start_queue)
                self.btn_pause_now.clicked.connect(self._pause_now)
                self.btn_stop_save.clicked.connect(self._stop_save)
                self.btn_stop_discard.clicked.connect(self._stop_discard)

            def _start_queue(self) -> None:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.information(self, "Queue", "Open a workspace and configure Hashcat first.")

            def _pause_now(self) -> None:
                pass

            def _stop_save(self) -> None:
                pass

            def _stop_discard(self) -> None:
                pass

            def update_progress(self, percent: float, description: str = "") -> None:
                self.progress_bar.setValue(int(percent))
                if description:
                    self.lbl_running.setText(description)

        return _QueueView()
