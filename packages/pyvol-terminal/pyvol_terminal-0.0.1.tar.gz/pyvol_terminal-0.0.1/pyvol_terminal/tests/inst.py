from PySide6.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem

app = QApplication([])

# Create the main window
main_window = QMainWindow()
main_window.setWindowTitle("Table as Central Widget Example")

# Create a QTableWidget
table = QTableWidget()
table.setRowCount(3)  # 3 rows
table.setColumnCount(2)  # 2 columns

# Fill the table with some data
table.setHorizontalHeaderLabels(["Name", "Age"])

table.setItem(0, 0, QTableWidgetItem("Alice"))
table.setItem(0, 1, QTableWidgetItem("25"))
table.setItem(1, 0, QTableWidgetItem("Bob"))
table.setItem(1, 1, QTableWidgetItem("30"))
table.setItem(2, 0, QTableWidgetItem("Charlie"))
table.setItem(2, 1, QTableWidgetItem("35"))

# Set the table as the central widget
main_window.setCentralWidget(table)

main_window.show()
app.exec()