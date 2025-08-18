from PySide6 import QtWidgets, QtCore, QtGui

class OptionExpiryCellItem(QtWidgets.QTableWidgetItem):
    def __init__(self, text):
        super().__init__(text)
        self.setBackground(QtGui.QBrush(QtGui.QColor("orange")))
        self.setForeground(QtGui.QBrush(QtGui.QColor("white")))
        self.setTextAlignment(QtCore.Qt.AlignLeft)
        font = QtGui.QFont("Neue Haas Grotesk", 12)
        self.setFont(font)

class OptionMetricCellItem(QtWidgets.QTableWidgetItem):
    def __init__(self, text):
        super().__init__(text)
        self.setBackground(QtGui.QBrush(QtGui.QColor("black")))
        self.setForeground(QtGui.QBrush(QtGui.QColor("white")))
        self.setTextAlignment(QtCore.Qt.AlignRight)
        font = QtGui.QFont("Neue Haas Grotesk", 12)
        self.setFont(font)

class CustomDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, table):
        super().__init__()
        self.table = table

    def paint(self, painter, option, index):
        item = self.table.item(index.row(), index.column())
        
        if item and item.background().color() == QtGui.QColor("orange"):
            # Fill background
            painter.fillRect(option.rect, QtGui.QColor("orange"))
            
            # Draw text manually with proper alignment and style
            painter.save()
            painter.setFont(item.font())
            painter.setPen(item.foreground().color())
            
            # Calculate text rectangle with padding
            text_rect = option.rect.adjusted(4, 0, -4, 0)  # 4px horizontal padding
            
            # Draw text with alignment
            painter.drawText(
                text_rect,
                item.textAlignment() | QtCore.Qt.AlignVCenter,
                item.text()
            )
            painter.restore()
        else:
            # Default painting for other items
            super().paint(painter, option, index)

app = QtWidgets.QApplication([])
window = QtWidgets.QMainWindow()
table = QtWidgets.QTableWidget(10, 4)

# Set delegate with table reference
table.setItemDelegate(CustomDelegate(table))


table.setStyleSheet("""
    QTableWidget {
        background-color: black;
        border-left: 2px solid #414141;
        border-right: 2px solid #414141;
    }
    QTableWidget::item {
        border: 0px;
        padding: 4px;
    }
    QTableWidget::item:selected {
        background-color: #414141;
    }
""")

# Configure table
table.setShowGrid(False)
#table.setFrameShape(QtWidgets.QFrame.NoFrame)
table.verticalHeader().setVisible(False)
table.horizontalHeader().setVisible(False)

# Fill the table
for row in range(10):
    for col in range(4):
        if row == 0:
            item = OptionExpiryCellItem(f"Expiry {col+1}")
        else:
            item = OptionMetricCellItem(f"{row}.{col}")
        table.setItem(row, col, item)

window.setCentralWidget(table)
window.resize(800, 600)
window.show()
app.exec()