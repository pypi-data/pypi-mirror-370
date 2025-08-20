from .imports import QObject,pyqtSignal
from .initFuncs import initFuncs
class RequestWorker(QObject):
    success = pyqtSignal(str)
    failure = pyqtSignal(str)

    def __init__(self, method: str, url: str, headers: dict, params: dict, timeout: float = 15.0):
        super().__init__()
        self.method  = method
        self.url     = url
        self.headers = headers or {}
        self.params  = params or {}
        self.timeout = timeout
RequestWorker = initFuncs(RequestWorker)

