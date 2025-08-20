from .imports import logging
from .initFuncs import initFuncs

# ─── Logging Handler ──────────────────────────────────────────────────────
class QTextEditLogger(logging.Handler):
    def __init__(self, widget):
        super().__init__()
        self.widget = widget
        self.widget.setReadOnly(True)
        self.api_prefix = "/api" # default; will update on detect or user edit
QTextEditLogger = initFuncs(QTextEditLogger)

