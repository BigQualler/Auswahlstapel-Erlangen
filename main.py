from aqt import mw
from aqt.qt import *
from aqt.utils import qconnect
from .ui.main_window import SelectionWindow

def open_window():
    window = SelectionWindow(mw)
    window.show()

def init_addon():
    action = QAction("Auswahlstapel Erlangen", mw)
    qconnect(action.triggered, open_window)
    mw.form.menuTools.addAction(action)
