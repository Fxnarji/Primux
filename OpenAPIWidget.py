import os
from PySide6.QtWidgets import (
    QMainWindow, QPushButton, QListWidget, QListWidgetItem,
    QLineEdit, QLabel, QWidget
)
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QSize, QFile
from server import start


def load_ui_widget(path: str) -> QWidget:
    """Load a .ui file and return its root widget."""
    loader = QUiLoader()
    file = QFile(path)
    if not file.open(QFile.ReadOnly):
        raise IOError(f"Cannot open UI file: {path}")
    widget = loader.load(file)
    file.close()
    return widget


class OpenAPIWidget(QMainWindow):
    UI_PATH_MAIN = "UI/Testui.ui"
    UI_PATH_ASSET = "UI/asset.ui"
    path = ''

    def __init__(self):
        super().__init__()
        self.init_ui()
        self.connect_signals()

    def init_ui(self):
        self.ui = load_ui_widget(self.UI_PATH_MAIN)
        self.setCentralWidget(self.ui)
        self.setFixedSize(1212, 510)

        self.button: QPushButton = self.ui.findChild(QPushButton, "bt_start_server")
        self.asset_list: QListWidget = self.ui.findChild(QListWidget, "asset_list")
        self.asset_step_list: QListWidget = self.ui.findChild(QListWidget, "asset_step_list")
        self.port: QLineEdit = self.ui.findChild(QLineEdit, "inpt_port")
        self.status: QLabel = self.ui.findChild(QLabel, "out_status")

    def connect_signals(self):
        self.button.clicked.connect(self.start_server)
        self.asset_list.currentItemChanged.connect(self.load_asset_steps)

    def start_server(self):
        try:
            port = int(self.port.text())
            start(port)
            self.status.setStyleSheet("color: green;")
            self.status.setText("Running")
        except Exception as e:
            print(e)
            self.status.setStyleSheet("color: red;")
            self.status.setText("Failed to start!")

    def add_asset_item(self, name: str, target_list: QListWidget):
        item = QListWidgetItem()
        item.setSizeHint(QSize(100, 35))

        widget = load_ui_widget(self.UI_PATH_ASSET)
        label = widget.findChild(QLabel, "asset_name")
        if label:
            label.setText(name)

        target_list.addItem(item)
        target_list.setItemWidget(item, widget)

    def load_directory(self):
        if not os.path.isdir(self.path):
            print(f"Path '{self.path}' is not a valid directory.")
            return

        for folder in os.listdir(self.path):
            full_path = os.path.join(self.path, folder)
            if os.path.isdir(full_path):
                self.add_asset_item(folder, self.asset_list)

    def load_asset_steps(self):
        self.asset_step_list.clear()

        current_item = self.asset_list.currentItem()
        if not current_item:
            return

        widget = self.asset_list.itemWidget(current_item)
        label = widget.findChild(QLabel, "asset_name") if widget else None
        if not label:
            return

        current_step_dir = os.path.join(self.path, label.text())
        if not os.path.isdir(current_step_dir):
            return

        for step in os.listdir(current_step_dir):
            if os.path.isdir(os.path.join(current_step_dir, step)):
                self.add_asset_item(step, self.asset_step_list)
