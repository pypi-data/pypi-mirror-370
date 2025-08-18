from __future__ import annotations 
from typing import List, Optional, Tuple, Union, Dict, TYPE_CHECKING, Callable, Any

from pyvol_terminal.gl_3D_graphing.widgets import GL3DViewWidget

if TYPE_CHECKING:
    from pyvol_terminal.gl_3D_graphing.graphics_items.GLViewBox import GLViewBox
import importlib
from pprint import pprint   
from OpenGL import GL
from OpenGL.GL import shaders
import numpy as np

from pyqtgraph.Qt import QtGui, QT_LIB
from pyqtgraph import functions as fn
from pyqtgraph.opengl.GLGraphicsItem import GLGraphicsItem

if QT_LIB in ["PyQt5", "PySide2"]:
    QtOpenGL = QtGui
else:
    QtOpenGL = importlib.import_module(f"{QT_LIB}.QtOpenGL")

__all__ = ['GLLinePlotItem']
from pyqtgraph import opengl
from PySide6 import QtWidgets, QtCore, QtGui
import numpy as np
from OpenGL import GL
from pyqtgraph.Qt import QT_LIB
import importlib
import pyqtgraph as pg
from pyvol_terminal.gl_3D_graphing.graphics_items.GL3DAxisItem import GL3DViewBox
from pyvol_terminal.gl_3D_graphing.graphics_items import GL3DViewBox
from pyqtgraph import opengl
import sys
import cProfile
import sys
import pstats
from pyqtgraph import ButtonItem, icons
QtOpenGL = importlib.import_module(f"{QT_LIB}.QtOpenGL")

from PySide6.QtTest import QTest
from pyqtgraph.opengl.GLGraphicsItem import GLGraphicsItem
from pyqtgraph.opengl import GLLinePlotItem, GLScatterPlotItem
from pyqtgraph import Transform3D
from pyvol_terminal.gl_3D_graphing.graphics_items.GL3DGraphicsItems import GL3DLinePlotDataItem



class CustomGLLinePlotItem(GLLinePlotItem):
    def __init__(self, *args, **kwargs):
        self._updatesBlocked=False
        super().__init__(*args, **kwargs)   
        
    def updatesBlocked(self):
        return self._updatesBlocked
    
    def update(self):
        if not self.updatesBlocked():
            super().update()
    
    def blockUpdates(self, flag):
        self._updatesBlocked=flag


class TickLineset(CustomGLLinePlotItem):
    def __init__(self, *args, **kwargs):
        mode = "lines"    # Keep mode lines for optimized painting for grouped line items 
        kwargs["mode"]=mode
        self._canPaint=True
        self._lineItems: List[GLLinePlotItem]=[]
        self._linkedLineItems: List[GLLinePlotItem]=[]
        self._zOffset=0
        
        self._contantArray: np.ndarray=None
        self._linkeLineset: TickLineset=None
        self._lineItemsContantMap: Dict[GLLinePlotItem, int] = {}
        self._linkedLinesetsConstantMap: Dict[TickLineset, Dict[GLLinePlotItem, Tuple[int, int]]] = {}
        
        super().__init__(*args, **kwargs)

    def stackLineset(self, newPositionAll, lineItems: List[GLLinePlotItem]):
        for item in lineItems:
            if item.transform().isIdentity():
                newPos = item.pos
            else:
                tr = np.array(item.transform().data()).reshape(4, 4).T  
                points_h = np.hstack([item.pos, np.ones((item.pos.shape[0], 1))])
                transformed_h = points_h @ tr.T
                newPos = transformed_h[:, :3]
            
            if newPositionAll is None:
                newPositionAll=newPos
            else:
                newPositionAll = np.vstack((newPositionAll, newPos))
        return newPositionAll
    
    def lineItems(self):
        return self._lineItems
    
    def addLineItem(self, item: GLLinePlotItem):        
        self._lineItems.append(item)
        
    def linkLineset(self, lineset):
        self._linkedLineItems = lineset
        
        
    def paint(self):
        print("paint")
        if not self._canPaint:
            return

        combined_pos = None
        
        # Process direct line items with z-offset
        for item in self._lineItems:
            pos = self._getWorldPositions(item)
            if pos is not None:
                pos[:, 2] += self._zOffset  # Apply z-offset
                combined_pos = pos if combined_pos is None else np.vstack((combined_pos, pos))
        
        for lineset in self._linkedLineItems:
            for item in lineset.lineItems():
                pos = self._getWorldPositions(item)
            
                #pos = item.pos
                if pos is not None:
                    pos[:, 2] -= self._zOffset
                    combined_pos = pos if combined_pos is None else np.vstack((combined_pos, pos))
        print(np.shape(combined_pos))

        if combined_pos is not None:
            self.blockUpdates(True)
            self.setData(pos=combined_pos)
            self.blockUpdates(False)
            
        super().paint()

    def _getWorldPositions(self, item):
      #  self.itemTr
        """Convert item's positions to this lineset's coordinate system"""
        if not hasattr(item, 'pos') or item.pos is None:
            return None
        
        tr = item.transform()
        pos = item.pos.copy()  # Create a copy to avoid modifying original
        
        if not tr.isIdentity():
            points_h = np.hstack([pos, np.ones((pos.shape[0], 1))])
            tr_matrix = np.array(tr.data()).reshape(4, 4).T
            transformed_h = points_h @ tr_matrix.T
            pos = transformed_h[:, :3]
        
        return pos



