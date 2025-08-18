import sys
import numpy as np
from PySide6 import QtWidgets, QtGui, QtCore
import pyqtgraph.opengl as gl
from OpenGL.GL import *


class GroupedGLTextItem(gl.GLGraphicsItem.GLGraphicsItem):
    def __init__(self, parent=None):
        super().__init__()
        self._positions = np.empty((0, 3))
        self._texts = []
        self._color = QtGui.QColor(255, 255, 255)
        self._font = QtGui.QFont("Helvetica", 12)

    def setData(self, positions, texts, color=QtGui.QColor(255, 255, 255)):
        self._positions = np.array(positions)
        self._texts = texts
        self._color = color
        self.update()

    def paint(self):
        view = self.view()
        if view is None:
            return

        self.setupGLState()
        cam = view.cameraParams()

        modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
        projection = glGetDoublev(GL_PROJECTION_MATRIX)
        width, height = view.width(), view.height()
        viewport = (0, 0, width, height)

        painter = QtGui.QPainter(view)
        painter.setPen(self._color)
        painter.setFont(self._font)

        for pos, text in zip(self._positions, self._texts):
            screen_pos = self.__project(pos, modelview, projection, viewport)
            if screen_pos is not None:
                painter.drawText(int(screen_pos.x()), int(screen_pos.y()), text)

        painter.end()

    def __project(self, obj_pos, modelview, projection, viewport):
        obj_vec = np.append(np.array(obj_pos), [1.0])

        view_vec = np.matmul(modelview.T, obj_vec)
        proj_vec = np.matmul(projection.T, view_vec)

        if proj_vec[3] == 0.0:
            return QtCore.QPointF(0, 0)

        proj_vec[0:3] /= proj_vec[3]

        return QtCore.QPointF(
            viewport[0] + (1.0 + proj_vec[0]) * viewport[2] / 2,
            viewport[1] + (1.0 + proj_vec[1]) * viewport[3] / 2
        )


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Optimized 3D Text Rendering")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        layout = QtWidgets.QVBoxLayout(central_widget)

        self.view = gl.GLViewWidget()
        self.view.setCameraPosition(distance=20)
        layout.addWidget(self.view)

        # Add grid for context
        grid = gl.GLGridItem()
        grid.setSize(10, 10)
        grid.setSpacing(1, 1)
        self.view.addItem(grid)

        # Create grouped text item
        self.text_item = GroupedGLTextItem()
        positions = [[0, 0, 0], [2, 2, 0], [-2, 1, 1]]
        texts = ["Origin", "Top Right", "Left Up"]
        self.text_item.setData(positions, texts, color=QtGui.QColor("yellow"))
        self.view.addItem(self.text_item)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
