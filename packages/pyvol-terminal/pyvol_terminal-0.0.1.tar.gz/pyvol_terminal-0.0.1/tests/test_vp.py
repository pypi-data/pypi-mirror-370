from PySide6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsRectItem
from PySide6.QtCore import QRectF
import sys
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from pyqtgraph import opengl

app = QApplication([])

view = QGraphicsView()
gl_view = opengl.GLViewWidget()
view.setViewport(gl_view)  # 🔧 Use OpenGL to render the QGraphicsView

scene = QGraphicsScene()
view.setScene(scene)

rect_item = QGraphicsRectItem(QRectF(0, 0, 100, 100))
scene.addItem(rect_item)

view.show()
sys.exit(app.exec())