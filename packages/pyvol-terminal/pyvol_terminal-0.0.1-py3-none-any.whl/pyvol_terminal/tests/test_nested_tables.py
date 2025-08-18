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
            painter.fillRect(option.rect, QtGui.QColor("orange"))
            painter.save()
            painter.setFont(item.font())
            painter.setPen(item.foreground().color())
            text_rect = option.rect.adjusted(4, 0, -4, 0)
            painter.drawText(
                text_rect,
                item.textAlignment() | QtCore.Qt.AlignVCenter,
                item.text()
            )
            painter.restore()
        else:
            super().paint(painter, option, index)

def create_child_table():
    child_table = QtWidgets.QTableWidget(50, 4)
    child_table.setItemDelegate(CustomDelegate(child_table))
    child_table.setStyleSheet("""
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
    child_table.setShowGrid(False)
    child_table.verticalHeader().setVisible(False)
    child_table.horizontalHeader().setVisible(True)
    child_table.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
    child_table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

    for row in range(child_table.rowCount()):
        for col in range(child_table.columnCount()):
            if row == 0:
                item = OptionExpiryCellItem(f"Expiry {col+1}")
            else:
                item = OptionMetricCellItem(f"{row}.{col}")
            child_table.setItem(row, col, item)

    child_table.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                               QtWidgets.QSizePolicy.Expanding)
    return child_table

def link_scrollbars(*tables):
    for table in tables:
        table.verticalScrollBar().valueChanged.connect(
            lambda value, current=table: sync_scroll(value, current, tables)
        )

def sync_scroll(value, source, tables):
    for table in tables:
        if table is not source:
            table.verticalScrollBar().setValue(value)

app = QtWidgets.QApplication([])
window = QtWidgets.QMainWindow()

parent_table = QtWidgets.QTableWidget(1, 3)

child_table1 = create_child_table()
child_table2 = create_child_table()
child_table3 = create_child_table()

parent_table.setCellWidget(0, 0, child_table1)
parent_table.setCellWidget(0, 1, child_table2)
parent_table.setCellWidget(0, 2, child_table3)

parent_table.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
parent_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

link_scrollbars(child_table1, child_table2, child_table3)

window.setCentralWidget(parent_table)
window.resize(800, 600)
window.show()
app.exec()
