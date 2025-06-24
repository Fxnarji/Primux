from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QPushButton
from PySide6.QtCore import Qt

# Example asset card widget
class AssetWidget(QWidget):
    def __init__(self, name, info):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"<b>{name}</b>"))
        layout.addWidget(QLabel(info))
        layout.addWidget(QPushButton("Import"))
        self.setLayout(layout)

# Assuming your UI file has a scrollArea named `scrollArea`
def populate_assets(ui):
    # Create a container for the asset widgets
    content = QWidget()
    layout = QVBoxLayout(content)
    
    # Manually add asset widgets
    layout.addWidget(AssetWidget("Tree", "Low poly stylized tree"))
    layout.addWidget(AssetWidget("Rock", "Large rock with moss"))
    layout.addWidget(AssetWidget("House", "Cartoon house, 4k textures"))

    # Apply content to scroll area
    ui.asset_list.setWidget(content)
    ui.asset_list.setWidgetResizable(True)
