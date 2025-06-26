# UI.py or core/app.py (wherever your PrimuxCore class lives)
from PySide6.QtWidgets import (
    QMainWindow, 
    QListWidget, 
    QListWidgetItem,
    QLabel, 
    QMenu,
    QTreeView,
    QMenu,
    QInputDialog, 
    QLineEdit
)
from PySide6.QtGui import QStandardItemModel, QStandardItem, QAction
from PySide6.QtCore import QSize, QModelIndex, Qt, QPoint
from pathlib import Path
import os

from core import ProjectContext
from ui.loader import load_ui_widget
from server import Server

class Primux(QMainWindow):
    UI_PATH_MAIN = "UI/Testui copy.ui"
    UI_PATH_ASSET = "UI/asset.ui"

    def __init__(self, context: ProjectContext):
        super().__init__()
        self.Server = Server()
        self.context_menu = QMenu(self)


        self.context = context
        self.init_ui()
        self.connect_signals()
        self.load_project_tree()
        self.Server.start()
        self.show()

    def init_ui(self):
        self.ui = load_ui_widget(self.UI_PATH_MAIN)
        self.setCentralWidget(self.ui)
        self.setFixedSize(1300, 510)


        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["text"])

        self.tw_project_tree: QTreeView = self.ui.findChild(QTreeView, "project_tree_view")
        self.tw_project_tree.setModel(self.model)
        self.tw_project_tree.setHeaderHidden(True)
        self.tw_project_tree.expandAll()
        self.tw_project_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tw_project_tree.customContextMenuRequested.connect(self.show_project_context_menu)
        self.tw_project_tree.setStyleSheet("""
            QTreeView::item {
                height: 30px;
                padding: 3px;
            }
        """)
        self.wl_step_list: QListWidget = self.ui.findChild(QListWidget, "asset_step_list")

    def connect_signals(self):
        self.tw_project_tree.clicked.connect(self.load_asset_steps)

    def get_user_input(self, parent = None):
        text, ok = QInputDialog.getText(
            parent,
            "New Folder",
            "Enter folder Name:",
            QLineEdit.Normal
        )
        if ok and text:
            return text
        return None

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
        self.wl_step_list.clear()

        index: QModelIndex = self.tw_project_tree.currentIndex()
        if not index.isValid():
            return

        # Reconstruct folder path
        item = self.model.itemFromIndex(index)
        parts = []
        while item:
            parts.insert(0, item.text())
            item = item.parent()

        selected_path = self.context.assets_path.joinpath(*parts)

        if not selected_path.is_dir():
            return

        for name in sorted(os.listdir(selected_path)):
            full_path = selected_path / name
            if full_path.is_dir() and not name.startswith("_"):
                self.add_asset_item(name, self.wl_step_list)

    def load_project_tree(self):
        self.model.clear()
        assets_root = self.context.assets_path

        def add_folder_to_item(parent_item, folder_path: Path):
            for name in sorted(os.listdir(folder_path)):
                full_path = folder_path / name
                if not full_path.is_dir():
                    continue
                item = QStandardItem(name)
                item.setEditable(False)
                parent_item.appendRow(item)
                add_folder_to_item(item, full_path)

        for root_folder in sorted(os.listdir(assets_root)):
            root_path = assets_root / root_folder
            if not root_path.is_dir():
                continue

            root_item = QStandardItem(root_folder)
            root_item.setEditable(False)
            self.model.appendRow(root_item)
            add_folder_to_item(root_item, root_path)
    
    def create_new_folder(self):

        folder_name = self.get_user_input(None)

        index = self.tw_project_tree.currentIndex()
        if index is None:
            return
        
        print(f"index: {index}")
        item_path = self.get_item_path_str(index)
        if Path is not None:
            folder_path = Path(item_path) / folder_name
        else:
            folder_path = folder_name
        self.context.create_folder(folder_path)
        self.load_project_tree()

    def delete_folder(self):
        index = self.tw_project_tree.currentIndex()
        if index is None:
            return
        folder_path = self.get_item_path_str(index)
        self.context.delete_directory(folder_path)
        self.load_project_tree()

    def get_item_path(self,index):
        path = []
        while index.isValid():
            item = index.model().itemFromIndex(index)
            path.insert(0, item.text())  # Prepend to keep order from root to leaf
            index = index.parent()
        return path

    def get_item_path_str(self,index, separator="/"):
        return separator.join(self.get_item_path(index))

    def show_project_context_menu(self, position: QPoint):
        
        index = self.tw_project_tree.indexAt(position)

        menu = QMenu()

        rename_action = QAction("Rename", self)
        delete_action = QAction("Delete", self)
        new_folder_action = QAction("New Folder", self)
        new_asset_action = QAction("New Asset", self)

        # Connect to appropriate methods
        rename_action.triggered.connect(lambda: print("Rename"))
        delete_action.triggered.connect(self.delete_folder)
        new_folder_action.triggered.connect(self.create_new_folder)
        new_asset_action.triggered.connect(lambda: print("New Asset"))

        menu.addAction(rename_action)
        menu.addAction(delete_action)
        menu.addSeparator()
        menu.addAction(new_folder_action)
        menu.addAction(new_asset_action)

        menu.exec(self.tw_project_tree.viewport().mapToGlobal(position))