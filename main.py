import sys
from PySide6.QtWidgets import QApplication
from OpenAPIWidget import OpenAPIWidget

app = QApplication(sys.argv)

window = OpenAPIWidget()

OpenAPIWidget.load_directory(window,"C:\\Users\\Fxnarji\\Documents\\GitHub\\Fonce_internal_prism_tools")

window.setWindowTitle("test")
window.show()

sys.exit(app.exec())
