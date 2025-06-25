from PySide6.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem
from PySide6.QtGui import QPainter, QColor, QFont
from PySide6.QtCore import QRect, Qt, QSize

class AssetDelegate(QStyledItemDelegate):
    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index):
        painter.save()

        # Background
        if option.state & QStyleOptionViewItem.State_Selected:
            painter.fillRect(option.rect, QColor("#a2c5f5"))
        elif option.state & QStyleOptionViewItem.State_MouseOver:
            painter.fillRect(option.rect, QColor("#e0e0e0"))

        # Custom text rendering
        name = index.data()
        rect = option.rect.adjusted(10, 0, -10, 0)
        font = QFont("Inter", 11)
        painter.setFont(font)
        painter.setPen(QColor("black"))
        painter.drawText(rect, Qt.AlignVCenter | Qt.AlignLeft, name)

        painter.restore()

    def sizeHint(self, option, index):
        return QSize(option.rect.width(), 35)
