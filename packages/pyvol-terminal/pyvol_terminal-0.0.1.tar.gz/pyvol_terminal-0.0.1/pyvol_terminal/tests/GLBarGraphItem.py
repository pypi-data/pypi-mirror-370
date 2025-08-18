import numpy as np
import pyqtgraph as pg
import pyqtgraph.opengl as gl
from PySide6 import QtWidgets, QtCore
import sys

class Window(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.gl_widget = gl.GLViewWidget()
        self.setCentralWidget(self.gl_widget)
        self.show()
        self.setWindowTitle('pyqtgraph example: GLBarGraphItem')
        self.gl_widget.setCameraPosition(distance=40)
        
        # Add grids
        self.gx = gl.GLGridItem()
        self.gx.rotate(90, 0, 1, 0)
        self.gx.translate(-10, 0, 10)
        self.gl_widget.addItem(self.gx)
        
        self.gy = gl.GLGridItem()
        self.gy.rotate(90, 1, 0, 0)
        self.gy.translate(0, -10, 10)
        self.gl_widget.addItem(self.gy)
        
        self.gz = gl.GLGridItem()
        self.gz.translate(0, 0, 0)
        self.gl_widget.addItem(self.gz)
        
    def setData(self, n):
        # Clear previous items
        for item in self.gl_widget.items[:]:
            if isinstance(item, gl.GLBarGraphItem):
                self.gl_widget.removeItem(item)
        
        # Generate data
        pos = np.empty((n, n, 3))
        pos[..., 0] = np.arange(n).reshape(n, 1)
        pos[..., 1] = np.arange(n).reshape(1, n)
        pos[..., 2] = 0
        
        size = np.empty((n, n, 3))
        size[..., 0:2] = 2*0.4
        size[..., 2] = np.random.normal(size=(n, n)) * 2 + 10
        
        # Create bar graph item
        self.bg = gl.GLBarGraphItem(pos, size)
        self.gl_widget.addItem(self.bg)

def main():
    # Check for existing QApplication before creating one
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)
    
  #  w1 = Window()
  #  w1.setData(10)
    
    w2 = Window()
    w2.setData(10)
    
    if sys.flags.interactive != 1 or not hasattr(QtCore, 'PYQT_VERSION'):
        sys.exit(app.exec())

if __name__ == '__main__':
    main()