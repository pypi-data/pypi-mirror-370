

from PySide6 import QtWidgets, QtCore, QtGui

import sys
import weakref
import numpy as np
from OpenGL.GL import * 
import pyqtgraph as pg
from pyqtgraph import opengl
import warnings
from pyqtgraph.Qt import QT_LIB, QtCore, QtWidgets
from pyvol_terminal.gl_3D_graphing import GLGraphicsItem

from pyvol_terminal.gl_3D_graphing.widgets.GLScatterPlotItem import GLScatterPlotItem 




def get_item_data(item):
    if isinstance(item, opengl.GLScatterPlotItem):
        return item.pos
    elif isinstance(item, opengl.GLMeshItem):
        return item.opts['meshdata'].vertexes()
    elif isinstance(item, opengl.GLLinePlotItem):
        return item.pos
    elif isinstance(item, opengl.GLBarGraphItem):
        return item.points()
    return None

def compute_scene_bbox(items):
    min_vals, max_vals = None, None
    
    for item in items:
        data = get_item_data(item)
        if data is None or len(data) == 0:
            continue
            
        if not isinstance(data, np.ndarray):
            data = np.array(data)
            
        if data.ndim == 1:
            data = data[np.newaxis, :]
        if data.shape[1] == 2:
            data = np.hstack([data, np.zeros((len(data), 1))])
            
        item_min = np.nanmin(data, axis=0)
        item_max = np.nanmax(data, axis=0)
        
        if min_vals is None:
            min_vals, max_vals = item_min, item_max
        else:
            min_vals = np.minimum(min_vals, item_min)
            max_vals = np.maximum(max_vals, item_max)
    
    if min_vals is None:
        return np.array([0, 0, 0]), np.array([1, 1, 1])
    
    return min_vals, max_vals


class WeakList(object):

    def __init__(self):
        self._items = []

    def append(self, obj):
        self._items.insert(0, weakref.ref(obj))

    def __iter__(self):
        i = len(self._items)-1
        while i >= 0:
            ref = self._items[i]
            d = ref()
            if d is None:
                del self._items[i]
            else:
                yield d
            i -= 1

class CustomTransform(QtGui.QTransform):
    def __init__(self, parent=None):
        super().__init__()
        self._vertical_shear = 0.0 
        self._horizontal_shear = 0.0
        self.updateTransform()

    def getVerticalShear(self):
        return self._vertical_shear
    
    def setVerticalShear(self, shear):
        if self._vertical_shear != shear:
            self._vertical_shear = shear
            self.updateTransform()

    def getHorizontalShear(self):
        return self._horizontal_shear

    def setHorizontalShear(self, shear):
        if self._horizontal_shear != shear:
            self._horizontal_shear = shear
            self.updateTransform()

    def updateTransform(self):
        self.setMatrix(1.0, self._horizontal_shear, 0.0,
                      self._vertical_shear, 1.0, 0.0,
                      0.0, 0.0, 1.0)

    verticalShear = QtCore.Property(float, getVerticalShear, setVerticalShear)
    horizontalShear = QtCore.Property(float, getHorizontalShear, setHorizontalShear)


class CustomGraphicsItem(QtWidgets.QGraphicsItem):
    def __init__(self, parent=None):
        super().__init__(parent)



class CustomItemGroup(GLGraphicsItem.GLGraphicsItem):
    def __init__(self, parent=None):
        super().__init__(parent)
        QtWidgets.QGraphicsObject.setFlag(self, QtWidgets.QGraphicsObject.GraphicsItemFlag.ItemHasNoContents)
        
    def addItem(self, item):
        item.setParentItem(self)
        print("\n")
        print(item)
        print(item.parentItem())
        print(self)
        #self.normaliseToparent()

    def boundingRect(self):
        return self.childrenBoundingRect()
    
    def normaliseToparent(self):
        rect = self.boundingRect()
        
        tr = self.transform()
        tr.scale(1/rect.width(), 1/rect.height())
        tr.translate(-rect.x(), -rect.y())
        self.update()

