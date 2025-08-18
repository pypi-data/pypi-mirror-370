from __future__ import annotations 
from typing import List, Optional, Tuple, Union, Dict, TYPE_CHECKING, Callable, ClassVar

from pyvol_terminal.gl_3D_graphing.widgets import GL3DViewWidget
if TYPE_CHECKING:
    from pyvol_terminal.gl_3D_graphing.graphics_items.GLViewBox import GLViewBox
from pyqtgraph import opengl
from PySide6 import QtWidgets, QtCore, QtGui
import numpy as np
from OpenGL import GL
from pyqtgraph.Qt import QT_LIB
import importlib
import pyqtgraph as pg
from pyvol_terminal.gl_3D_graphing.graphics_items.GL3DAxisItem import GL3DViewBox
from pyvol_terminal.gl_3D_graphing.graphics_items import GL3DViewBox, GLSurfacePlotItem, AbstractGLPlotItem, AbstractGLGraphicsItem, GLScatterPlotItem
from pyqtgraph import opengl
import sys
import cProfile
import sys
import pstats
from pyqtgraph import ButtonItem, icons
from dataclasses import dataclass, InitVar, field
from abc import ABC, abstractmethod, ABCMeta
import abc
from PySide6 import QtGui, QtCore, QtWidgets
from PySide6.QtWidgets import QGraphicsItem
from enum import Enum, EnumType, Flag, IntFlag
from pyqtgraph import Transform3D
from pyqtgraph import functions as fn
from pyqtgraph.opengl.GLGraphicsItem import GLGraphicsItem
import warnings
import weakref

class QABCMeta(ABCMeta, type(QtCore.QObject)):
    """Meta class for OpenGL mixin objects, combining ABC and QObject."""
    def __new__(mcls, name, bases, ns, **kw):
        cls = super().__new__(mcls, name, bases, ns, **kw)
        abc._abc_init(cls)
        return cls
    def __call__(cls, *args, **kw):
        print(f"cls: {cls}")
        if cls.__abstractmethods__:
            raise TypeError(f"Can't instantiate abstract class {cls.__name__} without an implementation for abstract methods {set(cls.__abstractmethods__)}")
        return super().__call__(*args, **kw)


class GLGraphicsItemMixin(GLGraphicsItem, metaclass=QABCMeta):
    def __init__(self, parentItem: 'GLGraphicsItemMixin'=None, **kwargs):
        self.__parent = None
        self.__view = None
        self.__children = list()
        self.__transform = Transform3D()
        self.__visible = True
        self.__initialized = False
        self.__glOpts = {}
        print("GLGraphicsItemMixin")
        super().__init__(parentItem=parentItem, **kwargs)
        
    def _paintHelper(self, *args, **kwargs):
        self.childPaint()
    
    @abstractmethod
    def childPaint(self):...

class _BaseGLPlotDataItemMixin(GLGraphicsItemMixin):
    sigPlotChanged = QtCore.Signal(object) 
    
    def __init__(self, parentItem=None, **kwargs):
        print("GLPlotDataItemMixin")
        super().__init__(parentItem=parentItem, **kwargs)
        
class MeshGLPlotDataItemMixin(_BaseGLPlotDataItemMixin):
    def __init__(self, parentItem=None, **kwargs):
        print("GLPlotDataItemMixin")
        super().__init__(parentItem=parentItem, **kwargs)

        

class CustomPlotDataItemClass(opengl.GLSurfacePlotItem):
    def __init__(self, parentItem=None, **kwargs):
        print("CustomPlotDataItemClass")
        super().__init__(parentItem=parentItem, **kwargs)
        
    def childPaint(self):
        return opengl.GLSurfacePlotItem.paint(self)

class mixedPlotDataItemClass(MeshGLPlotDataItemMixin, CustomPlotDataItemClass):
    def __init__(self, x=None, y=None, z=None, colors=None, parentItem=None, **kwds):
        print("mixedPlotDataItemClass")
        super().__init__(parentItem=parentItem, x=x, y=y, z=z, colors=colors, **kwds)

    def childPaint(self):
        return opengl.GLTextItem.paint(self)

class customGraphicsItemClass(opengl.GLTextItem):
    def __init__(self, parentItem=None, **kwargs):
        super().__init__(parentItem=parentItem, **kwargs)
    

class mixedCustomGraphicsItemClass(GLGraphicsItemMixin, customGraphicsItemClass):
    def __init__(self, text="Hello", pos=None, color=(1, 1, 1, 1), font=None, parentItem=None, **kwds):
        print("Mixed Text Item")
        super().__init__(text=text, pos=pos, color=color, font=font, parentItem=parentItem, **kwds)
        
    def childPaint(self):
        return opengl.GLTextItem.paint(self)

class customGLGraphItemClass(opengl.GLGraphItem):
    def __init__(self, parentItem=None, **kwargs):
        super().__init__(parentItem=parentItem, **kwargs)

class mixedcustomGLGraphItemClass(GLGraphicsItemMixin, customGLGraphItemClass):
    def __init__(self, text="Hello", pos=None, color=(1, 1, 1, 1), font=None, parentItem=None, **kwds):
        print("Mixed customGLGraphItem Item")
        super().__init__(text=text, pos=pos, color=color, font=font, parentItem=parentItem, **kwds)


