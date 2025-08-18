from PySide6.QtCore import QThread, QTimer
import time

# Shared counter (accessed by multiple threads)
counter = 0

class WorkerThread(QThread):
    def run(self):
        global counter
        for _ in range(1000):
            current = counter
            time.sleep(0.001)  # Simulate processing delay
            counter = current + 1

# Create and start multiple threads
threads = []
for _ in range(5):
    thread = WorkerThread()
    thread.start()
    threads.append(thread)

# Wait for all threads to finish
for thread in threads:
    thread.wait()

print("Final counter value (expected 5000):", counter)  # Likely less than 5000 due to race condition!