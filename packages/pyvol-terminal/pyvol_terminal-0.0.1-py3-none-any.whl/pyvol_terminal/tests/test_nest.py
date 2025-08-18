import sys
import numpy as np
from PySide6 import QtWidgets, QtCore, QtGui
import pyqtgraph.opengl as gl
from OpenGL import GL

class ContainerItem(gl.GLGraphicsItem.GLGraphicsItem):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        


class GLItemGroup(gl.GLGraphicsItem.GLGraphicsItem, QtWidgets.QGraphicsObject):
    def __init__(self):
        super().__init__(self)
        self._GLGraphicsItem__parent = None 
        self._GLGraphicsItem__children = list() 
        self._GLGraphicsItem__view = None 
        
    def setParentItem(self, item):
        if self._GLGraphicsItem__parent is not None:
            self._GLGraphicsItem__parent._GLGraphicsItem__children.remove(self)
        if item is not None:
            item._GLGraphicsItem__children.append(self)

        if self._GLGraphicsItem__view is not None:
            self._GLGraphicsItem__view.removeItem(self)

        self._GLGraphicsItem__parent = item
        self._GLGraphicsItem__view = None
        
    def childItems(self):
        return list(self._GLGraphicsItem__children)

    def boundingRect(self):
        return QtCore.QRectF()
        
    def paint(self, *args):
        pass
    
    def addItem(self, item):
        item.setParentItem(self)
    

def create_spot(point, color):
    return gl.GLScatterPlotItem(
            pos=point,
            color=color, # Yellow
            size=0.2,
            pxMode=False
        )
def create_constant(point, color):
    return Constant(
            pos=point,
            color=color, # Yellow
            size=0.2,
            pxMode=False
        )

class Constant(gl.GLScatterPlotItem):
    def __init__(self,*args,**kwargs):
        super().__init__(*args, **kwargs)
        
    def paint(self):
        print("\npaint")
        parent = self.parentItem()
        
        if parent is not None:
            # 1. Get parent's full transform matrix
            parent_transform = parent.transform()
            print("parent_transform")
            print(parent_transform)
            viewTransform = parent.viewTransform()
            
            print("viewTransform")
            print(viewTransform)
            arr = np.array(viewTransform.data()).reshape(4, 4)
            print("arr")
            print(arr)
            inv_transform = np.linalg.inv(arr)
            
            print("inv_transform")
            print(inv_transform)
            identity = np.eye(4, dtype=np.float32)
            
            print(identity)
            print(np.array(viewTransform.data()).reshape(4, 4).shape, inv_transform.shape, identity.shape)
            corrected_transform = np.array(viewTransform.data()).reshape(4, 4) @ inv_transform @ identity
            
            print("corrected_transform")
            print(corrected_transform)
            flatten = corrected_transform.flatten().tolist()
            self.setTransform(flatten)
        
        # 6. Render with modified transform
        super().paint()
        
        # 7. Restore original transform if modified
        if parent is not None:
            print("setTransform")
            self.setTransform(np.eye(4))
            print("setTransform2")
            
            

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Nested GLScatterPlotItem Example")
        self.setGeometry(100, 100, 800, 600)

        # Create a central widget and a layout
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        layout = QtWidgets.QVBoxLayout(central_widget)
        

        # Create a GLViewWidget
        self.gl_view = gl.GLViewWidget()
        self.gl_view.setCameraPosition(distance=40)
        self.showMaximized()
        layout.addWidget(self.gl_view)

        #self.parent_container = ContainerItem()
        self.parent_container = GLItemGroup()

        pos = np.random.random(size=(500, 3))
        
        pos *= [10, 10, 10]
        pos[0] = (0, 0, 0)
        
        pos = 0.5*np.array([[1, 1, 1]])

        self.scatter_plot_item1 = create_spot(pos, (1, 1, 0, 1))
        self.scatter_plot_item1.setParentItem(self.parent_container)
        pos = np.array([[1, 1, 1]])
        self.parent_container = create_spot(pos, (1, 0, 0, 1))
        
        
        self.scatter_plot_item1.setParentItem(self.parent_container)

        
        self.gl_view.addItem(self.parent_container)

        
        grid = gl.GLGridItem()
        grid.scale(2, 2, 1)
        self.gl_view.addItem(grid)
        
        pos = np.array([[1,1,1]])
        print(f"parent_container: {self.parent_container.visible()}")
        print(f"scatter_plot_item1: {self.scatter_plot_item1.visible()}")
        
        self.parent_container.setVisible(False)
        
        
        print(f"parent_container: {self.parent_container.visible()}")
        print(f"scatter_plot_item1: {self.scatter_plot_item1.visible()}")

        self.scatter_plot_item1.setVisible(True)
        print(f"parent_container: {self.parent_container.visible()}")
        print(f"scatter_plot_item1: {self.scatter_plot_item1.visible()}")
        import sys 
        sys.exit()

        
        for i in range(1, 11):
            x = gl.GLTextItem(pos = (i/10, 0, 0), text=f"{round(i/10, 1)}", color="white")
            y = gl.GLTextItem(pos = (0, i/10, 0), text=f"{round(i/10, 1)}", color="yellow")
            z = gl.GLTextItem(pos = (i/10, 0, i/10), text=f"{round(i/10, 1)}", color="cyan")
            self.gl_view.addItem(x)
            self.gl_view.addItem(y)
            self.gl_view.addItem(z)
            
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_plots)
        self.counter=1

    def update_plots(self):
        self.counter+=0.15
        tr = self.parent_container.transform()
        tr.scale(self.counter, self.counter, self.counter)
        
        print("\n")
        print(f"parent_container: {tr}")
        for child in self.parent_container.childItems():
            
            print(f"child tr: {child.transform()}")

        self.gl_view.update()

            


def main():
    """Main function to run the application."""
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.timer.start(1000)
    sys.exit(app.exec())

if __name__ == "__main__":
    main()