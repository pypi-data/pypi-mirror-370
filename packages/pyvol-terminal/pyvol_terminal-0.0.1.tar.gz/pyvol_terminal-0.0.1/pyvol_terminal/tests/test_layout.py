import sys
import numpy as np
import pyqtgraph as pg
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, 
                             QVBoxLayout, QHBoxLayout, QPushButton,
                             QStackedLayout, QLabel)
from PySide6.QtCore import Qt
from PySide6 import QtWidgets


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Stacked Layout Example")
        self.setGeometry(100, 100, 800, 600)
        
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        nav_layout = QHBoxLayout()
        self.btn1 = QPushButton("Graph View")
        self.btn2 = QPushButton("Text View")
        self.btn3 = QPushButton("Image View")
        
        self.btn1.clicked.connect(lambda: self.change_view(0))
        self.btn2.clicked.connect(lambda: self.change_view(1))
        self.btn3.clicked.connect(lambda: self.change_view(2))
        
        nav_layout.addWidget(self.btn1)
        nav_layout.addWidget(self.btn2)
        nav_layout.addWidget(self.btn3)
        main_layout.addLayout(nav_layout)
        

        self.stacked_layout = QStackedLayout()
        main_layout.addLayout(self.stacked_layout)
        
        self.create_graph_view()
        self.create_text_view()
        self.create_image_view()
        
        # Set the initial view
        self.change_view(0)
        
    def add_q_label(self):
        label = QtWidgets.QLabel(str(np.random.normal(0, 1, 1)))
        return label

    def create_graph_view(self):

        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)  
        # Create plot widget
        plot_widget = pg.PlotWidget()
        
        settings = QHBoxLayout()
        labels = [self.add_q_label() for _ in range(4)]
        
        for label in labels:
            settings.addWidget(label)
        
        layout.addLayout(settings)
        layout.addWidget(plot_widget)
        x = np.linspace(0, 10, 100)
        y = np.sin(x)
        plot_widget.plot(x, y, pen='r')
        plot_widget.setTitle("Graph View - Click buttons above to change views")
        
        self.stacked_layout.addWidget(widget)  # Fixed this line
            
    def create_text_view(self):
        """Create the second view with text"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        label = QLabel("This is the Text View\n\n"
                      "You can put any text or widgets here.\n"
                      "Click the buttons above to switch between views.")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        
        self.stacked_layout.addWidget(widget)
    
    def create_image_view(self):
        """Create the third view with an image"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        # Create a label for the title
        title_label = QLabel("Image View - Random Data")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Create an image using PyQtGraph's ImageItem
        imv = pg.ImageView()
        
        # Create a sample image
        data = np.random.normal(size=(100, 100))
        data = np.cumsum(data, axis=0)
        data = np.sin(data * 0.1) * 10 + 10
        
        imv.setImage(data)
        layout.addWidget(imv)
        
        self.stacked_layout.addWidget(widget)
    
    def change_view(self, index):
        """Change the current view in the stacked layout"""
        self.stacked_layout.setCurrentIndex(index)
        
        # Update button styles to show which is active
        for i, btn in enumerate([self.btn1, self.btn2, self.btn3]):
            if i == index:
                btn.setStyleSheet("background-color: #4CAF50; color: white;")
            else:
                btn.setStyleSheet("")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())