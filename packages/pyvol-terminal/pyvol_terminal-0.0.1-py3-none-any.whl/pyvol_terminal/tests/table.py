from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, 
                             QVBoxLayout, QTableWidget, QTableWidgetItem)
from PySide6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create 4x4 table
        self.table = QTableWidget(4, 4)  # 4 rows, 4 columns
        
        # Set headers
        self.table.setHorizontalHeaderLabels(["Column 1", "Column 2", "Column 3", "Column 4"])
        self.table.setVerticalHeaderLabels(["Row 1", "Row 2", "Row 3", "Row 4"])
        
        # Fill table with sample data
        for row in range(4):
            for col in range(4):
                item = QTableWidgetItem(f"Item {row+1}-{col+1}")
                item.setTextAlignment(Qt.AlignCenter)  # Center text
                self.table.setItem(row, col, item)
        
        # Set column widths
        self.table.horizontalHeader().setDefaultSectionSize(120)
        
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        layout.addWidget(self.table)
        layout.setContentsMargins(0, 0, 0, 0)  # Remove layout margins
        
        self.setWindowTitle("4x4 Table Example")
        
        self.adjustWindowToTable()

    def adjustWindowToTable(self):
        width = self.table.verticalHeader().width() + \
                self.table.horizontalHeader().length() + \
                self.table.frameWidth() * 2
        
        height = self.table.horizontalHeader().height() + \
                 self.table.verticalHeader().length() + \
                 self.table.frameWidth() * 2
        
        # Set the central widget size
        self.centralWidget().setFixedSize(width, height)        
        self.adjustSize()


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()