import sys
from PySide6 import QtCore, QtWidgets, QtGui
import pyqtgraph as pg
from pyqtgraph import opengl


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

class GraphicsObject(QtWidgets.QGraphicsObject):
    def __init__(self, parent=None):
        super().__init__(parent)


class ItemGroup(GraphicsObject):

    def __init__(self, parent=None):
        super().__init__(parent)

    def addItem(self, item):
        if item and item.parentItem() != self:
            item.setParentItem(self)
        self.normaliseToparent()


    def paint(self, painter, option, widget=None):
        pass

    def boundingRect(self):
        return self.childrenBoundingRect()
    
    def normaliseToparent(self):
        rect = self.boundingRect()
        
        tr = self.transform()
        tr.scale(1/rect.width(), 1/rect.height())
        tr.translate(-rect.x(), -rect.y())
        self.update()



class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ItemGroup with QOpenGLWidget Example")

        self.scene = QtWidgets.QGraphicsScene()
        
        self.view = QtWidgets.QGraphicsView(self.scene)
        self.view.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        
        self.openGLWidget = pg.Qt.QtWidgets.QOpenGLWidget()
        self.view.setViewport(self.openGLWidget)
        self.group = ItemGroup()
        
        tr = CustomTransform()
        self.group.setTransform(tr)
        
        self.scene.addItem(self.group)
        
        self.rect1 = QtWidgets.QGraphicsRectItem(0, 0, 50, 50)
        self.rect1.setBrush(QtGui.QColor("crimson"))
        self.group.addItem(self.rect1)

        self.rect2 = QtWidgets.QGraphicsRectItem(1200, 1200, 50, 50)
        self.rect2.setBrush(QtGui.QColor("steelblue"))
        self.group.addItem(self.rect2)
        
        self.group.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.group.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        

        self.setCentralWidget(self.view)
        self.resize(400, 300)
        self.showMaximized()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        rect = self.scene.itemsBoundingRect()
        print(rect)
        self.update()
        rect = self.scene.itemsBoundingRect()
        
        print(rect)

        
       # self.timer.start(1500)
        
    def update(self):
        self.rect1.setRect(2 * 1200, 2*1200, 50, 50)
        

        
        

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
