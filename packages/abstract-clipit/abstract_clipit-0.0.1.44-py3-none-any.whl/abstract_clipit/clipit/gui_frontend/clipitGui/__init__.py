from .main import DragDropWithFileBrowser
from .imports import QApplication,install_global_traps
import traceback,sys
def startClipit():
    try:
        install_global_traps()  # ← add this
        app = QApplication(sys.argv)
        win = DragDropWithFileBrowser()
        win.show()
        return app.exec()
    except Exception:
        print(traceback.format_exc())
        return 1

