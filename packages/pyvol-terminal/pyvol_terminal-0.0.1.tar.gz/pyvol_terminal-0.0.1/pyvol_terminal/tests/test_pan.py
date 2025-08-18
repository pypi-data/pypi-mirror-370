import sys
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets, QtCore





class AutoPanDemo(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AutoPan ON (left) vs OFF (right)")

        # Layout
        central_widget = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(central_widget)
        self.setCentralWidget(central_widget)

        # Left plot: autoPan ON
        self.plot_auto = pg.PlotWidget(title="autoPan = ON")
        self.plot_auto.plotItem.vb.setAutoPan(x=True)  # This is the key line
        self.curve_auto = self.plot_auto.plot(pen='y')
        layout.addWidget(self.plot_auto)

        # Right plot: autoPan OFF
        self.plot_manual = pg.PlotWidget(title="autoPan = OFF")
        # No autoPan here
        self.curve_manual = self.plot_manual.plot(pen='r')
        layout.addWidget(self.plot_manual)

        # Data
        self.x = []
        self.y = []
        self.counter = 0

        # Timer
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(500)  # every 0.5 sec

    def update_data(self):
        self.counter += 1
        x_val = self.counter
        y_val = np.sin(x_val * 0.2)

        self.x.append(x_val)
        self.y.append(y_val)

        self.curve_auto.setData(self.x, self.y)
        self.curve_manual.setData(self.x, self.y)

        # Manually set range on the right plot to fix the view
        if self.counter == 1:
            self.plot_manual.setXRange(0, 20)  # fixed range; doesn't move
            
        plotitem = self.plot_auto.getPlotItem()
        
        x_range = plotitem.vb.state['limits']['xRange']
        x_lims = plotitem.vb.state['limits']['xLimits']
        print("")
        print(x_range)
        print(x_lims)
        
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = AutoPanDemo()
    window.resize(1000, 400)
    window.show()
    sys.exit(app.exec())