class Custom(QtWidgets.QGraphicsObject):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)   

class Window(QtWidgets.QMainWindow):
    def __init__(self, *args, app=None, **kwargs):
        super().__init__(*args, **kwargs)   
        self.gl_widget = opengl.GLViewWidget()
        
        self.setCentralWidget(self.gl_widget)
        
        
        self.group1 = GLGraphicsItem()
        self.group1.translate(0, 1, 1)
        self.group2 = GLGraphicsItem()
        self.group2.translate(1, 0, -1)

        
        self.lineset1 = TickLineset(mode="lines", color="cyan")
        self.lineset1._zOffset=0.1
        self.lineset2 = TickLineset(mode="lines", color="blue")
        
        
     
        
        
        self.group4 = TickLineset()
        lines = []

        num_lines = 5
        start, end = 0, 1
        length = end - start
        positions = np.linspace(start, end + 2, num_lines)
        

    #    self.lineset1.translate(-0.5, 0.5, 0)
    #    self.lineset2.translate(-0.5, -.5, 0)


        for x in [start, end][:1]:
            for z in positions:
                pos = np.array([[x, start, z], [x, end, z]])
                line1 = opengl.GLLinePlotItem(pos=pos)

                
                line1.translate(0, 1, 0)
                
                self.lineset1.addLineItem(line1)
                
                
                
                line1.setParentItem(self.lineset1)
                
                
                line2 = opengl.GLLinePlotItem(pos=pos, color="blue")


                
                line2.translate(0.6, 0, 0)

                
                self.lineset2.addLineItem(line2)

                
                
                
                line2.setParentItem(self.lineset2)

        self.lineset1.setParentItem(self.group1)
        self.lineset2.setParentItem(self.group2)


        self.lineset1.linkLineset([self.lineset2])
        
        
        def _null():return
        
        self.group2.paint=_null
        
        pos = np.array(pos)
        
        

        self.gl_widget.addItem(self.group1)

        
        for i in range(1, 11):
            txt = opengl.GLTextItem(pos = (i/10, 0, 0), text=str(i))
            self.gl_widget.addItem(txt)
            txt = opengl.GLTextItem(pos = (0, i/10, 0), text=str(i))
            self.gl_widget.addItem(txt)
            txt = opengl.GLTextItem(pos = ( 0, 0, i/10), text=str(i))
            self.gl_widget.addItem(txt)
        
        
        
        self.showMaximized()
        self.update()
                
        
        
    def update_timer(self):


        #self.group.rotate(90., 0., 0., 1.)
        grid_pos = self.gridline.pos
        grid_pos[:, 1] = grid_pos[:, 1] + 0.2
        ticks_pos = self.ticks.pos
        ticks_pos[:, 1] = ticks_pos[:, 1]  + 0.2

        self.gridline.setData(pos=grid_pos)
        self.ticks.setData(pos=ticks_pos)
        
        
        
        
        self.lineset2.update()
        
        


def main():
    
    app = QtWidgets.QApplication(sys.argv)
    win = Window()
    #timer = QtCore.QTimer()
    #timer.timeout.connect(win.update_timer)
    #timer.start(300)


    sys.exit(app.exec())

if __name__ == "__main__":
    main()