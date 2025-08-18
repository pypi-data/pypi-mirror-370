


import sys
import weakref
import numpy as np
from OpenGL.GL import * 
import pyqtgraph as pg
from pyqtgraph import opengl
import warnings
from PySide6 import QtWidgets, QtCore, QtGui
from pyvol_terminal.gl_3D_graphing import GLGraphicsItem
from pyqtgraph.opengl.GLGraphicsItem import GLGraphicsItem as pyqtGLGraphicsItem
from pyvol_terminal.gl_3D_graphing.widgets.GLScatterPlotItem import GLScatterPlotItem 
import PySide6

class CustomGraphicsItem(GLGraphicsItem.GLGraphicsItem):
    def __init__(self, parent=None):
        super().__init__(parent)


class AnotherGraphicsItem(CustomGraphicsItem):
    def __init__(self, parent=None):
        super().__init__(parent)
    
    def boundingRect(self):
        return self.childrenBoundingRect()


class ViewBox(QtWidgets.QGraphicsItem):
    def __init__(self, parent=None):
        super().__init__()
        self.__view=None
        self.__initialized=False
        self.other_graphics_item = AnotherGraphicsItem(parent=self)
        self.setGroup(QtWidgets.QGraphicsItemGroup())
    
    def boundingRect(self):
        return self.childrenBoundingRect()
    
    def _setView(self, v):
        self.__view = v

    def initialize(self):
        self.initializeGL()
        self.__initialized = True

    def isInitialized(self):
        return self.__initialized
    
    def initializeGL(self):
        pass

class CustomGLViewWidget(opengl.GLViewWidget):  
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def setViewBox(self, vb):
        self.vb=vb

class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.vb = ViewBox()
        self.gl_view = CustomGLViewWidget()
        self.setCentralWidget(self.gl_view)
        self.show()
        print(self.gl_view.isValid())
        
        self.view_box = ViewBox()
        self.gl_view.addItem(self.view_box)
        print(self.gl_view.items)

        
        x_range, y_range = [-5, 5], [-5, 5]
        self.scatter, self.surface = self.create_surface(x_range, y_range)
        self.gl_view.addItem(self.scatter)
        self.gl_view.addItem(self.surface)
        self.update()
        
        self.view_box.setParentItem(self.scatter)
        self.view_box.setParentItem(self.surface)

        
        
    def create_surface(self, x_range, y_range):
        X = np.arange(*x_range, 0.5)
        Y = np.arange(*y_range, 0.5)
        X_mat, Y_mat = np.meshgrid(X, Y)
        
        R_shifted = np.sqrt((X_mat)**2 + (Y_mat)**2)
        Z_mat = 2 + np.sin(R_shifted)                
        X_vec, Y_vec, Z_vect = X_mat.flatten(), Y_mat.flatten(), Z_mat.flatten()
        
        pos_scatter = np.column_stack((X_vec, Y_vec, Z_vect))
        pos_surface = [X, Y, 3*Z_mat]

        
        scatter = GLScatterPlotItem(pos=pos_scatter, color=(1, 0, 0, 1))
        surface = opengl.GLSurfacePlotItem(*pos_surface,
                                    glOptions='opaque',
                                    color=(0.5, 0.5, 1, 1))
        
        return scatter, surface



def main():
    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
    
