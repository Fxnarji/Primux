import sys
from PySide6.QtWidgets import QApplication
from OpenAPIWidget import OpenAPIWidget

app = QApplication(sys.argv)

window = OpenAPIWidget()
window.setWindowTitle("test")
window.show()

sys.exit(app.exec())
