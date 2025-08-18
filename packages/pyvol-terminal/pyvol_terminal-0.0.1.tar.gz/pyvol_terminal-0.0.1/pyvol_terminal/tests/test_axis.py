from __future__ import annotations 
from typing import List, Optional, Tuple, Union, Dict, TYPE_CHECKING, Callable
if TYPE_CHECKING:
    from pyvol_terminal.gl_3D_graphing.widgets.view_box import ViewBox

from PySide6 import QtWidgets, QtCore
import sys
from pyvol_terminal.gl_3D_graphing.widgets import GL3DViewWidget
from pyqtgraph import opengl
import numpy as np
import uuid 
from pyvol_terminal.gl_3D_graphing.graphics_items import GL3DAxisItem


class Window(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        self.central_layout = QtWidgets.QVBoxLayout()
        central.setLayout(self.central_layout)
        self.gl_view = GL3DViewWidget.GL3DViewWidget(padding=.2)
        X = np.arange(-5, 5, 0.5)
        Y = np.arange(-5, 5, 0.5)
        
      #  X = (X -X.min()) / (X.max() - X.min())
     #   Y = (Y -Y.min()) / (Y.max() - Y.min())
        
        X_mat, Y_mat = np.meshgrid(X, Y)
        
        R_shifted = np.sqrt((X_mat)**2 + (Y_mat)**2)
        Z_mat = 2 + np.sin(R_shifted)                
        X_vec, Y_vec, Z_vect = X_mat.flatten(), Y_mat.flatten(), Z_mat.flatten()
        
        pos_scatter = np.column_stack((X_vec, Y_vec, Z_vect))
        pos_surface = [X, Y, Z_mat]

        
   #     scatter = opengl.GLScatterPlotItem(pos=pos_scatter, color=(1, 0, 0, 1))
        surface = opengl.GLSurfacePlotItem(*pos_surface,
                                    glOptions='opaque',
                                    color=(0.5, 0.5, 1, 1))
       # self.gl_view.addItem(scatter)
        self.gl_view.addItem(surface)
        self.axis_item = GL3DAxisItem.AxisGrid(0,
                                       1,
                                       0.1,
                                       ww=self
                                       )
        self.axis_item.linkToView(self.gl_view.vb)
      #  self.axis_item.linkGLWidget(self)

     #   self.scatter=scatter
        self.surface=surface
        
        #scatter = CustomScatter(pos=pos)
        
        
        self.central_layout.addWidget(self.gl_view)     
    #    z_new = surface._z * 2
     #   surface.setData(z=z_new)
        #self.gl_view.addItem(scatter, ignoreBounds=False) 

        for i in range(1, 11):
            #x = opengl.GLTextItem(pos = (i/10, 0, 0), text=f"{round(i/10, 1)}", color="white")
            y = opengl.GLTextItem(pos = (0, i/10, 0), text=f"{round(i/10, 1)}", color="yellow")
            z = opengl.GLTextItem(pos = (i/10, 0, i/10), text=f"{round(i/10, 1)}", color="cyan")
            #self.gl_view.addItem(x, ignoreBounds=True)
            self.gl_view.addItem(y, )#ignoreBounds=True)
            self.gl_view.addItem(z, )#ignoreBounds=True)
            
        self.showMaximized()
        
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        #self.timer.start(500)
        
    def update(self):
        i,j=np.unravel_index(np.argmax(self.surface._z), self.surface._z.shape)
        z_new= self.surface._z.copy()
        z_new[i,j] = z_new[i,j]+0.5
        self.surface.setData(z=z_new)
        
        pos = self.scatter.pos.copy()
        idx = np.argmax(pos[:,0])
        pos[idx,0] = pos[idx,0]+0.1
        self.scatter.setData(pos=pos)
        #self.gl_view.vb.normalize_scene()
        


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
    

    
