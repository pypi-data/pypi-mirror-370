from __future__ import annotations 
from typing import TYPE_CHECKING

from pyvol_terminal.gl_3D_graphing.widgets import GL3DViewWidget
if TYPE_CHECKING:
    from pyvol_terminal.gl_3D_graphing.graphics_items.GL3DViewBox import GL3DViewBox

from pyqtgraph import opengl
from PySide6 import QtWidgets, QtCore
import numpy as np
from OpenGL import GL
from pyqtgraph.Qt import QT_LIB
import importlib
from pyvol_terminal.gl_3D_graphing.graphics_items.GL3DAxisItem import GL3DAxisItem
from pyvol_terminal.gl_3D_graphing.graphics_items import GL3DViewBox, AbstractGLPlotItem, AbstractGLGraphicsItem
from pyqtgraph import opengl
import sys
QtOpenGL = importlib.import_module(f"{QT_LIB}.QtOpenGL")
from pyvol_terminal.gl_3D_graphing.graphics_items.GL3DGraphicsItems import GL3DSurfacePlotItem, GL3DLinePlotDataItem
from matplotlib import colormaps


def scale_value(x, old_min, old_max, new_min, new_max):
    return new_min + (x - old_min) * (new_max - new_min) / (old_max - old_min)

def normalize(x, p1, p2):
    x_min = np.min(x)
    x_max = np.max(x)
    return (x - x_min) / (x_max - x_min) * (p2 - p1) + p1

