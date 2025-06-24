from PySide6.QtWidgets import (
    QMainWindow, QPushButton, QListWidget, QListWidgetItem,
    QLineEdit, QLabel
)
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QSize, QFile
from server import start
import os

def load_asset_wgt(path):
    loader = QUiLoader()
    file = QFile(path)
    file.open(QFile.ReadOnly)
    widget = loader.load(file)
    file.close()
    return widget


class OpenAPIWidget(QMainWindow):
    def __init__(self):
        super().__init__()

        loader = QUiLoader()
        self.ui = loader.load("UI/Testui.ui", None)
        self.setCentralWidget(self.ui)
        self.setFixedSize(1212, 510)

        self.button = self.ui.findChild(QPushButton, "bt_start_server")
        self.asset_list = self.ui.findChild(QListWidget, "asset_list")
        self.port = self.ui.findChild(QLineEdit, "inpt_port")
        self.status = self.ui.findChild(QLabel, "out_status")

        self.button.clicked.connect(self.start_server)

    def start_server(self):
        port = self.port.text()
        try:
            start(int(port))
            self.status.setStyleSheet("color: green;")
            self.status.setText("Running")
        except Exception as e:
            print(e)
            self.status.setStyleSheet("color: red;")
            self.status.setText("Failed to start!")

    def load_asset(self, asset_name):
        item = QListWidgetItem()
        item.setSizeHint(QSize(220, 35))
        asset_widget = load_asset_wgt("UI/asset.ui")

        # Set label inside custom widget if it exists
        label = asset_widget.findChild(QLabel, "asset_name")
        if label:
            label.setText(asset_name)

        self.asset_list.addItem(item)
        self.asset_list.setItemWidget(item, asset_widget)

    def load_directory(self, path):
        if not os.path.isdir(path):
            print(f"Path '{path}' is not a valid directory.")
            return

        folders = [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]
        for folder in folders:
            self.load_asset(folder)
