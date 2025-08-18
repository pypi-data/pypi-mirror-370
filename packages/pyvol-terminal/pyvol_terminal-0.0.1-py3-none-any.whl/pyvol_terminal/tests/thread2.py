from PySide6 import QtCore, QtWidgets
import sys
import time

class Worker(QtCore.QObject):
    
    def __init__(self, name):
        super().__init__()
        self.name = name
       # self._thread = QtCore.QThread()
      #  self._
      #  self._thread.started.connect(self.start_thread)
        
    def start_thread(self):
        self.moveToThread(self._thread)
        self._thread.started.connect(self.work)
        self._thread.start()
    
    def work2(self):
        while True:
            print(f"Thead {self.name} working in thread {QtCore.QThread.currentThread()}...")
            time.sleep(1)
    
    def work(self):
        print(f"Thead {self.name} working in thread {QtCore.QThread.currentThread()}...")
        
    def start(self):
        print("starting worker")
        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self.work)
        self._timer.start(2000)
        
        
class Widget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self._workers=[]
        self.button = QtWidgets.QPushButton("Start Worker")
        self.button.clicked.connect(self.spawn_worker)
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.button)
        self.setLayout(layout)
        self._threads = []
        self.worker_count = 0
        
    def spawn_worker(self):
        self.worker_count += 1
        worker = Worker(f"Worker {self.worker_count}")
        thread = QtCore.QThread()
        self._threads.append(thread)
        
        worker.moveToThread(thread)
        
        thread.started.connect(worker.start)
        thread.start()
        
        #self._workers.append(worker)
        #worker.start_thread()

def main():
    app = QtWidgets.QApplication(sys.argv)
    widget = Widget()
    widget.show()
    sys.exit(app.exec())
    
if __name__ == "__main__":
    main()
