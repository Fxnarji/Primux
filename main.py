# main.py
import sys
from PySide6.QtWidgets import QApplication
from pathlib import Path

from core.context import ProjectContext
from core.Primux import Primux

if __name__ == "__main__":
    app = QApplication(sys.argv)

    context = ProjectContext()
    context.set_project(Path(r"C:\Users\Fxnarji\Documents\GitHub\Primux\SampleStructure\NewProject"))

    primux = Primux(context)

    sys.exit(app.exec())
