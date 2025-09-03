# ui/loader.py

import sys, os
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QFile
from PySide6.QtWidgets import QLabel
from enum import Enum
from PySide6.QtGui import QPixmap


class AssetIcon(Enum):
    PLACEHOLDER = ":/images/Placeholder.png"

    BLEND = ":/images/icon_blender.png"
    SPP = ":/images/icon_painter.png"
    FBX = ":/images/icon_fbx.png"
    PUR = ":/images/icon_pureref.png"


    RENDER = ":/images/icon_render.png"
    ANIM = ":/images/icon_anim.png"
    LIGHTING = ":/images/icon_lighting.png"
    VFX = ":/images/icon_vfx.png"
    ENVIRONMENT = ":/images/icon_environment.png"


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and PyInstaller """
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def load_ui_widget(path: str) -> QWidget:
    loader = QUiLoader()
    ui_file = QFile(resource_path(path))
    if not ui_file.open(QFile.ReadOnly):
        raise IOError(f"Cannot open UI file: {path}")
    widget = loader.load(ui_file)
    ui_file.close()
    return widget

def create_asset_widget(parent, name: str, icon: AssetIcon = AssetIcon.PLACEHOLDER) -> QWidget:
    widget = load_ui_widget("UI/asset.ui")
    label_name = widget.findChild(QLabel, "asset_name")
    if label_name:
        label_name.setText(name)

    label_icon = widget.findChild(QLabel, "label")
    if label_icon:
        set_asset_icon(label_icon, icon)

    return widget

def set_asset_icon(label: QLabel, icon: AssetIcon):
    """Set the pixmap of a QLabel to the selected AssetIcon."""
    pixmap = QPixmap(icon.value)
    label.setPixmap(pixmap)
    label.setScaledContents(True)
