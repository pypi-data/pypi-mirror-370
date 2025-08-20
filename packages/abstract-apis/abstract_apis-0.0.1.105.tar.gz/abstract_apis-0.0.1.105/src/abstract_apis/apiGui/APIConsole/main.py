from .imports import *
from .initFuncs import *

class APIConsole(QWidget):
    def __init__(self):
        try:
            super().__init__()                      # ← fixed
            self.setWindowTitle("API Console for abstract_apis")
            self.api_prefix = "/api"
            self.resize(800, 900)
            self.config_cache = {}
            self._build_ui()
            self._setup_logging()
        except Exception as e:
            logger.info(f"{e}")

APIConsole = initFuncs(APIConsole)
