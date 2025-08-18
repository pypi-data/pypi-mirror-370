from PySide6.QtCore import QTimer, QThread, Signal, QObject
import threading
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout
import sys


class ModbusComWorker(QObject):
    finished = Signal()
    count=0
    def __init__(self, parent=None):
        self._thread = QThread()
        super().__init__(parent)
        self.moveToThread(self._thread)


        
        self._thread.started.connect(self.start)
        self._thread.start()



    def start(self):
        print(f"creating thread: {QThread.currentThread()}")
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.process)
        self._timer.start(2000)

    def stop(self):
        self._timer.stop()
        self.finished.emit()

    def process(self):
        print(QThread.currentThread())
        self.count+=1
        if self.count==3:
            
            sys.exit()

class Widget(QWidget):
    def __init__(self):
        super().__init__()
        self._workers=[]
        self.button = QPushButton("Start Worker")
        self.button.clicked.connect(self.spawn_worker)
        layout = QVBoxLayout()
        layout.addWidget(self.button)
        self.setLayout(layout)
        self._threads = []
        self.worker_count = 0
        self.show()
        
    def spawn_worker(self):
        self.worker = ModbusComWorker()

if __name__ == "__main__":

    app = QApplication()
    if app is None:
        app = QApplication(sys.argv)

    
    w = Widget()

    print(F"starting: {QThread.currentThread()}")

    sys.exit(app.exec())