import sys
import numpy as np
from PySide6 import QtCore, QtGui, QtWidgets    
from pyqtgraph import opengl
from OpenGL import GL, GLU
from pprint import pprint   

def create_grid(rotation, translation):
    grid = opengl.GLGridItem()
    grid.setSize(x=1, y=1, z=1)
    grid.setSpacing(x=0.2, y=0.2, z=0.2)
    grid.rotate(*rotation)
    grid.translate(*translation)
    return grid

def create_txt(pos):
    return opengl.GLTextItem(text = f"{pos}", pos=pos, font=QtGui.QFont("Arial", 9))
    
    

def map_2D_coords_to_3D(widget, x, y):
    widget_width = widget.width()
    widget_height = widget.height()
    device_pixel_ratio = widget.window().screen().devicePixelRatio()

    ndc_x = x / widget_width
    ndc_y = y / widget_height

    viewport = GL.glGetIntegerv(GL.GL_VIEWPORT)
    
    _, _, viewport_width, viewport_height = viewport

    mouse_x_physical = ndc_x * viewport_width
    mouse_y_physical = ndc_y * viewport_height
    mouse_y_physical = viewport_height - mouse_y_physical 
    
    
    modelview = np.array(widget.viewMatrix().data()).reshape(4, 4)
    projection = np.array(widget.projectionMatrix(viewport, (0, 0, device_pixel_ratio * widget_width, device_pixel_ratio* widget_height)).data()).reshape(4, 4)
    print("proj:")
    pprint(projection.round(4).tolist())
    print("view:")
    pprint(modelview.round(4).tolist())
    depth = GL.glReadPixels(int(mouse_x_physical), int(mouse_y_physical), 1, 1, GL.GL_DEPTH_COMPONENT, GL.GL_FLOAT)[0][0]
    print(f"depth: {depth}")
    world_x, world_y, world_z = GLU.gluUnProject(mouse_x_physical, mouse_y_physical, depth, modelview, projection, viewport)

    return world_x, world_y, world_z

def map_3D_coords_to_2D(widget, world_x, world_y, world_z):
    device_pixel_ratio = widget.window().screen().devicePixelRatio()
    widget_height = widget.height()
    widget_width = widget.width()
    
    viewport = GL.glGetIntegerv(GL.GL_VIEWPORT)
    _, _, viewport_width, viewport_height = viewport
    
    modelview = np.array(widget.viewMatrix().data()).reshape(4, 4)
    projection = np.array(widget.projectionMatrix(viewport,
                                                (0, 0, device_pixel_ratio * widget_width, device_pixel_ratio * widget_height)).data()).reshape(4, 4)
    
    px_x, px_y, px_z = GLU.gluProject(world_x, world_y, world_z, modelview, projection, viewport)
    px_y = viewport_height - px_y
    return px_x, px_y, px_z




def world_to_viewport_pixel(widget: opengl.GLViewWidget, world_coords):
    if len(world_coords) == 3:
        world_coords = np.append(world_coords, 1.0)

    mvp = widget.currentProjection() * widget.currentModelView()
    mvp_np = np.array(mvp.data()).reshape(4, 4)

    clip_coords = mvp_np @ world_coords

    ndc_coords = clip_coords[:3] / clip_coords[3]

    viewport = widget.geometry()
    x_pixel = (ndc_coords[0] + 1) * 0.5 * viewport.width() + viewport.x()
    y_pixel = (1 - (ndc_coords[1] + 1) * 0.5) * viewport.height() + viewport.y()
    z_pixel = (ndc_coords[2] + 1) / 2
    return x_pixel, y_pixel, z_pixel


class CustomGLViewWidget(opengl.GLViewWidget):
    def __init__(self):
        super().__init__()
    
    def mouseMoveEvent(self, ev):
        return super().mouseMoveEvent(ev)
    
    def wheelEvent(self, ev):
        super().wheelEvent(ev)
        self.compute_optimal_clipping()
        return 
    
    def initializeGL(self):
        super().initializeGL()
        GL.glEnable(GL.GL_DEPTH_TEST)  
        return 

    def mousePressEvent(self, ev):
        if ev.buttons() == QtCore.Qt.MouseButton.LeftButton:
            print("\n")
            x_px, y_px = ev.x(), ev.y()
            world = map_2D_coords_to_3D(self, x_px, y_px)
            print(f"window coords: {np.round((x_px, y_px), 3)}")
            print(f"world coords: {np.round(world, 3)}")
            print(f"back to px1: {np.round(world_to_viewport_pixel(self, world),3)}")
            print(f"back to px2: {np.round(map_3D_coords_to_2D(self, *world),3)}")
            _, _, width, height = self.getViewport()
            print(f"width/2: {np.round(width/2,2)}")
            print(f"height/2: {np.round(height/2,2)}")
            
            
        return super().mousePressEvent(ev)
    
    def compute_optimal_clipping(self):
        return 
        largest_point_distance = np.sqrt(3)
        near_clip = max(0.0001, self.opts['distance'] - 1.01 * largest_point_distance) 
        far_clip = self.opts['distance'] 
        
        self.opts["near"] = near_clip
        self.opts["far"] = far_clip
        self.update()

    
    
  #  def keyPressEvent(self, ev):
       # if ev.key() == QtCore.Qt.Key.Key_T:
            
      #  return super().keyPressEvent(ev)
#
def create_pos():
    X = np.arange(-5, 5, 0.5)
    Y = np.arange(-5, 5, 0.5)
    X_mat, Y_mat = np.meshgrid(X, Y, indexing="xy")
    R = np.sqrt(X_mat**2 + Y_mat**2)
    

    m1 = 3
    
    Z_mat = m1 * np.sin(R) 
    X = (X - X.min()) / (X.max() - X.min())
    Y = (Y - Y.min()) / (Y.max() - Y.min())
    Z_mat = (Z_mat - Z_mat.min()) / (Z_mat.max() - Z_mat.min())

    
    return X, Y, Z_mat

class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.gl_widget = CustomGLViewWidget()
        self.setCentralWidget(self.gl_widget)
        self.gl_widget.opts["distance"] = 5
        
        self.g1 = create_grid(rotation=(0, 0, 0, 0), translation=(0.5, 0.5, 0))
        self.g2 = create_grid(rotation=(90, 0, 1, 0), translation=(0, 0.5, 0.5))
        self.g3 = create_grid(rotation=(90, 1, 0, 0), translation=(0.5, 0, 0.5))
        
        text_items = [create_txt((0,0,0)), create_txt((0,0,1)),create_txt((1,0,0)),create_txt((0,1,0))] 
        for txt_item in text_items:
            self.gl_widget.addItem(txt_item)


        self.gl_widget.addItem(self.g1)
        self.gl_widget.addItem(self.g2)
        self.gl_widget.addItem(self.g3)
        
        X, Y, Z_mat = create_pos()
        Z_mat += 0.5
        self.surface = opengl.GLSurfacePlotItem(X, Y, Z_mat, glOptions='opaque', color = (1, 0, 1, 1))
        
        self.gl_widget.addItem(self.surface)
        
        self.showMaximized()
        
def main():
    app = QtWidgets.QApplication()
    win = Window()
    app.exec()


if __name__ == "__main__":
    main()