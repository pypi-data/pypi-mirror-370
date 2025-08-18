from __future__ import annotations 
from typing import List, Optional, Tuple, Union, Dict, TYPE_CHECKING, Callable
if TYPE_CHECKING:
    from pyvol_terminal.gl_3D_graphing.graphics_items.GL3DViewBox import GL3DViewBox
from pyqtgraph import opengl
from pyqtgraph.opengl import GLGraphicsItem
from PySide6 import QtWidgets, QtCore, QtGui
import numpy as np
from OpenGL import GL
from dataclasses import dataclass, field
import weakref

from pyvol_terminal.gl_3D_graphing.meta import QABCMeta, abc
import pyqtgraph as pg

class CustomScatter(opengl.GLScatterPlotItem, QtWidgets.QGraphicsObject):
    def __init__(self, parentItem=None, **kwds):
        super().__init__(parentItem, **kwds)    
        


def create_objects():
    X = np.arange(-5, 2, 0.5)
    Y = np.arange(-5, 3, 0.5)
    X_mat, Y_mat = np.meshgrid(X, Y)

    m1, m2 = 1, 5 
    
    Z_mat = m1 * np.sin(X_mat) * np.cos(Y_mat)
    X_vec, Y_vec, Z_vect = X_mat.flatten(), Y_mat.flatten(), Z_mat.flatten()
    
    pos_scatter = np.column_stack((X_vec, Y_vec, m1 * Z_vect))
    pos_surface = [X, Y, m2 * Z_mat]
    scatter = opengl.GLScatterPlotItem(pos=pos_scatter,
                                        glOptions='opaque',
                                        color=(1, 0, 0, 1))

    """
    surface = GLSurfacePlotItem.GLSurfacePlotItem(x=pos_surface[0],
                            y=pos_surface[1],
                            z=pos_surface[2],
                            glOptions='opaque',
                            color=(1, 0, 0, 1))
    """
    surface=None
    return scatter, surface


class CustomGLViewWidget(opengl.GLViewWidget):
    sigPrepareForPaint = QtCore.Signal()
    
    
    def __init__(
        self,
        parent : QtCore.QObject | None = None,
        viewBox: GL3DViewBox | None = None,
        axisItems: dict[str, AxisItem] | None = None,
       # **kwargs
        ):  
        super().__init__(parent=parent)
        if viewBox is None:
            print(f"before create")
            viewBox = GL3DViewBox.GLViewBox()
        self.vb = viewBox
        self.sigPrepareForPaint.connect(viewBox.prepareForPaint)
        super().addItem(self.vb)
        

        # Enable or disable plotItem menu
        # Initialize axis items
        adjacent_limits = ["min", "max"]
        axes = [0, 1, 2]
        self.axes: Dict[str, Dict[str, Dict[str, AxisItem]]] = {ax: {ax_perp: {l: None for l in adjacent_limits} for ax_perp in axes if ax_perp != ax} for ax in axes}
        self.setAxisItems(axisItems)

    def setAxisItems(self, axisItems: 'Dict[str, AxisItem] | None' = None) -> None:
        if axisItems is None:
            axisItems = {}
        
        visibleAxes = []
        visibleAxes.extend(axisItems.keys()) 
        print(f"setAxisItems")
        
        for d, axis in axisItems.items():
            direction = axis.direction
            direction_perp = axis.direction_perp
            adjacent_limit = axis.adjacent_limit
            if direction == direction_perp:
                raise
            if adjacent_limit in self.axes[direction][direction_perp]:
                oldAxis = self.axes[direction][direction_perp][adjacent_limit]
                if not oldAxis is None:
                    oldAxis.unlinkFromView()
                    self.removeItem(oldAxis)

            self.axes[direction][direction_perp][adjacent_limit]=axis
            print(f"before link")
            axis.linkToView(self.vb)
            print(f"axis.linkedView(): {axis.linkedView()}")
            axisVisible = d in visibleAxes
            self.showAxis((direction, direction_perp, adjacent_limit), axisVisible)
            
            super().addItem(axis)
            
        
            
    
    def removeAxisItems(self, axisItems: 'Dict[str, AxisItem] | None' = None) -> None:
        for axis in axisItems.values():
            if axis.direction in self.axes:
                if axis in self.axes[axis.direction]:
                    axis.unlinkFromView()
                    
            

    def prepareForPaint(self):
        self.sigPrepareForPaint.emit()
    
    def paintGL(self):
        self.prepareForPaint()
        return super().paintGL()
            
            
    def addItem(self, item, ignoreBounds=False):
        print(f"CustOmGlView.AddItem")
        if ignoreBounds:
            super().addItem(item)
        else:
            if not item in self.items:
                if not ignoreBounds and not self.vb is None:
                    self.vb.addItem(item)
                super().addItem(item)

    def superAddItem(self, item):
        super().addItem(item)
    
    def showAxis(self, axis_direction_coords: Tuple[int, int, str], show: bool=True):
        s = self.getScale(axis_direction_coords)
        if show:
            s.show()
        else:
            s.hide()

    def getScale(self, axis_direction_coords: Tuple[int, int, str]):
        return self.getAxis(*axis_direction_coords)
    
    def getAxis(self, direction, direction_perp, adjacent_limit):
        """
        Return the specified AxisItem.

        Parameters
        ----------
        direction : {0, 1, 2}
            Axis direction of the axis to return.
            
        direction_perp : {0, 1, 2}  (direction != direction_perp)
            Axis perpendicular direction to return .

        adjacent_limit: {"min" "max"}

        Returns
        -------
        AxisItem
            The :class:`~pyqtgraph.AxisItem`.

        Raises
        ------
        KeyError
            If the specified axis is not present.
        """
        return self.axes[direction][direction_perp][adjacent_limit]



