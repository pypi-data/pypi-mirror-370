import sys
from PySide6.QtWidgets import QApplication, QGraphicsItem, QGraphicsRectItem
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView
from PySide6.QtCore import QRectF
from PySide6.QtGui import QBrush, QColor
import pyqtgraph as pg


class MyItem(QGraphicsRectItem):
    def __init__(self, name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setRect(QRectF(-20, -20, 40, 40))
        self.setBrush(QBrush(QColor("skyblue")))
        self.name = name
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemParentChange:
            print(f"{change}: {value}")
        elif change == QGraphicsItem.GraphicsItemChange.ItemParentHasChanged:
            print(f"{change}: {value}")
        return super().itemChange(change, value)
    def update(self, *args, **kwargs):
        print(f"updating...")
        super().update(*args, **kwargs)
    


app = QApplication(sys.argv)
scene = QGraphicsScene()
view = QGraphicsView(scene)

# Create items
parent_item = MyItem("Parent")
child_item = MyItem("Child")

# Add items to scene
scene.addItem(parent_item)
scene.addItem(child_item)

# Position items
parent_item.setPos(0, 0)
child_item.setPos(100, 0)

# Reparent the child after a short delay
def reparent():
    print("\nReparenting...")
    child_item.setParentItem(parent_item)

view.show()

# Delay the reparenting slightly to see the effect after rendering
QApplication.instance().timer = view.startTimer(1000)
import time
def timerEvent(event):
    while True:
        reparent()
        time.sleep(1)

view.timerEvent = timerEvent

sys.exit(app.exec())


class QGraphicsItem:
    class GraphicsItemFlag(Flag):
        ItemIsMovable = 0x01
        ItemIsSelectable = 0x02
        ItemContainsChildrenInShape = 0x20