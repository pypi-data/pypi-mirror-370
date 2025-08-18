from __future__ import annotations
from typing import List, Optional, Tuple, Union, Dict, TYPE_CHECKING
    
import pyqtgraph as pg
from pyqtgraph import opengl 
import numpy as np
from typing import List, Optional
from PySide6 import QtCore, QtGui
from pyqtgraph import functions as fn
from pyqtgraph.opengl.GLGraphicsItem import GLGraphicsItem
from pyqtgraph import opengl
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6 import QtWidgets
from typing import List, Optional, Tuple, Union, Dict, TYPE_CHECKING
import sys
from PySide6 import QtGui, QtCore
import pyqtgraph.opengl as gl
import numpy as np
from pyqtgraph.opengl import GLTextItem
from OpenGL import GL as opengl
from OpenGL import GLU
from PySide6 import QtGui
from pprint import pprint
import copy
import math
from pyvol_terminal.interfaces.volatility_surface import view_box


class WorldSizedText(GLTextItem):
    world_width_character = 0.014286

    def __init__(self, *args, **kwargs):
        self.pos_arr = np.array(kwargs["pos"])
        self._reference_size=None
        self._right_anchor_pos=np.array(kwargs["pos"])
        super().__init__(*args, **kwargs)

        
    def setParent(self, parent: CustomView):
        super().setParent(parent)
        self.updatePixelSize(parent)
        
    @QtCore.Slot()
    def updatePixelSize(self, view_widget: CustomView):
        print(f"\n{self.text}")
        self.blockSignals(True)
        self.maintain_text_world_width()
        self.shiftToWidget(view_widget)
        self.blockSignals(False)
    
    def shiftToWidget(self, widget: CustomView):
        text_width_world = self.worldWidth()
        camera_pos = widget.cameraPositionNumpy()
        current_angle = math.degrees(math.atan2(*(-1*camera_pos[:2])))
        
        x, y = self.offset_xy(text_width_world, current_angle, 0)
        pos = self._right_anchor_pos.copy()
        pos[0] = pos[0] + x
        pos[1] = pos[1] + y
        self.setData(pos = pos)

    def offset_xy(self, txt_width, theta, elevation):
        x = -txt_width * math.cos(math.radians(theta))
        y = txt_width * math.sin(math.radians(theta))
        return x, y

    def maintain_text_world_width(self):
        current_world_width = self.worldWidth()
        if current_world_width <= 0:
            return
        
        scale_factor = len(self.text) * self.world_width_character / current_world_width
        
        current_font = self.font
        current_point_size = current_font.pointSizeF()
        new_size = current_point_size * scale_factor
        current_font.setPointSizeF(new_size)
        self.setData(font=current_font)

    def setData(self, *args, **kwargs):
        super().setData(*args, **kwargs)
        if "pos" in kwargs:
            self.pos_arr[:] = kwargs["pos"]
    
    def pxHeight(self):
        metrics = QtGui.QFontMetricsF(self.font)
        return metrics.boundingRect(self.text).height()
    
    def pxWidth(self):
        metrics = QtGui.QFontMetricsF(self.font)
        return metrics.boundingRect(self.text).width()
    
    def pointWidth(self):
        return self.pxWidth() * 72 / self.view().screen().logicalDotsPerInch()

    def worldWidth(self):
        return self.pxWidth() * self.view().pixelSize(self.pos_arr)

    def worldWidthPoint(self):
        return self.pxWidth() * 72 / self.view().screen().logicalDotsPerInch()#* self.view().pointSize(self.pos_arr)
    
    
class CustomView(gl.GLViewWidget):
    viewChangedSignal = QtCore.Signal(object)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.opts["azimuth"] = 0 
        self.opts["center"] = QtGui.QVector3D(0, 0, 0)
        self.opts["distance"] = 3
        self.opts["elevation"] = 0
        self.update()
        self._update_timer = QtCore.QTimer()
        self._update_timer.setSingleShot(True)
        self._update_timer.setInterval(50) 
        self._update_timer.timeout.connect(self._emit_view_changed)
        self._pending_view_change = False
        

    def cameraPositionNumpy(self):
        p = self.cameraPosition()
        return np.array((p.x(), p.y(), p.z()))
        
    def wheelEvent(self, ev):
        distance_prev = self.opts["distance"]
        super().wheelEvent(ev)  
        if self.opts["distance"] != distance_prev:
            self.update()
            self.viewChangedSignal.emit(self)
            
    def pointSize(self, pos):
        PIXELS_PER_POINT = self.screen().logicalDotsPerInch() / 72.0
        return PIXELS_PER_POINT * self.pixelSize(pos)

    def _emit_view_changed(self):
        self.viewChangedSignal.emit(self)
        self._pending_view_change = False

    def orbit(self, azim, elev):
        super().orbit(azim, elev)
        if not self._pending_view_change:
            self._pending_view_change = True
            self._update_timer.start()
            
            
class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle('Volatility Surface')
        self.widget_central = QtWidgets.QWidget()
        self.setCentralWidget(self.widget_central)
        self.layout_main = QtWidgets.QVBoxLayout()
        self.widget_central.setLayout(self.layout_main)
        self.showMaximized()

        self.view_widget = CustomView()
        self.vw_layout = QtWidgets.QVBoxLayout()
        self.layout_main.addLayout(self.vw_layout)
        
        self.layout_main.addWidget(self.view_widget)
        
        self.showMaximized()
        QtCore.QTimer.singleShot(100, self.init_axes_after_show)
        
    def init_axes_after_show(self):

        grid = gl.GLGridItem()
        grid.setSize(1, 1, 1)
        
        self.view_widget.addItem(grid)
        grid.translate(0.5, 0.5, 0)
        font=QtGui.QFont('Neue Haas Grotesk')#, pointSize=12)
        font.setPointSizeF(12)
        print(font.pointSizeF())
        positions = [[100000, "abc"], [120000, 132000]]
        for i in np.linspace(0, 1, 4):
            for j in np.linspace(0, 1, 4):
                if i % 1 == 0 or j % 1 == 0:
                    if i != 1:
                        continue
                    pos = (i, j, 0)
                    text = str(positions[int(i)][int(j)])#f"{(float(i),float(j))}"
                    text = f"{(round(float(i),2), round(float(j),2))}"
                    font=QtGui.QFont('Neue Haas Grotesk')#, pointSize=12)
                    font.setPointSizeF(12)

                    text_item = WorldSizedText(pos=pos, text=text, font=font)
                    self.view_widget.addItem(text_item)
                    self.view_widget.viewChangedSignal.connect(text_item.updatePixelSize)
                    text_item.setParent(self.view_widget)
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    sys.exit(app.exec())
    