def create_pos():
    X = np.arange(-5, 5, 0.5)
    Y = np.arange(-3, 3, 0.5)
    X_mat, Y_mat = np.meshgrid(X, Y, indexing="xy")
    R = np.sqrt(X_mat**2 + Y_mat**2)

    m1 = 1
    
    Z_mat = m1 * np.sin(R) 
    return X_mat, Y_mat, Z_mat, m1

class CustomColorMap(pg.ColorMap):
    def __init__(self, colourmap_style: str):
        pos = np.linspace(0, 1, 500)          
        try:
            colourmap = pg.colormap.get(colourmap_style)
        except:
            print(f"{colourmap_style} is not in pyqtgraph, using default inferno")
            colourmap = pg.colormap.get("inferno")

        colors = colourmap.map(pos, mode='byte')        
        super().__init__(pos=pos, color=colors, mode='byte')

def create_objects(X_mat, Y_mat, Z_mat, m1) -> AbstractGLPlotItem:

    
    X_vec, Y_vec, Z_vect = X_mat.flatten(), Y_mat.flatten(), Z_mat.flatten()
    
    pos_scatter = np.column_stack((X_vec, Y_vec, Z_vect))
    """
    scatter = GLScatterPlotItem.GLScatterPlotItem(pos=pos_scatter,
                                                  glOptions='opaque',
                                                  color=(1, 0, 1, 1)
                                                  )
    """
    scatter=None
    pos_surface = X_mat[0], Y_mat[:,1], Z_mat.T
    colormap = CustomColorMap("inferno")
    
    z_norm = (Z_mat - Z_mat.min()) / (Z_mat.max() - Z_mat.min())
    colors = colormap.map(np.linspace(0, 1, 500), mode='byte')
    # Map normalized Z to RGB colors


    
    surface = mixedPlotDataItemClass(x=pos_surface[0],
                                                  y=pos_surface[1],
                                                  z=pos_surface[2],
                                                  glOptions='opaque',
                                                  shader="shaded",
                                                  colors=colors
                                                  )
    
    print(f"surface._x: {surface._x}")
    return scatter, surface




class Window(QtWidgets.QMainWindow):
    def __init__(self, *args):
        super().__init__(*args)
        
        self.gl_view = opengl.GLViewWidget()
        """
        worldRange=[[0.,1.], [0.,1.],[0.,1.]]

        self.viewBox = GLViewBox.GLViewBox(worldRange=worldRange)
        
        self.gl_view = GLPlotWidget.GLPlotWidget(
                                            # worldRange=worldRange,
                                             #worldRange=np.array([[0.,1.]]*3)
                                             viewBox=self.viewBox
                                             )

        """
   #     self.central_layout = QtWidgets.QVBoxLayout(self)
    #    self.central_layout.addWidget(self.gl_view)
        self.setCentralWidget(self.gl_view)
        self.gl_view.opts["distance"]=5
        self.gl_view.update()
        self.setCentralWidget(self.gl_view)
        self.setGeometry(0, 0, 500, 300)
        self.show()
        self.X_mat, self.Y_mat, self.Z_mat, self.m1 = create_pos()
        self.scatter, self.surface = create_objects(self.X_mat, self.Y_mat, self.Z_mat, self.m1)    
        
        self.gl_view.addItem(self.surface)
        
        
def main():
    import sys
    app = QtWidgets.QApplication(sys.argv)
    win = Window()
   # win.timer.start(750)
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
    
#%%
"""
from abc import ABC, abstractmethod, ABCMeta
import abc
from pyqtgraph import opengl, Transform3D


class GObj:
    def __init__(self, *args, **kwargs):
        print("GP1")


class pyqtGraphicsItem(GObj):
    def __init__(self, *args, **kwargs):
        print("GP2")
        super().__init__(*args,  **kwargs)

class GLMeta(abc.ABCMeta, type(GObj)):
    pass

class Parent1(pyqtGraphicsItem):
    def __init__(self, *args, **kwargs):
        print("Parent1")
        super().__init__(*args,  **kwargs)

    def paint(self):
        print("parent1 paint")



class GLGraphicsItemMixin(pyqtGraphicsItem, metaclass=GLMeta):
    def __init__(self, parentItem: 'GLGraphicsItemMixin'=None, **kwargs):
        self.__parent = None
        self.__view = None
        self.__children = list()
        self.__transform = Transform3D()
        self.__visible = True
        self.__initialized = False
        self.__glOpts = {}
        print("GLGraphicsItemMixin")
        super().__init__(parentItem=parentItem, **kwargs)
        
    def _paintHelper(self, *args, **kwargs):
        self.childPaint()
    
    @abstractmethod
    def childPaint(self):...
 


class GLPlotDataItemMixin(GLGraphicsItemMixin):

    def __init__(self, parentItem=None, **kwargs):
        print("GLPlotDataItemMixin")
        super().__init__(parentItem=parentItem, **kwargs)

class CustomPlotDataItemClass(Parent1):
    def __init__(self, parentItem=None, **kwargs):
        print("CustomPlotDataItemClass")
        super().__init__(parentItem=parentItem, **kwargs)
        
class mixedPlotDataItemClass(GLPlotDataItemMixin, CustomPlotDataItemClass):
    def __init__(self, x=None, y=None, z=None, colors=None, parentItem=None, **kwds):
        print("mixedPlotDataItemClass")
        super().__init__(parentItem=parentItem, x=x, y=y, z=z, colors=colors, **kwds)

    def childPaint(self):
        return Parent1.paint(self)




mixedPlotDataItemClass()
"""