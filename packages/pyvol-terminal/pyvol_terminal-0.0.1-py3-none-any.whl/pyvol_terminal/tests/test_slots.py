import sys
import time
import threading
from PySide6 import QtCore, QtWidgets
import pyqtgraph as pg
from PySide6.QtCore import QThread, QObject, Slot


class ClickablePlot(pg.PlotWidget):
    # Define a custom signal that emits the mouse click position (QPointF)
    mouseClicked = QtCore.Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseEnabled(x=False, y=False)
        self.scene().sigMouseClicked.connect(self._on_mouse_click)

    def _on_mouse_click(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            pos = event.scenePos()
            if self.sceneBoundingRect().contains(pos):
                mousePoint = self.getPlotItem().vb.mapSceneToView(pos)
                self.mouseClicked.emit(mousePoint)


class Worker1(QObject):
    @Slot(object)
    def run(self, pos):
        time.sleep(.5)
        print(f"Handler 1: {pos} | Thread: {threading.current_thread().name}")


class Worker2(QObject):
    @Slot(object)
    def run(self, pos):
        time.sleep(.5)
        print(f"Handler 2: {pos} | Thread: {threading.current_thread().name}")


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Mouse Click Signal Example")
        self.resize(800, 600)

        # Create and set up plot widget
        self.plot = ClickablePlot()
        self.setCentralWidget(self.plot)

        print(f"MainWindow thread: {threading.current_thread().name}")

        self.thread1 = QThread()
        self.worker1 = Worker1()
        self.worker1.moveToThread(self.thread1)
        self.plot.mouseClicked.connect(self.worker1.run)
        self.thread1.start()

        self.thread2 = QThread()
        self.worker2 = Worker2()
        self.worker2.moveToThread(self.thread2)
        self.plot.mouseClicked.connect(self.worker2.run)
        self.thread2.start()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
