import sys
from PySide6.QtWidgets import QApplication
from OpenAPIWidget import OpenAPIWidget
import os

app = QApplication(sys.argv)

window = OpenAPIWidget()

root = "/home/fxnarji/Documents/Primux_sample"
assets = os.path.join(root, "_assets")

window.path = assets
OpenAPIWidget.load_directory(window)


window.setWindowTitle("test")
window.show()

sys.exit(app.exec())
