import numpy as np
import pyqtgraph.opengl as gl
from PySide6 import QtWidgets, QtGui, QtCore
import time
import sys



def get_item_data(item):
    if isinstance(item, gl.GLScatterPlotItem):
        return item.pos
    elif isinstance(item, gl.GLMeshItem):
        return item.opts['meshdata'].vertexes()
    elif isinstance(item, gl.GLLinePlotItem):
        return item.pos
    elif isinstance(item, gl.GLBarGraphItem):
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

class AxisItem(gl.GLGraphicsItem.GLGraphicsItem):
    def __init__(self, size=None, color=(255, 255, 255, 76.5), antialias=True, glOptions='translucent', parentItem=None):
        super().__init__()

        self.lineplot = None    
        self.tickValues=None
        self.tickSize=1
        
        if size is None:
            size = QtGui.QVector3D(20,20,1)
        self.setSize(size=size)
        self.setSpacing(1, 1, 1)
        self.setTickColor(color)

        self.lineplot = gl.GLLinePlotItem(
            parentItem=self, glOptions=glOptions, mode='lines', antialias=antialias
        )
        self.setParentItem(parentItem)
        self.updateLines()

    def setSize(self, x=None, y=None, z=None, size=None):
        """
        Set the size of the axes (in its local coordinate system; this does not affect the transform)
        Arguments can be x,y,z or size=QVector3D().
        """
        if size is not None:
            x = size.x()
            y = size.y()
            z = size.z()
        self.__size = [x,y,z]
        self.updateLines()
        
    def size(self):
        return self.__size[:]

    def setSpacing(self, x=None, y=None, z=None, spacing=None):
        if spacing is not None:
            x = spacing.x()
            y = spacing.y()
            z = spacing.z()
        self.__spacing = [x,y,z]
        self.updateLines()
        
    def spacing(self):
        return self.__spacing[:]
        
    def setTickColor(self, color):
        self.__tickColor = color
        self.updateLines()

    def tickColor(self):
        return self.__tickColor

    def updateLines(self):
        if self.lineplot is None:
            return

        tickPos = np.array([])
        for i in range(1, 10, 10):
            text_item = gl.GLTextItem(pos = (i, 0 , 0), text=f"{i}", color="white")
            tickPos = np.vstack((tickPos, np.array([i, 0 , 0])))
            tickPos = np.vstack((tickPos, np.array([i, self.tickSize , 0])))
            
        self.lineplot.setData(pos=tickPos, color=self.tickColor())
        self.update()
        

    
class ViewBox(gl.GLGraphicsItem.GLGraphicsItem):
    def __init__(self, *args, **kwargs):
        self.padding = 0.3
        self.min_vals, self.max_vals = None, None
        self.vb_min, self.vb_max = None, None
        self.transform_matrix=None
        super().__init__(*args, **kwargs)
        
    def normalize_scene(self):
        min_vals, max_vals = compute_scene_bbox(self.childItems())
        if self.min_vals is None or any(min_vals < self.vb_min) or any(max_vals > self.vb_max):
            self.min_vals = min_vals
            self.max_vals = max_vals
            
            diff = max_vals - min_vals
            

            self.vb_min = min_vals - diff * self.padding
            self.vb_max = max_vals + diff* self.padding
            
            ranges = self.vb_max - self.vb_min
            ranges[ranges == 0] = 1.0
            
            self.transform_matrix = QtGui.QMatrix4x4()
        
            self.transform_matrix.scale(1/ranges[0], 1/ranges[1], 1/ranges[2])
            self.transform_matrix.translate(-self.vb_min[0], -self.vb_min[1], -self.vb_min[2])
            for child in self.childItems():
                child.setTransform(self.transform_matrix)

        
class Window(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        self.central_layout = QtWidgets.QVBoxLayout()
        central.setLayout(self.central_layout)
        self.gl_view = gl.GLViewWidget()
        self.parent_item = ViewBox()
        self.gl_view.addItem(self.parent_item)
    
    def create_axis(self):
        self.axis_item = AxisItem()
        
        
        
        
    def create_surface(self):
        X = np.arange(-5, 5, 0.5)
        Y = np.arange(-5, 5, 0.5)
        X_mat, Y_mat = np.meshgrid(X, Y)
        
        R_shifted = np.sqrt((X_mat)**2 + (Y_mat)**2)
        Z_mat = 40 + np.sin(R_shifted)                
        X_vec, Y_vec, Z_vect = X_mat.flatten(), Y_mat.flatten(), Z_mat.flatten()
        
        pos_scatter = np.column_stack((X_vec, Y_vec, Z_vect))
        pos_surface = [X, Y, Z_mat]

        
        scatter = gl.GLScatterPlotItem(pos=pos_scatter, color=(1, 0, 0, 1))
        surface = gl.GLSurfacePlotItem(*pos_surface,
                                    glOptions='opaque',
                                    color=(0.5, 0.5, 1, 1))
        scatter.setParentItem(self.parent_item)
        surface.setParentItem(self.parent_item)
        self.scatter=scatter
        self.surface=surface
        self.parent_item.normalize_scene()
        
        self.gl_view.show()
        

        ax = gl.GLAxisItem()
        ax.setSize(1,1,1)
        self.gl_view.addItem(ax)

        
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(500)
        
    def update(self):
        i,j=np.unravel_index(np.argmax(self.surface._z), self.surface._z.shape)
        z_new= self.surface._z.copy()
        z_new[i,j] = z_new[i,j]+0.5
        self.surface.setData(z=z_new)
        
        pos = self.scatter.pos.copy()
        idx = np.argmax(pos[:,0])
        pos[idx,0] = pos[idx,0]+0.1
        self.scatter.setData(pos=pos)
        self.parent_item.normalize_scene()

  #  view.addItem(scatter)
  #  view.addItem(surface)

    
    
def main():
    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()