from __future__ import annotations 
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pyvol_terminal.gl_3D_graphing.graphics_items.GL3DViewBox import GL3DViewBox

from pyqtgraph import opengl
from PySide6 import QtWidgets, QtCore, QtGui
import numpy as np
from OpenGL import GL
import sys
import cProfile
import pstats



class Window(QtWidgets.QMainWindow):
    def __init__(self, *args, app=None, **kwargs):
        super().__init__(*args, **kwargs)   
    
        self.gl_view = opengl.GLViewWidget()
        
        self.setCentralWidget(self.gl_view)
        self.count=0
        self.m=50
        self.world_m = 4
        self.gl_view.opts.update({"azimuth" : -50,
                          "distance" : 10,
                          "center" : QtGui.QVector3D(0, 1, 0)}
                         )
        
        self.gl_view.update()
        self.linedata_even = np.array([[0., 1., 0.,], [1., 1., 0.]] * self.m)
        self.linedata_odd = np.array([[0., 1., 1.,], [1., 1., 1.]] * self.m)
        self.linedata_even[:, 1] = self.linedata_even[:, 1] * np.repeat(np.linspace(0, self.world_m, self.m), 2)
        self.linedata_odd[:, 1] = self.linedata_odd[:, 1] * np.repeat(np.linspace(0, self.world_m, self.m), 2)
        pos = self.linedata_odd
        self.lines1 = opengl.GLLinePlotItem(pos=self.linedata_odd,
                                           color=(255, 255, 255, 150),
                                           glOptions="translucent",
                                           mode="lines"
                                           )
        self.gl_view.addItem(self.lines1)
        line_data2 = pos.copy()
        line_data2[:, 1] += line_data2[0, 1] - line_data2[1, 1]
        line_data2[:, 1] = line_data2[:, 1] + pos[:, 1]
        self.lines2 = opengl.GLLinePlotItem(pos=line_data2,
                                            color=(255, 255, 255, 150),
                                            glOptions="translucent",
                                            mode="lines"
                                            )

        
        self.gl_view.addItem(self.lines2)

        
        self.showMaximized()
        
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_plots)
        


    def update_plots(self):
        self.count+=1
        if self.count % 2 == 0:
            pos = self.linedata_even
        else:
            pos = self.linedata_odd

        self.lines1.setData(pos=pos)
        self.lines1.paint()

        line_data2 = pos.copy()
        line_data2[:, 1] += line_data2[0, 1] - line_data2[1, 1]
        line_data2[:, 1] = line_data2[:, 1] + pos[:, 1]
        self.lines2.setData(pos=line_data2)


if __name__ == "__main__":
    

    profiler = cProfile.Profile()
    profiler.enable()
    
    app = QtWidgets.QApplication(sys.argv)
    win = Window()
    win.timer.start(100)
    app.exec()
    
    profiler.disable()


    with open(f'profit_{win.m}.txt', 'w') as f:
        ps = pstats.Stats(profiler, stream=f)
        ps.sort_stats('tottime')
        ps.print_stats()