class ChildGroup(CustomItemGroup):
    def __init__(self, parent):
        super().__init__(parent=parent)
        print(f"self.group(): {self.group()}")
        self.itemsChangedListeners = WeakList()

    def itemChange(self, change, value):
        ret = super().itemChange(change, value)
        if change in [
            QtWidgets.QGraphicsItem.ItemChildAddedChange,
            QtWidgets.QGraphicsItem.ItemChildRemovedChange,
        ]:
            try:
                for listener in self.itemsChangedListeners:
                    listener.itemsChanged()
            except AttributeError:
                pass
        return ret
    
    
class ViewBox(QtWidgets.QGraphicsItem):
    
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.__view=None

        #self.childGroup: ChildGroup = ChildGroup(parent=self)
        #self.childGroup.setParentItem(self)
        #self.childGroup.itemsChangedListeners.append(self)
        
    def _setView(self, v):
        self.__view = v
        
        
    def addItem(self, item):
        print(f"ViewBox addItem: {item}")
        self.group().addToGroup(item)
        #self.childGroup.addItem(item)
        #self.normalize_scene()
        
    def itemsChanged(self):
        print("itemsChanged")
        self.update()
    
    
    
    
    def normalize_scene(self):
        min_vals, max_vals = compute_scene_bbox(self.childItems())
        self.min_vals = min_vals
        self.max_vals = max_vals
        
        diff = max_vals - min_vals
        

        self.vb_min = min_vals - diff * self.padding
        self.vb_max = max_vals + diff* self.padding
        
        ranges = self.vb_max - self.vb_min
        ranges[ranges == 0] = 1.0
        
        self.transform_matrix = QtGui.QMatrix4x4()
        #tr = CustomTransform()
       # self.childGroup.setTransform(tr)

        self.transform_matrix.scale(1/ranges[0], 1/ranges[1], 1/ranges[2])
        self.transform_matrix.translate(-self.vb_min[0], -self.vb_min[1], -self.vb_min[2])
        for child in self.childItems():
            child.setTransform(self.transform_matrix)
            
    def boundingRect(self):
        return self.childrenBoundingRect()

class CustomGLViewWidget(opengl.GLViewWidget):  
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def addItem(self, item, ignoreBounds=False):
        if isinstance(item, ViewBox):
            self.setViewBox(item)
            return
        if not ignoreBounds and not isinstance(item, ViewBox):
            self.vb.addItem(item)
        super().addItem(item)   

    def setViewBox(self, vb):
        self.vb=vb


class Window(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.setWindowTitle("ItemGroup with QOpenGLWidget Example")
        
        
        self.gl_view = opengl.GLViewWidget()
        self.setCentralWidget(self.gl_view)
        self.view_box = ViewBox(parent=self.gl_view)
        
        self.gl_view.addItem(self.view_box)
        self.view_box.setGroup(QtWidgets.QGraphicsItemGroup())
        
        
        x_range, y_range = [-5, 5], [-5, 5]
        self.scatter, self.surface = self.create_surface(x_range, y_range)
        self.view_box.setParentItem(self.scatter)
        self.view_box.setParentItem(self.surface)
        #self.gl_view.addItem(self.scatter)
        #self.gl_view.addItem(self.surface)
        
        self.gl_view.opts["distance"]=25

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_data)
        
        nticks=15
        for i, j in zip(np.linspace(*x_range, nticks), np.linspace(*y_range, nticks)):
            x = opengl.GLTextItem(pos = (i, 0, 0), text=f"{round(i, 1)}", color="white")
            y = opengl.GLTextItem(pos = (0, j, 0), text=f"{round(j, 1)}", color="yellow")
            z = opengl.GLTextItem(pos = (0, 0, i), text=f"{round(i, 1)}", color="cyan")
            self.gl_view.addItem(x, True)
            self.gl_view.addItem(y, True)
            self.gl_view.addItem(z, True)
        self.showMaximized()
        self.update()
        
        

        
       # self.timer.start(1500)
        
    def update_data(self):
        self.rect1.setRect(2 * 1200, 2*1200, 50, 50)

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
        
        from types import MethodType
        return scatter, surface

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
    

    
