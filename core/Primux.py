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
from .util import ConfigHelper
from ui.loader import load_ui_widget
from server import Server

class Primux(QMainWindow):
    UI_PATH_MAIN = "UI/Testui copy.ui"
    UI_PATH_ASSET = "UI/asset.ui"

    def __init__(self, context: ProjectContext):
        super().__init__()
        self.Server = Server()
        self.context_menu = QMenu(self)
        self.config = ConfigHelper()


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
        self.wl_step_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.wl_step_list.customContextMenuRequested.connect(self.show_steps_context_menu)

    def connect_signals(self):
        self.tw_project_tree.clicked.connect(self.load_asset_steps)

    def get_user_input(self, name = "Folder", parent = None):
        text, ok = QInputDialog.getText(
            parent,
            f"New {name}",
            f"Enter {name} Name:",
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
        steps = self.config.get("steps")

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
            if full_path.is_dir() and name.startswith("_"):
                displayname = steps.get(name, "Error")
                self.add_asset_item(displayname, self.wl_step_list)

    def load_project_tree(self):
        self.model.clear()
        assets_root = self.context.assets_path

        def add_folder_to_item(parent_item, folder_path: Path):
            for name in sorted(os.listdir(folder_path)):
                if name.startswith("_"):
                    continue
                full_path = folder_path / name
                if not full_path.is_dir():
                    continue
                item = QStandardItem(name)
                item.setEditable(False)
                parent_item.appendRow(item)
                add_folder_to_item(item, full_path)


        for folder in sorted(os.listdir(assets_root)):
            root_path = assets_root / folder
            if folder.startswith("_") or not root_path.is_dir():
                continue

            root_item = QStandardItem(folder)
            root_item.setEditable(False)
            self.model.appendRow(root_item)
            add_folder_to_item(root_item, root_path)

    def get_item_path(self,index):
        path = []
        while index.isValid():
            item = index.model().itemFromIndex(index)
            path.insert(0, item.text())  # Prepend to keep order from root to leaf
            index = index.parent()
        return path

    def get_item_path_str(self,index, separator="/"):
        return separator.join(self.get_item_path(index))



# TREE VIEW CONTEXT MENU

    def create_new_folder(self):
        folder_name = self.get_user_input(None)
        if not folder_name:
            return

        index = self.tw_project_tree.currentIndex()
        if index.isValid():
            parent_path = self.get_item_path_str(index)
        else:
            parent_path = self.context.assets_path
        new_folder_path = Path(parent_path) / folder_name


        # Create the folder in the filesystem or data context
        self.context.create_folder(new_folder_path)

        # Add new item to the tree model
        model = self.tw_project_tree.model()
        parent_item = model.itemFromIndex(index)

        if parent_item is None:
            self.load_project_tree()

        # Optional: sort children alphabetically (can be omitted)
        new_item = QStandardItem(folder_name)
        new_item.setEditable(False)
        parent_item.appendRow(new_item)

        # Expand the parent so the new item becomes visible
        self.tw_project_tree.expand(index)

    def create_new_asset(self):
        name = self.get_user_input(name = "Asset")
        index = self.tw_project_tree.currentIndex()
        if index is None:
            return
        folder_path = self.get_item_path_str(index) 
        self.context.create_Asset(folder_path, name)

    def delete_folder(self):
        index = self.tw_project_tree.currentIndex()
        if index is None:
            return
        folder_path = self.get_item_path_str(index)
        self.context.delete_directory(folder_path)

        model = self.tw_project_tree.model()
        item = model.itemFromIndex(index)

        if item:
            parent = item.parent()
            if parent:
                parent.removeRow(item.row())
            else:
                model.removeRow(item.row())

    def rename_folder(self):
        new_name = self.get_user_input(None)
        index = self.tw_project_tree.currentIndex()
        if index is None:
            return
        folder_path = self.get_item_path_str(index)
        self.context.delete_directory(folder_path)

        self.context.rename_folder(folder_path, new_name)

    def show_project_context_menu(self, position: QPoint):
        
        index = self.tw_project_tree.indexAt(position)

        menu = QMenu()

        rename_action = QAction("Rename", self)
        delete_action = QAction("Delete", self)
        new_folder_action = QAction("New Folder", self)
        new_asset_action = QAction("New Asset", self)

        # Connect to appropriate methods
        rename_action.triggered.connect(self.rename_folder)
        delete_action.triggered.connect(self.delete_folder)
        new_folder_action.triggered.connect(self.create_new_folder)
        new_asset_action.triggered.connect(self.create_new_asset)

        menu.addAction(rename_action)
        menu.addAction(delete_action)
        menu.addSeparator()
        menu.addAction(new_folder_action)
        menu.addAction(new_asset_action)

        menu.exec(self.tw_project_tree.viewport().mapToGlobal(position))


# STEPS CONTEXT MENU

    def create_step(self, name):
        index = self.tw_project_tree.currentIndex()
        path = self.get_item_path_str(index)
        print(path)
        new_folder_path = self.context.assets_path / path / name
        print(new_folder_path)
        self.context.create_folder(new_folder_path)
        self.load_asset_steps()

    def show_steps_context_menu(self, position: QPoint):

        menu = QMenu()
        steps = self.config.get("steps")
        print(steps)

        default_action = QAction("test", self)
        menu.addAction(default_action)
        print("context menu open!")
        for suffix, step_name in steps.items():
            print("test")
            action = QAction(step_name,menu)
            action.triggered.connect(lambda checked=False, s=suffix: self.create_step(s))
            menu.addAction(action)
        
        menu.exec(self.wl_step_list.viewport().mapToGlobal(position))
