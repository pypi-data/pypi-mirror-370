import sys
import time
import random
from PySide6.QtWidgets import (QApplication, QMainWindow, QTableView, QTableWidget,
                               QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QLabel, QTableWidgetItem)
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, QTimer
from PySide6 import QtGui
from PySide6.QtGui import QFontDatabase

class OptionMetricCellItem(QTableWidgetItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFlags(self.flags() | Qt.ItemIsSelectable)
        self.setFlags(self.flags() & ~Qt.ItemIsEditable)
        self.setBackground(QtGui.QBrush(QtGui.QColor("black")))
        self.setForeground(QtGui.QBrush(QtGui.QColor("#fb8b1e")))
        self.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

class TableModel(QAbstractTableModel):
    def __init__(self, rows=100, cols=20):
        super().__init__()
        self._data = [[random.random() for _ in range(cols)] for _ in range(rows)]

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return len(self._data[0]) if self._data else 0

    def data(self, index, role=Qt.DisplayRole):
        if role in (Qt.DisplayRole, Qt.EditRole):
            return f"{self._data[index.row()][index.column()]:.4f}"
        return None

    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.EditRole and index.isValid():
            self._data[index.row()][index.column()] = value
            self.dataChanged.emit(index, index)
            return True
        return False

    def flags(self, index):
        return super().flags(index) | Qt.ItemIsEditable

    def update_all_values(self):
        for row in range(self.rowCount()):
            for col in range(self.columnCount()):
                self._data[row][col] = random.random()
        self.dataChanged.emit(
            self.index(0, 0),
            self.index(self.rowCount()-1, self.columnCount()-1))

class PerformanceTestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Performance Comparison")
        self.setGeometry(100, 100, 1200, 800)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Add all three test sections
        main_layout.addLayout(self.create_model_view_section())
        main_layout.addLayout(self.create_table_widget_section())
        main_layout.addLayout(self.create_custom_table_widget_section())
        
        self.model_view_times = []
        self.table_widget_times = []
        self.custom_widget_times = []

    def create_model_view_section(self):
        layout = QHBoxLayout()
        self.model = TableModel()
        self.model_view = QTableView()
        self.model_view.setModel(self.model)
        
        btn_layout = QVBoxLayout()
        self.model_view_btn = QPushButton("Test Model-View (100 cycles)")
        self.model_view_btn.clicked.connect(lambda: self.run_performance_test("model"))
        self.model_view_result = QLabel("Average time: --")
        
        btn_layout.addWidget(self.model_view_btn)
        btn_layout.addWidget(self.model_view_result)
        
        layout.addWidget(self.model_view)
        layout.addLayout(btn_layout)
        return layout

    def create_table_widget_section(self):
        layout = QHBoxLayout()
        self.table_widget = QTableWidget(100, 20)
        self.populate_table_widget()
        
        btn_layout = QVBoxLayout()
        self.table_widget_btn = QPushButton("Test Standard QTableWidget (100 cycles)")
        self.table_widget_btn.clicked.connect(lambda: self.run_performance_test("widget"))
        self.table_widget_result = QLabel("Average time: --")
        
        btn_layout.addWidget(self.table_widget_btn)
        btn_layout.addWidget(self.table_widget_result)
        
        layout.addWidget(self.table_widget)
        layout.addLayout(btn_layout)
        return layout

    def create_custom_table_widget_section(self):
        layout = QHBoxLayout()
        self.custom_table_widget = QTableWidget(100, 20)
        self.populate_custom_table_widget()
        
        btn_layout = QVBoxLayout()
        self.custom_widget_btn = QPushButton("Test Custom QTableWidget (100 cycles)")
        self.custom_widget_btn.clicked.connect(lambda: self.run_performance_test("custom_widget"))
        self.custom_widget_result = QLabel("Average time: --")
        
        btn_layout.addWidget(self.custom_widget_btn)
        btn_layout.addWidget(self.custom_widget_result)
        
        layout.addWidget(self.custom_table_widget)
        layout.addLayout(btn_layout)
        return layout

    def populate_table_widget(self):
        for row in range(100):
            for col in range(20):
                item = QTableWidgetItem()
                item.setData(Qt.DisplayRole, f"{random.random():.4f}")
                self.table_widget.setItem(row, col, item)

    def populate_custom_table_widget(self):
        for row in range(100):
            for col in range(20):
                item = OptionMetricCellItem(f"{random.random():.4f}")
                self.custom_table_widget.setItem(row, col, item)

    def update_table_widget(self):
        self.table_widget.setUpdatesEnabled(False)
        for row in range(100):
            for col in range(20):
                self.table_widget.item(row, col).setText(f"{random.random():.4f}")
        self.table_widget.setUpdatesEnabled(True)

    def update_custom_table_widget(self):
        self.custom_table_widget.setUpdatesEnabled(False)
        for row in range(100):
            for col in range(20):
                self.custom_table_widget.item(row, col).setText(f"{random.random():.4f}")
        self.custom_table_widget.setUpdatesEnabled(True)

    def run_performance_test(self, test_type):
        test_funcs = {
            "model": self.model.update_all_values,
            "widget": self.update_table_widget,
            "custom_widget": self.update_custom_table_widget
        }
        
        results = []
        test_func = test_funcs[test_type]
        
        for _ in range(100):
            start_time = time.perf_counter()
            test_func()
            QApplication.processEvents()
            end_time = time.perf_counter()
            results.append(end_time - start_time)
            
        avg_time = sum(results) / len(results)
        
        if test_type == "model":
            self.model_view_result.setText(f"Model-View: {avg_time:.6f}s")
        elif test_type == "widget":
            self.table_widget_result.setText(f"Standard Widget: {avg_time:.6f}s")
        else:
            self.custom_widget_result.setText(f"Custom Widget: {avg_time:.6f}s")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    font_families = QFontDatabase().families()
    window = PerformanceTestWindow()
    window.show()
    sys.exit(app.exec())