from .APIConsole import APIConsole
from .imports import *
def startGui():
    try:
        install_global_traps()  # ← add this
        app = QApplication.instance() or QApplication(sys.argv)
        win = APIConsole()
        win.show()
        return app.exec()
    except Exception:
        print(traceback.format_exc())
        return 1

