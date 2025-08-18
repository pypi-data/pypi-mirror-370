from PySide6.QtWidgets import QGraphicsTransform
from PySide6.QtGui import QMatrix4x4
from PySide6.QtCore import Property, QObject
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import QTimer, QPropertyAnimation


class CustomTransform(QGraphicsTransform):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._vertical_shear = 0.0 
        self._horizontal_shear = 0.0

    def applyTo(self, matrix):
        shear_matrix = QMatrix4x4()
        shear_matrix.setToIdentity()
        if self._vertical_shear != 0.0:
            shear_matrix.setRow(1, QtGui.QVector4D(self._vertical_shear, 1.0, 0.0, 0.0))
        if self._horizontal_shear != 0.0:
            shear_matrix.setRow(0, QtGui.QVector4D(1.0, self._horizontal_shear, 0.0, 0.0))
        matrix *= shear_matrix

    def getVerticalShear(self):
        return self._vertical_shear
    
    def setVerticalShear(self, shear):
        if self._vertical_shear != shear:
            self._vertical_shear = shear
            self.update()

    def getHorizontalShear(self):
        return self._horizontal_shear

    def setHorizontalShear(self, shear):
        if self._horizontal_shear != shear:
            self._horizontal_shear = shear
            self.update()

    verticalShear = Property(float, getVerticalShear, setVerticalShear)
    horizontalShear = Property(float, getHorizontalShear, setHorizontalShear)


from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsRectItem, QApplication
import sys

app = QApplication(sys.argv)

view = QGraphicsView()
scene = QGraphicsScene()
view.setScene(scene)

rect = QGraphicsRectItem(0, 0, 100, 100)
rect.setBrush(QtGui.Qt.GlobalColor.red)
scene.addItem(rect)

# Create and apply our custom transform
custom_transform = CustomTransform()
rect.setTransformations([custom_transform])  # Can combine with other transforms

animation = QPropertyAnimation(custom_transform, b"verticalShear")
animation.setDuration(2000)
animation.setStartValue(0.0)
animation.setEndValue(2.0)
animation.setLoopCount(-1)  # Infinite loop
animation.start()



view.show()
sys.exit(app.exec())
