# ui/loader.py

from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QFile
from PySide6.QtWidgets import QLabel

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

def create_asset_widget(self, name: str) -> QLabel:
        """
        Load asset.ui and set the asset_name label.
        """
        widget = load_ui_widget(self.UI_PATH_ASSET)
        label: QLabel = widget.findChild(QLabel, "asset_name")
        if label:
            label.setText(name)
        return widget
