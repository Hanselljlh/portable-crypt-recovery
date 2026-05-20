"""Root pytest configuration.

Sets QT_QPA_PLATFORM=offscreen when no display platform is already configured
so that tests that instantiate Qt widgets run on headless CI runners (Linux).
"""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
