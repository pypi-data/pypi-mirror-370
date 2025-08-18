from PySide6 import QtCore, QtWidgets
import sys
import time

class Worker(QtCore.QObject):
    finished = QtCore.Signal()
    progress = QtCore.Signal(int)

    def run(self):
        """Long-running task"""
        for i in range(5):
            time.sleep(0.5)
            print(f"i: {i}")
            self.progress.emit(i)

        self.finished.emit()

class SlotClass(QtCore.QThread):
    other_progress = QtCore.Signal(int)
    
    def __init__(self):
        super().__init__()
        self._buffered_values=[]
        
    def progress_slot(self, value):
        self._buffered_values.append(value)
        print(f"\nprogress_slot")
        print(f"value: {value}")
        print(f"self._buffered_values: {self._buffered_values}")
        time.sleep(1)
    
    def run(self):
        self.timer = QtCore.QTimer()
        self.timer.moveToThread(self)
        self.timer.timeout.connect(self.other)
        self.timer.start(1000)
        self.exec()    
        
        
    
    def other(self):
        print(f"other: {self._buffered_values}")
        for value in self._buffered_values.copy():
            self.other_progress.emit(value)
        self._buffered_values = []
    

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.button = QtWidgets.QPushButton("Start Work")
        self.label = QtWidgets.QLabel("Progress: 0")
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.button)
        layout.addWidget(self.label)

        container = QtWidgets.QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.button.clicked.connect(self.start_worker)

    def start_worker(self):
        self.thread = QtCore.QThread()
        self.worker = Worker()
        self.worker.moveToThread(self.thread)
        
      #  self.slot_thread = QtCore.QThread()
        self.slot_class = SlotClass()
       # self.slot_class.moveToThread(self.slot_thread)
       # self.slot_thread.start()
        

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        
        self.worker.progress.connect(self.slot_class.progress_slot)
        self.slot_class.other_progress.connect(self.update_progress)
        self.slot_class.start()

        self.thread.start()
        
        
        
    def update_progress(self, value):
        self.label.setText(f"Progress: {value}")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
