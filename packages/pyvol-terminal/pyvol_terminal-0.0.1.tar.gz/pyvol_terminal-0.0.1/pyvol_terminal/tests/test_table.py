import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QTableWidget,
                               QTableWidgetItem, QVBoxLayout, QWidget,QSizePolicy, QHeaderView)
from PySide6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Merged Column Header Example")
        self.setGeometry(100, 100, 600, 400)
        self.showMaximized()

        # Create the table widget
        
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["AA", "BB", "CC","DD"])
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.table.setRowCount(1)
        
        child1_table1 = self.create_child1_table()
        
        child1_table2 = self.create_child1_table()
        child1_table3 = self.create_child1_table()
        child1_table4 = self.create_child1_table()

        self.table.setCellWidget(0, 0, child1_table1) 
        self.table.setCellWidget(0, 1, child1_table2) 
        self.table.setCellWidget(0, 2, child1_table3) 
        self.table.setCellWidget(0, 3, child1_table4) 

        layout = QVBoxLayout()
        layout.addWidget(self.table)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)



    def create_child1_table(self):
        
        
        child1_table = QTableWidget()
        child1_table.setColumnCount(2)
        child1_table.setHorizontalHeaderLabels(["Calls", "Puts"])
        child1_table.setRowCount(3)  # Extra row for the merged column header
        child1_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        child1_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        child1_table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        for jdx in range(2):
            for idx in range(3):
                child2_table = self.create_child2_table(idx)
                child1_table.setCellWidget(idx, jdx, child2_table) 
        
        return child1_table




    def create_child2_table(self, idx):
        child_table = QTableWidget()
        child_table.setColumnCount(3)
        child_table.setRowCount(3)
        
        
        
        child_table.setHorizontalHeaderLabels(["A", "B", "C"])
        
        for i in range(3):
            for j in range(3):
                item = QTableWidgetItem(str(i*j))
                child_table.setItem(i, j, item)

        
        return child_table
        
        
        # Set up layout
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
