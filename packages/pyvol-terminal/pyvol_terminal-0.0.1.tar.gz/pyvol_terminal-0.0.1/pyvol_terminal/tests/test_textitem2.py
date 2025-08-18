import sys
import numpy as np
from PySide6 import QtCore, QtGui, QtWidgets
import pyqtgraph.opengl as gl
from OpenGL import GL, GLU




class GroupedGLTextItem(gl.GLGraphicsItem.GLGraphicsItem):
    """
    A custom GLGraphicsItem for efficiently drawing multiple text labels.

    This item manages and renders a collection of text strings at specified
    3D positions, optimizing the rendering process by handling them as a
    single unit.
    """

    def __init__(self, **kwds):
        super().__init__()
        self.texts = []
        self.positions = np.empty((0, 3))
        self.font = QtGui.QFont('Helvetica', 16)
        self.color = QtGui.QColor(QtCore.Qt.white)

    def setData(self, positions, texts, color=None, font=None):
        """
        Sets the data for the text items.

        Args:
            positions (np.ndarray): A NumPy array of shape (N, 3) specifying the
                                    x, y, z coordinates for each text string.
            texts (list): A list of N strings to be displayed.
            color (QtGui.QColor, optional): The color of the text. Defaults to white.
            font (QtGui.QFont, optional): The font to use for the text.
        """
        self.positions = np.asarray(positions)
        self.texts = texts
        if color is not None:
            self.color = color
        if font is not None:
            self.font = font
        self.update()

    def paint(self):
        """
        The paint method called by the GLViewWidget to render the text.
        """
        if len(self.texts) == 0:
            return

        self.setupGLState()

        painter = QtGui.QPainter(self.view())
        painter.setPen(self.color)
        painter.setFont(self.font)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        viewport = GL.glGetIntegerv(GL.GL_VIEWPORT)

        modelview_matrix = GL.glGetDoublev(GL.GL_MODELVIEW_MATRIX)
        projection_matrix = GL.glGetDoublev(GL.GL_PROJECTION_MATRIX)
        for i in range(len(self.texts)):
            pos = self.positions[i]
            text = self.texts[i]
            """
            gl_pos = modelview * QtGui.QVector4D(pos[0], pos[1], pos[2], 1.0)
            gl_pos = projection * gl_pos
            print(f"\ngl_pos\n")
            print(gl_pos)
            
            w = self.view().width()
            h = self.view().height()
            
            x = (gl_pos.x() / gl_pos.w() + 1.0) / 2.0 * w
            y = (1.0 - (gl_pos.y() / gl_pos.w())) / 2.0 * h
            """
            
            
            screen_pos = GLU.gluProject(pos[0], pos[1], pos[2],
                                       modelview_matrix,
                                       projection_matrix,
                                       viewport)

            x = screen_pos[0]
            y = self.view().height() - screen_pos[1]
            painter.drawText(QtCore.QPointF(x, y), text)
        painter.end()
 

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Optimized 3D Text Rendering")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        layout = QtWidgets.QVBoxLayout(central_widget)

        self.view = gl.GLViewWidget()
        layout.addWidget(self.view)

        # Add a grid to the scene for context
        grid = gl.GLGridItem()
        self.view.addItem(grid)

        # Create and add the grouped text item
        self.grouped_text_item = GroupedGLTextItem()
        self.view.addItem(self.grouped_text_item)

        # Initial data for the text items
        self.positions = np.array([
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1]
        ])
        self.texts = ["Text 1", "Text 2", "Text 3"]
        
        self.grouped_text_item.setData(positions=self.positions, texts=self.texts)

        # Timer to update the text and positions
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_text)
        #self.timer.start(50)  # Update every 50ms

        self.frame_count = 0

    def update_text(self):
        """
        Updates the positions and text of the labels.
        """
        # Animate the positions
        angle = np.radians(self.frame_count * 2)
        rotation_matrix_z = np.array([
            [np.cos(angle), -np.sin(angle), 0],
            [np.sin(angle), np.cos(angle), 0],
            [0, 0, 1]
        ])
        
        new_positions = np.dot(self.positions, rotation_matrix_z.T)

        # Update the text
        new_texts = [f"Frame: {self.frame_count}" for _ in self.texts]

        # Update the data in the grouped item
        self.grouped_text_item.setData(positions=new_positions, texts=new_texts)
        
        self.frame_count += 1

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())