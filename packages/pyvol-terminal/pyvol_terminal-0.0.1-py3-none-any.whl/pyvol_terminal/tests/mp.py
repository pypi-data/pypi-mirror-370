from PySide6.QtCore import QObject, Signal, QTimer
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel
import multiprocessing as mp
import sys
import time
 
def worker_process(queue):
    for i in range(5):
        time.sleep(1)
        queue.put(f"Message {i} from process")

class SignalEmitter(QObject):
    message_received = Signal(str)

class MainWindow(QMainWindow):
    def __init__(self, queue):
        super().__init__()
        self.label = QLabel("Waiting for messages...", self)
        self.setCentralWidget(self.label)
        self.emitter = SignalEmitter()
        self.emitter.message_received.connect(self.label.setText)
        self.queue = queue
        self.timer = QTimer()
        self.timer.timeout.connect(self.poll_queue)
        self.timer.start(100)

    def poll_queue(self):
        while not self.queue.empty():
            self.emitter.message_received.emit(self.queue.get())

def main():
    mp.set_start_method("spawn")
    queue = mp.Queue()
    process = mp.Process(target=worker_process, args=(queue,))
    process.start()
    app = QApplication(sys.argv)
    win = MainWindow(queue)
    win.show()
    app.exec()
    process.join()

if __name__ == "__main__":
    main()
