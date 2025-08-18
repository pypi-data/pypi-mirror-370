from pyvol_terminal.interfaces.volatility_surface import gl_plotitems2
from PySide6 import QtWidgets, QtCore, QtGui
import sys
import pyqtgraph as pg  
import numpy as np
from pyqtgraph import opengl



class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dropdown Options with QToolButton")
        self.resize(400, 200)

        self.gl_view = opengl.GLViewWidget()
        
        self.setCentralWidget(self.gl_view)
        x_vec, y_vec = [np.linspace(-1, 1, 10)] * 2
        x_grid, y_grid = np.meshgrid(x_vec, y_vec)
        z = np.sin(x_grid.flatten()) + np.cos(y_grid.flatten())
        pos = np.column_stack((x_grid.flatten(),y_grid.flatten(),z))
        #scatter = gl_plotitems2.CustomGLScatterPlotItem2(pos=pos, color="red")
        scatter = gl_plotitems2.CustomGLScatterPlotItem2(pos=pos, color="red")
        self.gl_view.addItem(scatter)
        scatter = opengl.GLScatterPlotItem(pos=pos)
        self.gl_view.addItem(scatter)
        

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec())
