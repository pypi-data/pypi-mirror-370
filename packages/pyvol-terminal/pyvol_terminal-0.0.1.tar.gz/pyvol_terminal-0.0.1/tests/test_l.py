import numpy as np
import pyqtgraph as pg
import pyqtgraph.opengl as gl
from PySide6 import QtGui


app = pg.mkQApp()
view = gl.GLViewWidget()
view.show()

# Create 5 random lines (10 points)
pos = np.random.rand(10, 3) * 10  # Example data

# Build transformation matrix (translate + scale)
matrix = QtGui.QMatrix4x4()
matrix.translate(2, 2, 2)  # Shift by (2, 2, 2)
matrix.scale(3, 3, 3)      # Scale by (3, 3, 3)

for i in range(0, len(pos), 2):
    point = QtGui.QVector3D(*pos[i])
    transformed_point = matrix * point
    pos[i] = [transformed_point.x(), transformed_point.y(), transformed_point.z()]

line_plot = gl.GLLinePlotItem(pos=pos, mode="lines", width=2, color='r')
view.addItem(line_plot)

matrix = QtGui.QMatrix4x4()
matrix.translate(2, 2, 2)  # Shift by (2, 2, 2)
matrix.scale(3, 3, 3)      # Scale by (3, 3, 3)



line_plot.setTransform()

