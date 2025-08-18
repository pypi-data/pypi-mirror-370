from PySide6.QtWidgets import (QMainWindow, QWidget, QDockWidget, QSplitter, 
                              QVBoxLayout, QLabel, QApplication)
from PySide6.QtCore import Qt
import sys
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("3D Graph with 2D Slices")
        self.setGeometry(100, 100, 1000, 800)
        
        # Create central widget with 3D graph
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Create 3D plot
        self.figure_3d = Figure()
        self.canvas_3d = FigureCanvas(self.figure_3d)
        self.ax_3d = self.figure_3d.add_subplot(111, projection='3d')
        
        # Generate some sample 3D data
        x = np.linspace(-5, 5, 50)
        y = np.linspace(-5, 5, 50)
        x, y = np.meshgrid(x, y)
        z = np.sin(np.sqrt(x**2 + y**2))
        
        # Plot the 3D surface
        self.ax_3d.plot_surface(x, y, z, cmap='viridis')
        self.ax_3d.set_title("3D Graph")
        
        # Create layout for central widget
        layout = QVBoxLayout(self.central_widget)
        layout.addWidget(self.canvas_3d)
        
        # Create dock widget for 2D slices
        self.create_slice_dock()
        
        # Connect 3D graph interaction to update slices
        # (You'll need to implement this based on your interaction method)
        
    def create_slice_dock(self):
        """Create the dock widget with split view of 2D slices"""
        self.dock = QDockWidget("2D Slices", self)
        self.dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        
        # Create container widget for the dock
        container = QWidget()
        layout = QVBoxLayout(container)
        
        # Create splitter for the two slice views
        splitter = QSplitter(Qt.Vertical)
        
        # Create XY slice plot
        self.figure_xy = Figure()
        self.canvas_xy = FigureCanvas(self.figure_xy)
        self.ax_xy = self.figure_xy.add_subplot(111)
        self.ax_xy.set_title("XY Slice")
        
        # Create XZ slice plot
        self.figure_xz = Figure()
        self.canvas_xz = FigureCanvas(self.figure_xz)
        self.ax_xz = self.figure_xz.add_subplot(111)
        self.ax_xz.set_title("XZ Slice")
        
        # Add plots to splitter
        splitter.addWidget(self.canvas_xy)
        splitter.addWidget(self.canvas_xz)
        
        layout.addWidget(splitter)
        
#        container.setLayout(layout)
        
        self.dock.setWidget(container)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dock)
        print(self.dock.widget().layout().itemAt(0).widget())
        # Enable dock features
        self.dock.setFeatures(QDockWidget.DockWidgetMovable | 
                             QDockWidget.DockWidgetFloatable |
                             QDockWidget.DockWidgetClosable)
        
    def update_slices(self, x, y, z):
        """Update the 2D slices based on a point in 3D space"""
        # This is a placeholder - implement your actual slice calculation here
        
        # Example: Update XY slice (constant z)
        self.ax_xy.clear()
        # ... plot XY slice data ...
        self.ax_xy.set_title(f"XY Slice at Z={z:.2f}")
        self.canvas_xy.draw()
        
        # Example: Update XZ slice (constant y)
        self.ax_xz.clear()
        # ... plot XZ slice data ...
        self.ax_xz.set_title(f"XZ Slice at Y={y:.2f}")
        self.canvas_xz.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())