class CustomMixedGLSurfacePlotItem(GL3DSurfacePlotItem):
    def __init__(self, colormap, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.colormap = colormap
        
    def _setDataChild2(self, x=None, y=None, z=None, colors=None):        
        if not x is None \
            and not y is None \
                and not z is None \
                    and not colors is None:
            if not self.view() is None:
                vb = self.view().vb
                wz_min, wz_max = vb.opts["worldRange"][2]
                z_norm = scale_value(z, z.min(), z.max(), wz_min, wz_max)
                
                colors = self.colormap(z_norm.flatten()).reshape(*z.shape, 4) 
        return super()._setDataChild(x=x, y=y, z=z, colors=colors)
    
    def _setDataChild(self, x=None, y=None, z=None, colors=None):
        if x is not None and y is not None and z is not None:
            if self.view() is not None:
                vb = self.view().vb
                wz_min, wz_max = vb.state["worldRange"][2]
                # Normalize z-values to [0,1] based on worldRange
                if wz_max != wz_min:
                    z_normalized =  (wz_max - wz_min) / (z - wz_min)
                else:
                    z_normalized = np.zeros_like(z)
                z_normalized = normalize(z, wz_min, wz_max)
                colors = self.colormap(z_normalized.flatten()).reshape(*z.shape, 4)
        return super()._setDataChild(x=x, y=y, z=z, colors=colors)
    
def create_pos(nticks) :
    X = np.linspace(-5, 10, nticks)
    Y = np.linspace(-3, 10, nticks)
    X_mat, Y_mat = np.meshgrid(X, Y, indexing="xy")
    R = np.sqrt(X_mat**2 + Y_mat**2)

    m1 = 20
    
    Z_mat = m1 * np.sin(R) 
    return X_mat, Y_mat, Z_mat, m1

from pyvol_terminal.gl_3D_graphing.graphics_items.GL3DPlotDataItemMixin import BaseGL3DPlotDataItemMixin
from abc import abstractmethod

class ABCPyVolPlotItemMixin(BaseGL3DPlotDataItemMixin):
    
    @abstractmethod
    def getValues(self):...
    
    @abstractmethod
    def id(self):...
    

class PyVolLineItem(ABCPyVolPlotItemMixin, GL3DLinePlotDataItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.item_type = None
        self.dataset = None

    def id(self):
        return self._internal_id
    
    def getValues(self):
        return self.pos[:,0], self.pos[:,1], self.pos[:,2]

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
    pos = np.linspace(0, 1, 500)   
    #pre_cmap = pg.colormap.get("inferno")
    

    colormap = colormaps["viridis"]
    
    z_norm = (Z_mat - Z_mat.min()) / (Z_mat.max() - Z_mat.min())
    colors = colormap(z_norm.flatten())
    colors = colors.reshape(*Z_mat.T.shape, 4)


    wz_min, wz_max = 0, 1
    z_norm = scale_value(Z_mat, Z_mat.min(), Z_mat.max(), wz_min, wz_max)
    
    #colors = None  # Let the item handle color mapping dynamically
    
    
    surface = GL3DSurfacePlotItem(
                                           x=pos_surface[0],
                                            y=pos_surface[1],
                                            z=pos_surface[2],
                                            glOptions='opaque',
                                            shader="shaded",
                                            colors=colors
                                            )
    
    surface.setGLOptions("opaque")
    
    line = PyVolLineItem(pos = [[0, 0, 0], [0, 0, 1]])
    line.setGLOptions("opaque")

    return scatter, surface




class DotItem(AbstractGLGraphicsItem.AbstractGLGraphicsItem):
    def __init__(self, *coordinate):
        super().__init__()
        self.coordinate = list(coordinate)
        self.setGLOptions('opaque')
        self.setFlag(self.GLGraphicsItemFlag.ItemIgnoresTransformations)
        
    def initializeGL(self):
        GL.glEnable(GL.GL_POINT_SMOOTH)
        GL.glPointSize(10)
        
    def updateCoordinate(self, coord):
        self.coordinate = coord
        
    def paint(self):
        if not self.view():
            return
            
        self.setupGLState()
        
        # Set up orthographic projection matching view dimensions
        width = self.view().width()
        height = self.view().height()
        
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(0, width, height, 0, -1, 1)
        
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()
        
        GL.glColor3f(1.0, 1.0, 0.0)  # White color
        
        GL.glBegin(GL.GL_POINTS)
        GL.glVertex2f(*self.coordinate)  # Use pixel coordinates directly
        GL.glEnd()

class CustomScatter(opengl.GLScatterPlotItem):
    def __init__(self, *args, **kwargs):
        self.coordinate = (300, 300)
        super().__init__(*args, **kwargs)      
        
    

    def paint(self):
        GL.glColor3f(1.0, 1.0, 1.0)
        
        GL.glBegin(GL.GL_POINTS)
        GL.glVertex2f(*(self.coordinate))  
        GL.glEnd()

"""
        ax_orth = worldRange[1][0], worldRange[2][0]
        ax=0
        ax_perp = 1
        axisWidth = abs(worldRange[ax_perp][0] - worldRange[ax_perp][1])
        tickOrientation = -1

        axisItem1 = GLAxisItem(ax,
                               worldRange[ax],
                               ax_orth,   
                               axisWidth, 
                               tickOrientation,
                               ax_perp,
                               text="x-axis"
                               )
        


"""

class Custom(QtWidgets.QGraphicsItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)      

class Window(QtWidgets.QMainWindow):
    def __init__(self, *args, app=None, **kwargs):
        super().__init__(*args, **kwargs)   
        
        worldRange=[[0., 1.5],
                    [-0.7, 1.],
                    [0.,1.]
                    ]
        
        worldRange=[[0., 1.],
                    [0., 1.],
                    [0., 1.]
                    ]

        
        a1 = [[worldRange, 0, (0, 0, 0), 1],
              {"text" : "x-axis",
               "showValues" : True,
               "valuesColor" : "white",
               "labelColor" : "white",
               "faceTickOffset" : -0.1,
               "syncToView" : True,
               "showGrid" : True,
               "showTickMargin" : True,
            #   "showFaceBorder" : False,
               
               }
              ]
        a2 = [[worldRange, 1, (0, 0, 0), 0],
              {"text" : "y-axis",
               "showValues" : True,
               "valuesColor" : "yellow",
               "labelColor" : "yellow",
               "faceTickOffset" : -0.1,
               "syncToView" : True,
               "showGrid" : True,
          #     "showFaceBorder" : False,
               }
              ]
        
        a3 = [[worldRange, 2, (1, 1, 0), 0],
              {"text" : "z-axis",
               "showValues" : True,
               "showTicks" : True,
               "valuesColor" : "cyan",
               "labelColor" : "cyan",
               "faceTickOffset" : -0.1,
               "graphFaceOffset" : -0.3,
               "syncToView" : True,
               "showGrid" : True,
             #  "showFaceBorder" : False,
               }
              ] 
        a33 = [[worldRange, 2, (1, 0, 0), 0],
              {"text" : "z-axis",
               "showValues" : True,
               "showTicks" : True,
               "valuesColor" : "cyan",
               "labelColor" : "cyan",
               "faceTickOffset" : -0.1,
               "graphFaceOffset" : -0.3,
               "syncToView" : True,
               "showGrid" : True,
             #  "showFaceBorder" : False,
               }
              ] 

        a4 = [[worldRange, 2, (0, 0, 0), 1],
              {"text" : "z-axis",
               "showValues" : True,
               "valuesColor" : "cyan",
               "labelColor" : "cyan",
               "faceTickOffset" : -0.1,
               "graphFaceOffset" : -0.3,
               "syncToView" : True,
            #   "showGrid" : False,
           #    "showFaceBorder" : False,

               }
              ]
        a44 = [[worldRange, 2, (0, 1, 0), 1],
              {"text" : "z-axis",
               "showValues" : True,
               "valuesColor" : "cyan",
               "labelColor" : "cyan",
               "faceTickOffset" : -0.1,
               "graphFaceOffset" : -0.3,
               "syncToView" : True,
            #   "showGrid" : False,
           #    "showFaceBorder" : False,

               }
              ]

        a13 = [[worldRange, 0, (0, 1, 0), 2],
              {"text" : "x-axis",
               "showValues" : False,
               "showLabel" : False,
               "valuesColor" : "cyan",
               "labelColor" : "cyan",
               "faceTickOffset" : -0.1,
               "graphFaceOffset" : -0.3,
               "syncToView" : True,
               "showTickMargin" : True,
               }
              ] 
        
        a23 = [[worldRange, 1, (0, 0, 0), 2],
              {"text" : "x-axis",
               "showValues" : False,
               "showLabel" : False,
               "valuesColor" : "cyan",
               "labelColor" : "cyan",
               #"faceTickOffset" : -0.1,
               "graphFaceOffset" : -0.3,
               "syncToView" : True
               }
              ]

        items = [a1, a4]
        items = [a1, a2, a3]

      #  items = [a1, a13]
      #  a1[1]["showGrid"] = False
      #  a1[1]["showFaceBorder"] = False
      #  a2[1]["showFaceBorder"] = False
        
    #    items = [a1, a2]
        
        axis_items = [GL3DAxisItem.fromViewBoxRange(*item[0], **item[1]) for item in items]

     #   axis_items[0].linkOptimizeAxes(axis_items[1])
        
        worldRange=[[-1., 1.],
                    [-1., 1.],[-1., 1.]
                    ]

        worldRange=[[0., 1.],
                    [0., 1.],
                    [0., 1.]
                    ]

        self.viewBox = GL3DViewBox.GL3DViewBox(worldRange=worldRange)
        
        self.gl_view = GL3DViewWidget.GL3DViewWidget(axisItems=axis_items,
                                                 viewBox=self.viewBox
                                                 )
        
                
        self.phase=0
        self.step=0

        self.gl_view.setCameraPosition(distance=5)
        self.setCentralWidget(self.gl_view)
    #    self.setGeometry(0, 0, 800, 600)
        self.update()
        
        self.nticks=50
        
        self.X_mat, self.Y_mat, self.Z_mat, self.m1 = create_pos(self.nticks)
        self.scatter, self.surface = create_objects(self.X_mat, self.Y_mat, self.Z_mat, self.m1)    
        
        self.scatter=None
       # self.gl_view.addItem(self.scatter)
        self.gl_view.addItem(self.surface)
        self.c=0
        
        self.setGeometry(0, 0, 800, 600)
        self.show()
    
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_plots)
        
        for i in range(21):
            if i % 2 == 0:
                txt = opengl.GLTextItem(pos = (i/ 10, i/10, 0), text=str(i))
                #self.gl_view.addItem(txt, ignoreBounds=True)
        
        
        
     #   self.timer.setSingleShot(True)
        


        
    def update_plots(self):
        self.c+=1
        self.phase += 0.4

        growth = 1 + 0.5 * np.sin(self.phase * 0.3)


        step = 0.5
        range_base = 10 * growth
        xmin, xmax = -range_base, range_base
        ymin, ymax = -range_base, range_base

        X = np.linspace(xmin+step, xmax + step, self.nticks)
        Y = np.linspace(ymin+step, ymax + step, self.nticks)
        self.X_mat, self.Y_mat = np.meshgrid(X, Y)
        

        R = np.sqrt(self.X_mat**2 + self.Y_mat**2)

        amplitude = 10 + 5 * np.sin(self.phase * 0.2)
        self.Z_mat = amplitude * np.sin(R - self.phase) * np.sin(R * 0.5 - self.phase)

        X_vec = self.X_mat.flatten()
        Y_vec = self.Y_mat.flatten()
        Z_vec = self.Z_mat.flatten()
        
        pos_scatter = np.column_stack((X_vec, Y_vec, Z_vec))

        
        x_vals = self.X_mat[0]
        y_vals = self.Y_mat[:, 0]
        z_vals = self.Z_mat
        
        x_vals *= 20
        
        y_vals *= 6
        
        self.surface.setData(x=x_vals,
                             y=y_vals , 
                             z=z_vals,
                             )
        
        print(self.gl_view.vb.viewRange())
        
        

def main():
    
    app = QtWidgets.QApplication(sys.argv)
    win = Window()
    win.timer.start(50)
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
    
    """
    # Profile the entire application run
    profiler = cProfile.Profile()
    profiler.enable()
    
    app = QtWidgets.QApplication(sys.argv)
    win = Window()
    win.timer.start(750)
    app.exec()
    
    profiler.disable()
    
    # Save results to file
    with open('profile_results.txt', 'w') as f:
        ps = pstats.Stats(profiler, stream=f)
        ps.sort_stats('tottime')
        ps.print_stats()
    """