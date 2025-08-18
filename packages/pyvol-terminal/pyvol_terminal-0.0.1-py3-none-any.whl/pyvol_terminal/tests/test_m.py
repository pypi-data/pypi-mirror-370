import sys
import numpy as np
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
import pyqtgraph.opengl as gl
from PySide6.QtGui import QVector3D, QMatrix4x4

class TransformDemo(gl.GLViewWidget):
    def __init__(self):
        super().__init__()
        self.setCameraPosition(distance=15)

        # Axis grid
        grid = gl.GLGridItem()
        grid.setSize(10, 10)
        grid.setSpacing(1, 1)
        self.addItem(grid)

        # Create an "L" shaped object made of 2 points
        self.l_shape = np.array([
            [2, 0, 0],  # horizontal arm
            [2, 1, 0],  # vertical arm
        ])

        # Compute centroid of L shape
        self.centroid_local = np.mean(self.l_shape, axis=0)

        # Scatter 1 - Local (centered at origin)
        pos_local = self.l_shape - self.centroid_local  # shift points so centroid is at origin
        self.scatter_local = gl.GLScatterPlotItem(pos=pos_local,
                                                  color=(1, 0, 0, 1))
        self.scatter_local.setGLOptions('opaque')
        self.addItem(self.scatter_local)

        # Position the local scatter at centroid location
        self.scatter_local.translate(*self.centroid_local)

        # Scatter 2 - Global (shifted in space)
        pos_global = self.l_shape + np.array([[5, 0, 0]])
        self.scatter_global = gl.GLScatterPlotItem(pos=pos_global,
                                                   color=(0, 1, 0, 1))
        self.scatter_global.setGLOptions('opaque')
        self.addItem(self.scatter_global)

        # Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.apply_rotation)
        self.timer.start(1000)

    def apply_rotation(self):
        # ----- RED: Local Rotation around its own centroid -----
        # Step 1: move to origin (inverse translate)
        """
        self.scatter_local.translate(-self.centroid_local[0],
                                    -self.centroid_local[1],
                                    -self.centroid_local[2])
        
        """
        self.scatter_local.rotate(45, 0, 0, 1, local=True)

        # Step 3: move back to centroid
        """
        self.scatter_local.translate(self.centroid_local[0],
                                    self.centroid_local[1],
                                    self.centroid_local[2])
        """
        # ----- GREEN: Global Rotation around scene origin -----
        self.scatter_global.rotate(45, 0, 0, 1, local=False)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = TransformDemo()
    w.show()
    sys.exit(app.exec())