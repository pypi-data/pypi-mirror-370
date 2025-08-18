
from PySide6 import QtWidgets, QtCore
from pyqtgraph import opengl
import numpy as np
from pyvol_terminal.gl_3D_graphing.graphics_items.AbstractGLGraphicsItem import AbstractGLGraphicsItem
from pyvol_terminal.gl_3D_graphing.graphics_items.GLScatterPlotItem import GLScatterPlotItem
from pyvol_terminal.gl_3D_graphing.graphics_items.GL3DViewBox import GL3DViewBox



def create_objects():
    X = np.arange(-5, 5, 0.5)
    Y = np.arange(-5, 5, 0.5)
    X_mat, Y_mat = np.meshgrid(X, Y)

    m1, m2 = 2, 3 
    
    Z_mat = np.sin(X_mat) * np.cos(Y_mat)
    X_vec, Y_vec, Z_vect = X_mat.flatten(), Y_mat.flatten(), Z_mat.flatten()
    
    pos_scatter1 = np.column_stack((X_vec,  Y_vec, m1 * Z_vect))
    pos_scatter2 =np.column_stack((X_vec, Y_vec, m2 * Z_vect))
    
    cls = GLScatterPlotItem
    #cls = opengl.GLScatterPlotItem

    
    scatter1 = cls(pos=pos_scatter1,
                    glOptions='opaque',
                    color=(1, 0, 0, 1))

    scatter2 = cls(pos=pos_scatter2,
                    glOptions='opaque',
                    color=(1, 1, 0, 1))
    
    return scatter1, scatter2

class GLViewBox222(AbstractGLGraphicsItem, QtWidgets.QGraphicsItem):
    def __init__(self, parent=None):
        self._GLGraphicsItem__parent = None 
        self._GLGraphicsItem__children = list() 
        self._GLGraphicsItem__view = None 

        #QtWidgets.QGraphicsItem.__init__(self, None)
        super().__init__(parentItem=parent)
        
    

    def itemsChanged(self):
        print(f"\nitems have changed!!\n")


class CustomGLViewWidget(opengl.GLViewWidget):
    sigPrepareForPaint = QtCore.Signal()
    
    
    def __init__(
        self,
        parent = None,
        viewBox: GL3DViewBox | None = None,
        axisItems = None,
       # **kwargs
        ):  
        super().__init__(parent=parent)
        if viewBox is None:
            print(f"before create")
            viewBox = GL3DViewBox()
        self.vb = viewBox
        self.sigPrepareForPaint.connect(viewBox.prepareForPaint)
        super().addItem(self.vb)
        
    def addItem(self, item, ignoreBounds=False):
        if not item in self.items:
            super().addItem(item)
            if not ignoreBounds and not self.vb is None:
                self.vb.addItem(item)


class CustomGraphicsItem(AbstractGLGraphicsItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)      

    def _internal_update(self):...



class Window(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)      
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        layout = QtWidgets.QVBoxLayout(central_widget)
        self.item_object = CustomGraphicsItem()
        self.item_group = GLItemGroup(parentItem=self.item_object)
        
        #self.view_box = GLViewBox()
        #self.gl_view = CustomGLViewWidget(viewBox=self.view_box)
        self.gl_view = opengl.GLViewWidget()
        self.gl_view.setCameraPosition(distance=40)
        self.showMaximized()
        layout.addWidget(self.gl_view)
        self.gl_view.opts["distance"]=15

        return 
        
        
        
                

        
        
        
        #self.childgroup = GLItemGroup(self.view_box)   # Does not correctly normalise

        self.childitem1, self.childitem2  = create_objects()

      

        #self.childgroup.itemsChangedListeners.append(self.view_box)
        print("\nbefore add1\n")
        #self.childgroup.addItem(self.childitem1)
        print("\nbefore add2")
        #self.childgroup.addItem(self.childitem2)

        #self.gl_view.addItem(self.view_box)
        self.gl_view.addItem(self.childitem1)
        self.gl_view.addItem(self.childitem2)

        
        #self.childgroup.compute_normaliser()
        #tr = Transform3D()
       #tr.scale(0.5, 0.5, 0.5)
        #self.childgroup.setTransform(tr)
        print(self.childitem1.pos)


        for i in range(1, 11):
            x = opengl.GLTextItem(pos = (i/10, 0, 0), text=f"{round(i/10, 1)}", color="white")
            y = opengl.GLTextItem(pos = (0, i/10, 0), text=f"{round(i/10, 1)}", color="yellow")
            z = opengl.GLTextItem(pos = (i/10, 0, i/10), text=f"{round(i/10, 1)}", color="cyan")
            self.gl_view.addItem(x)
            self.gl_view.addItem(y)
            self.gl_view.addItem(z)

        

        
def main():
    
    app = QtWidgets.QApplication()
    win = Window()
    
    app.exec()


if __name__ == "__main__":
    main()
