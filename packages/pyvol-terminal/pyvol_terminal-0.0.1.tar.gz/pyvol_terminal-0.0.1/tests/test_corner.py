from PySide6.QtWidgets import QHeaderView, QTableWidget, QApplication, QMainWindow
from PySide6.QtCore import Qt
from PySide6 import QtGui, QtCore, QtWidgets
import sys
from PySide6.QtWidgets import QTableWidget, QStyle, QStyleOptionHeader
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPalette

            
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = QMainWindow()
    table = QTableWidget(5, 5)
    table.setCornerButtonEnabled(True) 
    for i in range(5):
        label = QtWidgets.QLabel(f"col_{i}")
        label_r = QtWidgets.QLabel(f"r_{i}")
    table.setHorizontalHeaderLabels([f"col_{i}" for i in range(5)])
    table.setVerticalHeaderLabels([f"row_{i}" for i in range(5)])
    corner_label=QtWidgets.QLabel("Main Title")
    corner_label.setAlignment(Qt.AlignCenter)
    table.setCornerWidget(corner_label)
    
    win.setCentralWidget(table)
    win.showMaximized()
    sys.exit(app.exec())
