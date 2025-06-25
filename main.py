import sys
from PySide6.QtWidgets import QApplication
from OpenAPIWidget import OpenAPIWidget
import os

app = QApplication(sys.argv)

window = OpenAPIWidget()
project = os.path.join("/home/fxnarji/Documents/Primux_sample")

window.load_project(path = project)


window.setWindowTitle("test")
window.show()

sys.exit(app.exec())
