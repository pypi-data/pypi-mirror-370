from PySide6 import QtCore, QtWidgets
import sys

class InnerWorker(QtCore.QObject):
    aslot = QtCore.Signal()
    def __init__(self, name):
        super().__init__()
        self.name = name
        self._thread = QtCore.QThread()  # Each worker has its own thread
        self.aslot.connect(triggered)
    
    def run(self):
        print(f"[{self.name}] running in", QtCore.QThread.currentThread())
        self.aslot.emit()
        
        
def triggered():
    print(f"triggered: {QtCore.QThread.currentThread()}")
    import sys
    sys.exit()

class Manager(QtCore.QObject):
    def __init__(self):
        super().__init__()
        self.worker1 = InnerWorker("Worker 1")
        self.worker2 = InnerWorker("Worker 2")

    def start_inner_threads(self):
        self.worker1.moveToThread(self.worker1._thread)
        self.worker1._thread.started.connect(self.worker1.run)
        self.worker1._thread.start()

        # Start Worker 2 in its own thread  
        self.worker2.moveToThread(self.worker2._thread)
        self.worker2._thread.started.connect(self.worker2.run)
        self.worker2._thread.start()

        print("[Manager] started workers from", QtCore.QThread.currentThread())

class Bootstrap(QtCore.QObject):
    def __init__(self):
        super().__init__()
        self._thread = QtCore.QThread()
        self.manager = Manager()
        self.manager.moveToThread(self._thread)
        self._thread.started.connect(self.manager.start_inner_threads)
        self._thread.start()

app = QtWidgets.QApplication(sys.argv)
b = Bootstrap()
sys.exit(app.exec())