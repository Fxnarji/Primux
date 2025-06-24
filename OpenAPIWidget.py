from PySide6.QtWidgets import QListWidgetItem, QListWidget, QListView, QWidget, QVBoxLayout, QMainWindow, QPushButton, QLineEdit, QLabel, QScrollArea
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QSize
from server import start

class OpenAPIWidget(QMainWindow):
    def __init__(self):
        super().__init__()

        loader = QUiLoader()
        self.ui = loader.load("UI/Testui.ui", None)

        self.setCentralWidget(self.ui)

        self.setFixedSize(1212, 510)

        self.button = self.ui.findChild(QPushButton,"bt_start_server")
        self.populate_list = self.ui.findChild(QPushButton,"bt_populate_list")
        self.asset_list = self.ui.findChild(QListView, "asset_list")
        self.port = self.ui.findChild(QLineEdit, "inpt_port")
        self.status = self.ui.findChild(QLabel, "out_status")


        self.populate_list.clicked.connect(self.load_assets)
        self.button.clicked.connect(self.start_server)

    def start_server(self):
        port = self.port.text()
        try:
            start(int(port))
            self.status.setStyleSheet("color: green;")
            self.status.setText(f"running")
        except:
            self.status.setStyleSheet("color: red;")
            self.status.setText(f"failed to Start!")
    
    def load_assets(self):
        self.asset_list_widget = QListWidget()
        self.asset_list.setWidget(self.asset_list_widget)  # replace scroll area's widget

        for i in range(4):
            item = QListWidgetItem()
            item.setSizeHint(QSize(300, 50))  # set item size
            
            asset_widget = QWidget()
            layout = QVBoxLayout(asset_widget)
            label = QLabel(f"Asset {i+1}")
            layout.addWidget(label)

            self.asset_list_widget.addItem(item)
            self.asset_list_widget.setItemWidget(item, asset_widget)
        self.asset_list_widget.setSelectionMode(QListWidget.SingleSelection)    