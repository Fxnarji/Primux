from PySide6.QtWidgets import (
    QMainWindow,
    QListWidget,
    QMenu,
    QTreeView,
    QListWidgetItem,
    QPushButton,
    QTabWidget,
    QFileDialog, 
    QMessageBox,
    QLabel
)
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtCore import Qt, QModelIndex
from pathlib import Path
from enum import Enum
import ui.resources_rc

from core import ProjectContext
from .util import ConfigHelper
from ui.loader import load_ui_widget, create_asset_widget, AssetIcon
import subprocess, sys, os

class ShowType(Enum):
    SHOW = 0
    ASSETS = 1

class Primux(QMainWindow):
    UI_PATH_MAIN = "UI/MainWindow.ui"
    UI_PATH_ASSET = "UI/asset.ui"
    current_tab = ShowType.SHOW

    def __init__(self, context: ProjectContext):
        super().__init__()
        self.context = context
        self.current_root = None  

        self.init_ui()

        if not self.context.project_root:
            self.on_open_project_clicked()
        else:
            self.set_root(self.context.show_path)

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

        # Step + File lists
        self.wl_step_list: QListWidget = self.ui.findChild(QListWidget, "asset_step_list")
        self.wl_file_list: QListWidget = self.ui.findChild(QListWidget, "file_list")

        # Button
        self.bt_open_file: QPushButton = self.ui.findChild(QPushButton, "open_file")
        self.bt_open_file.clicked.connect(self.on_open_file_clicked)

        # Tab widget
        self.tab_widget: QTabWidget = self.ui.findChild(QTabWidget, "tabWidget")
        self.tab_widget.currentChanged.connect(self.on_tab_changed)

        # Connect selection signals
        self.tw_project_tree.selectionModel().currentChanged.connect(self.on_tree_selection_changed)
        self.wl_step_list.currentItemChanged.connect(self.on_step_list_selection_changed)

        # open project button
        self.bt_open_project: QPushButton = self.ui.findChild(QPushButton, "bt_populate_list")
        self.bt_open_project.clicked.connect(self.on_open_project_clicked)

    # --- Switching Roots ---
    def set_root(self, root: Path):
        """Repopulate the tree from the given root directory"""
        print("Switched Roots")
        if not root or not root.exists():
            return
        self.current_root = root
        self.load_project_tree()

    def on_tab_changed(self, index: int):
        if index == 0:  # Show tab
            self.set_root(self.context.show_path)
            self.current_tab = ShowType.SHOW
        elif index == 1:  # Assets tab
            self.set_root(self.context.assets_path)
            self.current_tab = ShowType.ASSETS
        print(self.current_tab)


    # --- Tree Population ---
    def load_project_tree(self):
        self.model.clear()
        if not self.current_root:
            return

        for folder in sorted(self.current_root.iterdir(), key=lambda p: p.name):
            if not folder.is_dir():
                continue
            root_item = QStandardItem(folder.name)
            root_item.setEditable(False)
            root_item.setData(folder, Qt.UserRole)
            self.model.appendRow(root_item)
            self.add_subfolders_to_tree(root_item, folder)

    def add_subfolders_to_tree(self, parent_item, folder_path: Path):
        subdirs = [p for p in sorted(folder_path.iterdir()) if p.is_dir()]
        subdirs = [p for p in subdirs if any(c.is_dir() for c in p.iterdir())]  # only non-leaves

        for subdir in subdirs:
            item = QStandardItem(subdir.name)
            item.setEditable(False)
            item.setData(subdir, Qt.UserRole)
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

        subdirs = [p for p in folder_path.iterdir() if p.is_dir()]
        leaf_subdirs = [p for p in subdirs if not any(c.is_dir() for c in p.iterdir())]

        for leaf in sorted(leaf_subdirs, key=lambda p: p.name):
            # Default icon
            icon = AssetIcon.PLACEHOLDER

            # Check if leaf.name matches an enum member (case-insensitive)
            leaf_upper = leaf.name.upper()
            if leaf_upper in AssetIcon.__members__:
                icon = AssetIcon[leaf_upper]

            self.add_widget(self.wl_step_list, leaf.name, leaf, icon=icon)

    def on_step_list_selection_changed(self, current, previous):
        self.wl_file_list.clear()
        if current is None:
            return

        leaf_folder_path: Path = current.data(Qt.UserRole)
        if not leaf_folder_path or not leaf_folder_path.is_dir():
            return

        for file_path in sorted(leaf_folder_path.iterdir(), reverse=True):
            if file_path.is_file() and file_path.suffix != ".blend1" and "master" not in file_path.name:
                if self.current_tab == ShowType.SHOW:
                    name = file_path.name[16:-6]
                else:
                    name = file_path.name

                # Determine icon from file extension
                ext = file_path.suffix.upper().lstrip(".")  # ".blend" -> "BLEND"
                print(ext)
                try:
                    icon = AssetIcon[ext]  # look up in the enum
                except KeyError:
                    icon = AssetIcon.PLACEHOLDER  # fallback

                self.add_widget(self.wl_file_list, name, file_path, icon=icon)



    # --- Utility ---
    def add_widget(self, list_widget, name, path: Path = None, icon: AssetIcon = AssetIcon.PLACEHOLDER):
        widget = create_asset_widget(self, name, icon)
        list_item = QListWidgetItem(list_widget)
        list_item.setSizeHint(widget.sizeHint())
        if path:
            list_item.setData(Qt.UserRole, path)
        list_widget.addItem(list_item)
        list_widget.setItemWidget(list_item, widget)

    def on_open_file_clicked(self):
        current_item = self.wl_file_list.currentItem()
        if current_item is None:
            return
        file_path: Path = current_item.data(Qt.UserRole)
        if not file_path or not file_path.exists():
            return

        if sys.platform.startswith("darwin"):
            subprocess.call(("open", file_path))
        elif os.name == "nt":
            os.startfile(file_path)
        elif os.name == "posix":
            subprocess.call(("xdg-open", file_path))


    def on_open_project_clicked(self):
        """Let user pick a new project root and reload the tree."""
        dialog = QFileDialog(self, "Select Project Root")
        dialog.setFileMode(QFileDialog.Directory)
        dialog.setOption(QFileDialog.ShowDirsOnly, True)

        if dialog.exec():
            selected_paths = dialog.selectedFiles()
            if not selected_paths:
                return

            new_root = Path(selected_paths[0])
            try:
                self.context.set_project(new_root)
            except ValueError as e:
                QMessageBox.warning(self, "Invalid Project", str(e))
                return

            # Update tree with new project root (default: Show)
            self.set_root(self.context.show_path)

            # Clear lists
            self.wl_step_list.clear()
            self.wl_file_list.clear()

            # Update label with current path
            lbl_path = self.ui.findChild(QLabel, "CurrentPath")
            if lbl_path:
                lbl_path.setText(str(new_root))