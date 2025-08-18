import pyqtgraph.opengl as gl
from PySide6 import QtWidgets
from pyqtgraph.opengl import GLTextItem
from PySide6 import QtGui, QtCore

class RotatedGLTextItem(GLTextItem):
    def __init__(self, text=None, angle=45, color=(1,1,1,1), parent=None):
        super().__init__(text=text, color=color, parent=parent)
        self.angle = angle
        
    def paint(self):
        glPushMatrix()
        glRotatef(self.angle, 0, 0, 1)  # Rotate around Z-axis
        super().paint()
        glPopMatrix()
app = QtWidgets.QApplication([])
w = gl.GLViewWidget()
w.show()

# Add a rotated text item
text = RotatedGLTextItem("Rotated Text", angle=45)
w.addItem(text)

app.exec_()