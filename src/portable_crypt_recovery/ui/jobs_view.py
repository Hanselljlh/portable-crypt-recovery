"""Jobs view — list of job drafts and expand button."""

from __future__ import annotations


class JobsView:  # pragma: no cover
    """List of job drafts with mode/PIM/keyfile/password source details."""

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
                self.btn_expand = QPushButton("Expand to Queue Jobs")
                toolbar.addWidget(self.btn_expand)
                toolbar.addStretch()
                layout.addLayout(toolbar)

                self.job_list = QListWidget()
                layout.addWidget(self.job_list, 1)

                info = QLabel(
                    "Configure hash mode, PIM, keyfile, and password source "
                    "for each target, then expand into queue jobs."
                )
                info.setWordWrap(True)
                layout.addWidget(info)

                self.btn_expand.clicked.connect(self._expand_jobs)

            def _expand_jobs(self) -> None:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.information(
                    self,
                    "Expand Jobs",
                    "Select a job draft and configure settings to expand into queue jobs.",
                )

        return _JobsView()
