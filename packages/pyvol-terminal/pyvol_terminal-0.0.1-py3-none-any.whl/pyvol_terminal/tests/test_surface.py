import numpy as np
import pyqtgraph as pg
import pyqtgraph.opengl as gl
from PySide6 import QtWidgets
import sys

def main():
    app = QtWidgets.QApplication(sys.argv)

    # Create the main OpenGL view widget
    w = gl.GLViewWidget()
    w.setWindowTitle('GLSurfacePlotItem Example')
    w.setCameraPosition(distance=40)
    w.show()

    # Create grid
    g = gl.GLGridItem()
    g.scale(2, 2, 1)
    w.addItem(g)

    # Generate a 2D surface (z = sin(r))
    x = np.linspace(-10, 10, 50)
    y = np.linspace(-10, 10, 50)
    X, Y = np.meshgrid(x, y)
    r = np.sqrt(X**2 + Y**2)
    z = np.sin(r)
    
    z = np.nan * z
    # Create surface plot
    p = gl.GLSurfacePlotItem(x=x, y=y, z=z, shader='shaded')
    p.translate(0, 0, 0)  # Optional: move the surface
    w.addItem(p)

    sys.exit(app.exec())

if __name__ == '__main__':
    main()
