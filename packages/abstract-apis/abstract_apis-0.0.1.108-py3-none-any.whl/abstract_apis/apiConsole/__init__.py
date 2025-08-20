from .apiConsole import apiConsole
from .imports import QApplication,install_global_traps
import traceback,sys
def startApiConsole():
    try:
        install_global_traps()  # ← add this
        app = QApplication.instance() or QApplication(sys.argv)
        win = apiConsole()
        win.show()
        return app.exec()
    except Exception:
        print(traceback.format_exc())
        return 1

