from PySide6.QtWidgets import QMenu
from PySide6.QtGui import QAction
from PySide6.QtCore import QPoint

def show_tree_context_menu(parent, tree_view, model, position: QPoint):
    index = tree_view.indexAt(position)
    if not index.isValid():
        return

    item = model.itemFromIndex(index)
    if item is None:
        return

    menu = QMenu(parent)

    open_action = QAction("Open", parent)
    rename_action = QAction("Rename", parent)
    delete_action = QAction("Delete", parent)

    open_action.triggered.connect(lambda: print(f"Open: {item.text()}"))
    rename_action.triggered.connect(lambda: print(f"Rename: {item.text()}"))
    delete_action.triggered.connect(lambda: print(f"Delete: {item.text()}"))

    menu.addAction(open_action)
    menu.addAction(rename_action)
    menu.addAction(delete_action)

    menu.exec(tree_view.viewport().mapToGlobal(position))
