import numpy as np
from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.Qt3DCore import Qt3DCore
import pyqtgraph.opengl as gl
import sys


class CustomTextItem(gl.GLTextItem, QtWidgets.QGraphicsItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


def create_qgeometry_data(points: np.ndarray) -> Qt3DCore.QGeometry:
    """Convert numpy array points into a QGeometry object."""
    geometry = Qt3DCore.QGeometry()

    # Byte buffer for the vertex data
    buffer = Qt3DCore.QBuffer(geometry)
    float_data = points.astype(np.float32).tobytes()
    buffer.setData(QtCore.QByteArray(float_data))

    # Position attribute
    position_attribute = Qt3DCore.QAttribute(geometry)
    position_attribute.setName(Qt3DCore.QAttribute.defaultPositionAttributeName())
    position_attribute.setVertexBaseType(Qt3DCore.QAttribute.Float)
    position_attribute.setVertexSize(3)
    position_attribute.setAttributeType(Qt3DCore.QAttribute.VertexAttribute)
    position_attribute.setBuffer(buffer)
    position_attribute.setByteOffset(0)
    position_attribute.setByteStride(3 * 4)
    position_attribute.setCount(len(points))

    geometry.addAttribute(position_attribute)
    return geometry

"""
            x = gl.GLTextItem(pos = (i/10, 0, 0), text=f"{round(i/10, 1)}", color="white", )
            y = gl.GLTextItem(pos = (0, i/10, 0), text=f"{round(i/10, 1)}", color="yellow", )
            z = gl.GLTextItem(pos = (i/10, 0, i/10), text=f"{round(i/10, 1)}", color="cyan", )
            


"""

class ScatterPlotExample(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Scatter Plot with PyQtGraph and Qt3DCore QGeometry")
        self.resize(800, 600)

        # Main OpenGL view widget
        self.gl_view = gl.GLViewWidget()
        self.setCentralWidget(self.gl_view)
        self.gl_view.opts['distance'] = 20

        self.item_group = QtWidgets.QGraphicsItemGroup()
        points=[]
        for i in range(1, 11):
            x = CustomTextItem(pos = (i/10, 0, 0), text=f"{round(i/10, 1)}", color="white", )
            y = CustomTextItem(pos = (0, i/10, 0), text=f"{round(i/10, 1)}", color="yellow", )
            z = CustomTextItem(pos = (i/10, 0, i/10), text=f"{round(i/10, 1)}", color="cyan", )
            
            
            #self.gl_view.addItem(x)
            #self.gl_view.addItem(y)
            #self.gl_view.addItem(z)
            points.append((i/10, 0, 0))
            points.append((0, i/10, 0))
            points.append((i/10, 0, i/10))
            self.item_group.addToGroup(x)
            self.item_group.addToGroup(y)
            self.item_group.addToGroup(z)

        points = np.array(points)
        self.geometry1 = create_qgeometry_data(points)
        
            
        




if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = ScatterPlotExample()
    window.show()
    sys.exit(app.exec())
