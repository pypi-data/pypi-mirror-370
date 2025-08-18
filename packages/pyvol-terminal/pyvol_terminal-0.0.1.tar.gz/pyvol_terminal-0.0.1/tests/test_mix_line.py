from __future__ import annotations 
from typing import TYPE_CHECKING

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


class CustomObject(GLLinePlotItem):
    def __init__(self, new_items=[], **kwargs):
        self.items=[]
        self.recursive=False
        super().__init__(**kwargs)
        for i in new_items:
            self.addItem(i)

        

    def addItem(self, item):
        self.items.append(item) 
     #   item.setParentItem(self)
        
    def paint(self):
      #  if self.pos is None:
          # return
        self.setupGLState()

        lines = []
      #  color = []
        print(len(self.items))
        colors = []
        for line in self.items:
            
            new_pos =  line.mapToParent(line.pos.T).T
            print("\n")
            line.parent
            pprint(line.transform())
            parent = line.parentItem()
            if parent is not None:
                if not parent.transform().isIdentity():
                    new_pos = parent.transform().map(line.pos.T).T
                    #line.applyTransform(parent.transform(), local=True)

            

            lines.append(new_pos)
      #      colors.append(line.color.tolist())
            colors = colors  + line.color.tolist()

        if len(lines) > 0:  
            self.pos = np.ascontiguousarray(np.vstack(lines))
            self.setData(pos=self.pos)
            
        #    self.color = np.ascontiguousarray(colors)

        super().paint()
        
    def setData(self, **kwds):
        """
        Update the data displayed by this item. All arguments are optional; 
        for example it is allowed to update vertex positions while leaving 
        colors unchanged, etc.
        
        ====================  ==================================================
        **Arguments:**
        ------------------------------------------------------------------------
        pos                   (N,3) array of floats specifying point locations.
        color                 (N,4) array of floats (0.0-1.0) or
                              tuple of floats specifying
                              a single color for the entire item.
        width                 float specifying line width
        antialias             enables smooth line drawing
        mode                  'lines': Each pair of vertexes draws a single line
                                       segment.
                              'line_strip': All vertexes are drawn as a
                                            continuous set of line segments.
        ====================  ==================================================
        """
        args = ['pos', 'color', 'width', 'mode', 'antialias']
        for k in kwds.keys():
            if k not in args:
                raise Exception('Invalid keyword argument: %s (allowed arguments are %s)' % (k, str(args)))
        if 'pos' in kwds:
            pos = kwds.pop('pos')
            self.pos = np.ascontiguousarray(pos, dtype=np.float32)
        if 'color' in kwds:
            color = kwds.pop('color')
            if isinstance(color, np.ndarray):
                color = np.ascontiguousarray(color, dtype=np.float32)
            self.color = color
        for k, v in kwds.items():
            setattr(self, k, v)

        if self.mode not in ['line_strip', 'lines']:
            raise ValueError("Unknown line mode '%s'. (must be 'lines' or 'line_strip')" % self.mode)

        self.vbos_uploaded = False

    def upload_vbo(self, vbo, arr):
        if arr is None:
            vbo.destroy()
            return
        if not vbo.isCreated():
            vbo.create()
        vbo.bind()
        vbo.allocate(arr, arr.nbytes)
        vbo.release()

class Window(QtWidgets.QMainWindow):
    def __init__(self, *args, app=None, **kwargs):
        super().__init__(*args, **kwargs)   
        
        worldRange=[[0., 2.],
                    [0., 2.],
                    [0., 2.]
                    ]

        y_offsets = np.linspace(0, 1, 4)  # 4 horizontal lines

        lines = []
        for y in y_offsets:
            lines.append([0, y, 0])   # start point
            lines.append([0.5, y, 0])   # end point
            

        lines = np.array(lines)  # shape: (8, 3)

        
        
        lines1, lines2 = lines.copy(), lines.copy()
        

        self.gl_widget = opengl.GLViewWidget()
        
        lines1[0, :] = lines1[0, :] 
        
        lines2[:, 0] = lines2[:,0]/5 - 0.5

        N = lines.shape[0]
        self.line1 = GLLinePlotItem(pos = lines1,
                                    color=np.tile([1.0, 0.0, 0.0, 1.0], (N, 1),),
                                    mode="lines"
                                    )

        self.line2 = GLLinePlotItem(pos = lines2,
                                    color=np.tile([1., 0.0, 1., 1.0], (N, 1),),
                                    mode="lines"
                                    )
        
        self.group = CustomObject(mode="lines", )

        
        self.group.addItem(self.line1)
        self.group.addItem(self.line2)
        
        
        self.line2.setParentItem(self.line1)
        
        
        self.gl_widget.addItem(self.group)
        
        
        
       

        pos = np.array([0, 0, 0])
        colors=["white", "yellow", "cyan"]
        for k in range(3):
            
            pos = np.zeros(3)
            pos[k] = 1 

            
            for i in range(21):
                if i % 2 == 0:
                    gl_item = opengl.GLTextItem(pos=pos * i / 10, text=f"{i/10}", color=colors[k])
                    self.gl_widget.addItem(gl_item), #ignoreBounds=True)
                pos = np.zeros(3)
                pos[k] = 1 
                
        self.setCentralWidget(self.gl_widget)
        self.showMaximized()
        
        
        
        #self.line1.translate(0,dy=1, dz=0, local=False)
        self.line1.update()
        
        self.update()
        
    def update_timer(self):
        self.line1.translate(0,dy=0.5, dz=0, local=False)
        self.update()

        

def main():
    
    app = QtWidgets.QApplication(sys.argv)
    win = Window()
    timer = QtCore.QTimer()
    timer.timeout.connect(win.update_timer)
    timer.start(300)


    sys.exit(app.exec())

if __name__ == "__main__":
    main()