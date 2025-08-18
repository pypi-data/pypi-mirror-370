import sys
from PySide6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsSimpleTextItem
from PySide6.QtGui import QPainter, QColor, QFont
from PySide6.QtCore import Qt

class CustomView(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        
        # Shared painter settings
        self.font = QFont("Arial", 20)
        self.color = QColor("red")

        # Create two text items
        self.text1 = QGraphicsSimpleTextItem("Text 1")
        self.text2 = QGraphicsSimpleTextItem("Text 2")

        # Position them
        self.text1.setPos(50, 50)
        self.text2.setPos(50, 100)

        # Add to scene
        self.scene.addItem(self.text1)
        self.scene.addItem(self.text2)

    def paintEvent(self, event):
        # Override paintEvent to force the same painter settings
        painter = QPainter(self.viewport())
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Apply shared settings
        painter.setFont(self.font)
        painter.setPen(self.color)

        # Let the scene handle the rest (items will inherit painter state)
        self.scene.render(painter)
        painter.end()

def main():
    app = QApplication(sys.argv)
    view = CustomView()
    view.setWindowTitle("Double Paint with Same QPainter")
    view.resize(300, 200)
    view.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()