class Window(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)      
        self.gl_view = CustomGLViewWidget()
        print(f"after gl_instantiated")
        self.gl_view.setCameraPosition(distance=5)
        self.setCentralWidget(self.gl_view)
        
        
        self.showMaximized()
        self.scatter, self.surface = create_objects()    

        self.gl_view.addItem(self.scatter)
        
        self.scatter2, _ = create_objects2()
        self.gl_view.superAddItem(self.scatter2)

        font=QtGui.QFont("Arial", 10)
        
        
        for i in range(1, 11):
            x = opengl.GLTextItem(pos = (i/10, 0, 0), text=f"{round(i/10, 1)}", color="white", font=font)
            y = opengl.GLTextItem(pos = (0, i/10, 0), text=f"{round(i/10, 1)}", color="yellow", font=font)
            z = opengl.GLTextItem(pos = (i/10, 0, i/10), text=f"{round(i/10, 1)}", color="cyan", font=font)
            self.gl_view.addItem(x, ignoreBounds=True)
            self.gl_view.addItem(y, ignoreBounds=True)
            self.gl_view.addItem(z, ignoreBounds=True)
        
        
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_plots)
        
        
    def update_plots(self):
        """
        i,j=np.unravel_index(np.argmax(self.surface._z), self.surface._z.shape)
        z_new= self.surface._z.copy()
        z_new[i,j] = z_new[i,j]+0.5
        AbstractGraphicsItem.setData(self.surface, z=z_new)
        #self.surface.setData(z=z_new)
        
        """
        pos = self.scatter.pos.copy()
        idx = np.argmax(pos[:,0])
        pos[idx, 0] = pos[idx, 0]+1
        print(f"\npos: {pos[:,0].max()}")
        #AbstractGLPlotItem.AbstractGLPlotItem.setData(self.scatter, pos=pos)
        self.scatter.setData(pos=pos)
        
        

def main():
    app = QtWidgets.QApplication()
    win = Window()
    #win.timer.start(750)
    app.exec()

if __name__ == "__main__":
    main()