import sys, json, time, asyncio
from multiprocessing import Process
import numpy as np
import websockets
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
import atexit
from pyqtgraph import opengl as gl
import qasync  # pip install qasync

async def server_handler(ws):
    while True:
        await ws.send(json.dumps({"price": float(np.random.rand()), "ts": time.time()}))
        await asyncio.sleep(0.5)

async def run_server():
    async with websockets.serve(server_handler, "localhost", 8766):
        await asyncio.Future()

def server_process():
    asyncio.run(run_server())

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.label = QLabel("waiting...")
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)

    def update_from_ws(self, data):
        self.label.setText(f"price={data['price']:.4f} ts={data['ts']:.2f}")

async def ws_listener(window):
    async with websockets.connect("ws://localhost:8766") as ws:
        while True:
            msg = await ws.recv()
            window.update_from_ws(json.loads(msg))



class GLScatterDemo(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GLScatter + Orbit + LocalSocket updates")
        self.resize(900, 700)

        layout = QVBoxLayout(self)
        self.status = QLabel("not connected")
        layout.addWidget(self.status)

        self.view = gl.GLViewWidget()
        self.view.opts['distance'] = 20
        layout.addWidget(self.view, 1)

        self.max_points = 1024
        self.points = np.zeros((0, 3), dtype=float)
        self.sizes = np.array([], dtype=float)
        self.colors = np.empty((0,4), dtype=float)

        self.scatter = gl.GLScatterPlotItem(pos=np.array([[0,0,0]]), size=8, color=(1,1,1,1))
        self.view.addItem(self.scatter)

        self._angle = 0.0

        g = gl.GLGridItem()
        g.scale(2,2,1)
        self.view.addItem(g)
        self.view.setCameraPosition(azimuth=0.0, elevation=20, distance=20)
        self.show()


if __name__ == "__main__":
    p = Process(target=server_process, daemon=True)
    p.start()
    atexit.register(lambda: p.terminate())

    app = QApplication(sys.argv)
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)
    scatter = GLScatterDemo()
    win = MainWindow()
    win.show()

    loop.create_task(ws_listener(win))
    with loop:
        loop.run_forever()
