import os
from PySide6.QtWidgets import (
    QMainWindow, QPushButton, QListWidget, QListWidgetItem,
    QLineEdit, QLabel, QWidget, QTreeView
)
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtCore import QSize, QFile, QModelIndex
from AssetDelegate import AssetDelegate
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
    UI_PATH_MAIN = "UI/Testui copy.ui"
    UI_PATH_ASSET = "UI/asset.ui"

    def __init__(self):
        super().__init__()
        self.init_ui()
        self.connect_signals()

    def init_ui(self):
        self.ui = load_ui_widget(self.UI_PATH_MAIN)
        self.setCentralWidget(self.ui)
        self.setFixedSize(1212, 510)

        self.button: QPushButton = self.ui.findChild(QPushButton, "bt_start_server")
        self.tree_view: QTreeView = self.ui.findChild(QTreeView, "treeView")
        self.asset_step_list: QListWidget = self.ui.findChild(QListWidget, "asset_step_list")
        self.port: QLineEdit = self.ui.findChild(QLineEdit, "inpt_port")
        self.status: QLabel = self.ui.findChild(QLabel, "out_status")
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["Assets"])
        self.tree_view.setModel(self.model)
        self.tree_view.setHeaderHidden(True)
        self.tree_view.expandAll()
        self.tree_view.setStyleSheet("""
            QTreeView::item {
                height: 30px;
                padding: 3px;
            }
        """)


    def connect_signals(self):
        self.button.clicked.connect(self.start_server)
        self.tree_view.clicked.connect(self.load_asset_steps)

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

    def load_asset_steps(self):
        self.asset_step_list.clear()

        # Get the selected index from the tree view
        index: QModelIndex = self.tree_view.currentIndex()
        if not index.isValid():
            return

        # Build the full path by walking up the index tree
        item = self.model.itemFromIndex(index)
        parts = []
        while item:
            parts.insert(0, item.text())
            item = item.parent()
        
        selected_path = os.path.join(self.root_path, "_assets", *parts)

        if not os.path.isdir(selected_path):
            return

        # Add only subfolders (steps)
        for name in sorted(os.listdir(selected_path)):
            full_path = os.path.join(selected_path, name)
            if os.path.isdir(full_path) and not name.startswith("_"):
                self.add_asset_item(name, self.asset_step_list)

    def load_project(self, path):
        path = os.path.join(path, "_assets")
        if not os.path.isdir(path):
            print(f"Path '{path}' is not a valid directory.")
            return

        self.model.clear()

        def add_folder_to_item(parent_item, folder_path):
            for name in sorted(os.listdir(folder_path)):
                full_path = os.path.join(folder_path, name)
                if not os.path.isdir(full_path):
                    continue
            
                if name.startswith("_"):
                    continue
                
                item = QStandardItem(name)
                item.setEditable(False)
                parent_item.appendRow(item)

                # Recurse into subfolders
                add_folder_to_item(item, full_path)

        # Top-level folders under _assets
        for root_folder in sorted(os.listdir(path)):
            root_path = os.path.join(path, root_folder)
            if not os.path.isdir(root_path):
                continue
            
            root_item = QStandardItem(root_folder)
            root_item.setEditable(False)
            self.model.appendRow(root_item)

            # Recurse into subfolders
            add_folder_to_item(root_item, root_path)
