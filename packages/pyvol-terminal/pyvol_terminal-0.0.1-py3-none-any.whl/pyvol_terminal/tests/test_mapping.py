from PySide6 import QtWidgets, QtCore
from pyqtgraph.opengl import GLViewWidget
import numpy as np
from OpenGL import GL, GLU
import sys

def map_2D_coords_to_3D(widget, x, y):
    widget_height = widget.height()
    widget_width = widget.width()
    device_pixel_ratio = widget.window().screen().devicePixelRatio()

    x_norm = x / widget_width
    y_norm = y / widget_height

    viewport = GL.glGetIntegerv(GL.GL_VIEWPORT)
    _, _, viewport_width, viewport_height = viewport

    mouse_x_physical = x_norm * viewport_width
    mouse_y_physical = y_norm * viewport_height
    mouse_y_physical = viewport_height - mouse_y_physical 
    
    depth = GL.glReadPixels(int(mouse_x_physical), int(mouse_y_physical),  1, 1, GL.GL_DEPTH_COMPONENT, GL.GL_FLOAT)[0][0]

    modelview = np.array(widget.viewMatrix().data()).reshape(4, 4)
    projection = np.array(widget.projectionMatrix(viewport, (0, 0, device_pixel_ratio * widget_width, device_pixel_ratio* widget_height)).data()).reshape(4, 4)
    
    world_x, world_y, world_z = GLU.gluUnProject(mouse_x_physical, mouse_y_physical, depth, modelview, projection, viewport)
    px_x, px_y, px_z = GLU.gluProject(world_x, world_y, world_z, modelview, projection, viewport)
    
    px_y = viewport_height - px_y
    
    world_coords = world_x, world_y, world_z
    px_coords = px_x, px_y, px_z
    
    return world_coords, px_coords



class CustomGLViewWidget(GLViewWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMouseTracking(True)
        self.setAttribute(QtCore.Qt.WA_Hover)
        self.setAttribute(QtCore.Qt.WA_DontCreateNativeAncestors) 

    def mousePressEvent(self, event):
        match event.buttons().value :    
            case 1: 
                self.interacting=True
                pos = event.pos()
                world_coords, px_coords = map_2D_coords_to_3D(self, pos.x(), pos.y())
                print(f"\npos: {np.round((pos.x(), pos.y()), 4)}")
                print(f"world: {np.round((world_coords), 4)}")
                print(f"px_coords: {np.round((px_coords), 4)}")

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle('Volatility Surface')
        self.widget_central = QtWidgets.QWidget()
        self.setCentralWidget(self.widget_central)
        self.layout_main = QtWidgets.QVBoxLayout()
        self.widget_central.setLayout(self.layout_main)
        
        self.view_widget = CustomGLViewWidget()
        self.vw_layout = QtWidgets.QVBoxLayout()
        self.layout_main.addLayout(self.vw_layout)
        self.layout_main.addWidget(self.view_widget)
        self.showMaximized()
        
        

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec())
    
