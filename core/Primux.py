# UI.py or core/app.py
from PySide6.QtWidgets import (
    QMainWindow,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QTreeView,
    QPushButton,
)
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtCore import Qt, QModelIndex
from pathlib import Path

from core import ProjectContext
from .util import ConfigHelper
from ui.loader import load_ui_widget, create_asset_widget
import subprocess, sys, os


class Primux(QMainWindow):
    UI_PATH_MAIN = "UI/MainWindow.ui"
    UI_PATH_ASSET = "UI/asset.ui"

    def __init__(self, context: ProjectContext):
        super().__init__()
        self.context_menu = QMenu(self)
        self.config = ConfigHelper()

        self.context = context
        self.init_ui()
        self.load_project_tree()
        self.show()

    def init_ui(self):
        self.ui = load_ui_widget(self.UI_PATH_MAIN)
        self.setCentralWidget(self.ui)
        self.setFixedSize(1300, 510)

        # Tree model
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["text"])

        self.tw_project_tree: QTreeView = self.ui.findChild(QTreeView, "project_tree_view")
        self.tw_project_tree.setModel(self.model)
        self.tw_project_tree.setHeaderHidden(True)
        self.tw_project_tree.expandAll()
        self.tw_project_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tw_project_tree.setStyleSheet("""
            QTreeView::item {
                height: 30px;
                padding: 3px;
            }
        """)

        # QListWidget for leaf folders
        self.wl_step_list: QListWidget = self.ui.findChild(QListWidget, "asset_step_list")
        self.wl_step_list.setContextMenuPolicy(Qt.CustomContextMenu)

        # QListWidget for Files
        self.wl_file_list: QListWidget = self.ui.findChild(QListWidget, "file_list")
        self.wl_file_list.setContextMenuPolicy(Qt.CustomContextMenu)

        # Button for opening Files
        self.bt_open_file: QPushButton = self.ui.findChild(QPushButton, "open_file")
        self.wl_step_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.bt_open_file.clicked.connect(self.on_open_file_clicked)


        # Connect selection signals
        self.tw_project_tree.selectionModel().currentChanged.connect(self.on_tree_selection_changed)
        self.wl_step_list.currentItemChanged.connect(self.on_step_list_selection_changed)

    # --- Tree Population ---

    def load_project_tree(self):
        self.model.clear()
        assets_root = self.context.assets_path

        for folder in sorted(assets_root.iterdir(), key=lambda p: p.name):
            if not folder.is_dir():
                continue
            root_item = QStandardItem(folder.name)
            root_item.setEditable(False)
            root_item.setData(folder, Qt.UserRole)  # store full path
            self.model.appendRow(root_item)
            self.add_subfolders_to_tree(root_item, folder)

    def add_subfolders_to_tree(self, parent_item, folder_path: Path):
        # List immediate subdirectories
        subdirs = [p for p in sorted(folder_path.iterdir()) if p.is_dir()]

        # Filter out leaf folders (folders with no subfolders)
        subdirs = [p for p in subdirs if any(c.is_dir() for c in p.iterdir())]

        for subdir in subdirs:
            item = QStandardItem(subdir.name)
            item.setEditable(False)
            item.setData(subdir, Qt.UserRole)  # store full path
            parent_item.appendRow(item)
            self.add_subfolders_to_tree(item, subdir)

    # --- Leaf Folder Handling ---

    def on_tree_selection_changed(self, current: QModelIndex, previous: QModelIndex):
        self.wl_step_list.clear()

        if not current.isValid():
            return

        item = current.model().itemFromIndex(current)
        folder_path: Path = item.data(Qt.UserRole)
        if not folder_path or not folder_path.is_dir():
            return

        # List immediate subfolders
        subdirs = [p for p in folder_path.iterdir() if p.is_dir()]

        # Only include leaf folders (no subfolders themselves)
        leaf_subdirs = [p for p in subdirs if not any(c.is_dir() for c in p.iterdir())]
        for leaf in sorted(leaf_subdirs, key=lambda p: p.name):
            self.add_widget(self.wl_step_list, leaf.name, leaf)

    def on_step_list_selection_changed(self, current, previous):
        self.wl_file_list.clear()
        if current is None:
            return

        # Retrieve the full path of the selected leaf folder
        leaf_folder_path: Path = current.data(Qt.UserRole)
        if not leaf_folder_path or not leaf_folder_path.is_dir():
            return

        # List all .blend files in the folder
        for file_path in sorted(leaf_folder_path.iterdir(), reverse = True):
            if file_path.is_file() and file_path.suffix == ".blend" and "master" not in file_path.name:
                name = file_path.name[16:-6]
                self.add_widget(self.wl_file_list, name, file_path)

    # --- Utility ---

    def get_item_path(self, index: QModelIndex):
        path = []
        while index.isValid():
            item = index.model().itemFromIndex(index)
            path.insert(0, item.text())  # Prepend to keep order from root to leaf
            index = index.parent()
        return path

    def add_widget(self, list_widget, name, path: Path = None):
        widget = create_asset_widget(self, name)
        list_item = QListWidgetItem(list_widget)
        list_item.setSizeHint(widget.sizeHint())
        if path:
            list_item.setData(Qt.UserRole, path)  # store path in item
        list_widget.addItem(list_item)
        list_widget.setItemWidget(list_item, widget)

    def on_open_file_clicked(self):
        # Get current selection from file_list
        current_item = self.wl_file_list.currentItem()
        if current_item is None:
            return  # nothing selected
        
        file_path: Path = current_item.data(Qt.UserRole)
        if file_path is None or not file_path.exists():
            return

        # Open depending on OS
        if sys.platform.startswith("darwin"):      # macOS
            subprocess.call(("open", file_path))
        elif os.name == "nt":                      # Windows
            os.startfile(file_path)
        elif os.name == "posix":                   # Linux
            subprocess.call(("xdg-open", file_path))