
import numpy as np
from PySide6 import QtWidgets, QtCore, QtGui
import pyqtgraph as pg
from pyvol_terminal.gl_3D_graphing.graphics_items.GL3DGraphicsItems import GL3DSurfacePlotItem, GL3DScatterPlotItem
from pyvol_terminal.gl_3D_graphing.graphics_items.GL3DViewBox import GL3DViewBox
from pyvol_terminal.gl_3D_graphing.widgets.GL3DViewWidget import GL3DViewWidget
from pyvol_terminal.gl_3D_graphing.graphics_items.GL3DAxisItem import GL3DViewBox

import sys

def create_pos():
    X = np.arange(-5, 5, 0.5)
    Y = np.arange(-3, 3, 0.5)
    X_mat, Y_mat = np.meshgrid(X, Y, indexing="xy")
    R = np.sqrt(X_mat**2 + Y_mat**2)

    m1 = 2
    
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

def create_objects(X_mat, Y_mat, Z_mat, m1):

    
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
  #  colors = viridis_like.map(z_norm.flatten(), mode='byte')[:, :3]  # shape: (N, 3)\

    #colors = colors.reshape(Z_mat.shape + (3,))  # shape: (rows, cols, 3)

    
    surface = GL3DSurfacePlotItem(x=pos_surface[0],
                                    y=pos_surface[1],
                                    z=pos_surface[2],
                                    glOptions='opaque',
                                    shader="shaded",
                                    colors=colors
                                    )
        
    return scatter, surface




class Window(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)      
        self.X_mat, self.Y_mat, self.Z_mat, self.m1 = create_pos()
        self.scatter, self.surface = create_objects(self.X_mat, self.Y_mat, self.Z_mat, self.m1)    
        worldRange=[[0.,1.], [0.,1.],[0.,1.]]
        
        self.viewBox = GL3DViewBox(worldRange=worldRange)
        ax_orth = worldRange[0][1], worldRange[2][0]
        axisItem2 = GL3DViewBox(1,
                               ax_orth,
                               0,
                               )
        axis_items = [axisItem2]

        self.gl_view = GL3DViewWidget(defaultWorldRange=worldRange,
                                    viewBox=self.viewBox,
                                    axisItems=axis_items,
                                    )
        self.gl_view.opts["distance"] = 10

        self.X_mat, self.Y_mat, self.Z_mat, self.m1 = create_pos()
        self.scatter, self.surface = create_objects(self.X_mat, self.Y_mat, self.Z_mat, self.m1)    
       # import sys
      #  sys.exit()
        
        self.scatter=None
       # self.gl_view.addItem(self.scatter)
        self.gl_view.addItem(self.surface)


        self.setCentralWidget(self.gl_view)
        self.showMaximized()
        


        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_plots)

    def update_plots(self):
        self.m1 += 1
        xmin, xmax = self.X_mat.min() - 1, self.X_mat.max() + 1
        ymin, ymax = self.Y_mat.min() - 1, self.Y_mat.max() + 1
        X = np.arange(xmin, xmax, 0.5)
        Y = np.arange(ymin, ymax, 0.5)
        self.X_mat, self.Y_mat = np.meshgrid(X, Y)
        R = np.sqrt(self.X_mat**2 + self.Y_mat**2)

        
        
        self.Z_mat = self.m1 * np.sin(R) 
        
        X_vec, Y_vec, Z_vec = self.X_mat.flatten(), self.Y_mat.flatten(), self.Z_mat.flatten()
        
        pos_scatter = np.column_stack((X_vec, Y_vec, Z_vec))
        pos_surface = self.X_mat[0], self.Y_mat[:,1], self.Z_mat.T
        
        
        
        #AbstractGLPlotItem.AbstractGLPlotItem.setData(self.scatter, pos=new_pos)
        
     #   self.scatter.setData(pos=pos_scatter)
        
        self.surface.setData(x=pos_surface[0],
                             y=pos_surface[1],
                             z=pos_surface[2]
                             )
        """
        self.surface.setData(x=self.surface._x,
                             y=self.surface._y,
                             z=self.surface._z,
                             )
        """

def main():
    
    app = QtWidgets.QApplication(sys.argv)
    win = Window()
    win.timer.start(1000)
    sys.exit(app.exec())
if __name__ == "__main__":
    main()