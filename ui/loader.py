# ui/loader.py

from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QFile

def load_ui_widget(path: str) -> QWidget:
    """
    Load a .ui file and return its root widget.
    """
    loader = QUiLoader()
    file = QFile(path)
    if not file.open(QFile.ReadOnly):
        raise IOError(f"Cannot open UI file: {path}")
    widget = loader.load(file)
    file.close()
    return widget
