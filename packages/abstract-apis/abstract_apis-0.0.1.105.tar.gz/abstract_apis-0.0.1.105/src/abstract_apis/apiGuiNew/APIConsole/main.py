from .initFuncs import initFuncs
from .imports import QWidget
# ─── Main GUI ─────────────────────────────────────────────────────────────
class APIConsole(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("API Console for abstract_apis")
        self.api_prefix = "/api" # default; will update on detect or user edit
        self.resize(800, 900)
        self.config_cache = {} # cache per-endpoint settings
        self._build_ui()
        self._setup_logging()
APIConsole = initFuncs(APIConsole)
