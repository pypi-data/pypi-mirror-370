from __future__ import annotations
from typing import List, Optional, Tuple, Union, Dict, TYPE_CHECKING
if TYPE_CHECKING:
    from quantities.engines import TickEngine
    from pyvol_terminal.interfaces.volatility_surface.pyvol_GL3DViewWidget import SurfaceViewWidget
    
from PySide6 import QtGui, QtCore, QtWidgets
import pyqtgraph.opengl as gl
import numpy as np
from pyqtgraph.opengl import GLTextItem
from OpenGL import GL as opengl
from OpenGL import GLU
from PySide6 import QtGui
import math
import pyqtgraph as pg
from PySide6.QtGui import QColor, QPixmap, QPainter, QBrush
import warnings

import warnings
warnings.filterwarnings(
    "ignore",
    message=r"invalid value encountered in cast",
    category=RuntimeWarning  # or UserWarning if that’s what you see
)
    
class CustomColorMap(pg.ColorMap):
    def __init__(self, colourmap_style: str):
        pos = np.linspace(0, 1, 500)          
        try:
            colourmap = pg.colormap.get(colourmap_style)
        except:
            print(f"{colourmap_style} is not in pyqtgraph, using default inferno")
            colourmap = pg.colormap.get("inferno")

        colors = colourmap.map(pos, mode='byte')        
        super().__init__(pos=pos, color=colors, mode='byte')


class ColorSquare(QtWidgets.QLabel):
    def __init__(self, color, size=50):
        super().__init__()
        self.color = color
        self.color_width = size
        self.color_height = size /2
        self.setFixedSize(self.color_width, self.color_height)
        self.update_color()

    def update_color(self):
        pixmap = QPixmap(self.color_width, self.color_height)
        pixmap.fill(QtCore.Qt.transparent)
        painter = QPainter(pixmap)
        if isinstance(self.color, tuple):
            r, g, b, a = [int(x * 255) for x in self.color]
            q_color = QColor(r, g, b, a)
            
        elif isinstance(self.color, str):
            
            q_color = QColor(self.color)
        else:
            q_color =None

        if not q_color is None:
            painter.setBrush(QBrush(q_color))
        painter.drawRect(0, 0, self.color_width, self.color_height)
        painter.end()
        self.setPixmap(pixmap)
        self.setStyleSheet("border: 2px solid black;")


class Legend(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background: transparent; color: white;")
        self.layout = QtWidgets.QVBoxLayout(self)
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.legend_items={}
        self.legend_count={}
        
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                           QtWidgets.QSizePolicy.Expanding
                           )

    def remove_legend_item(self, name):
        self.legend_count[name]-=1
        if self.legend_count[name]==0:
            inner_widget=self.legend_items[name]
            self.layout.removeWidget(inner_widget)
                    
    def add_legend_item(self, name, colour):
        if not name in self.legend_count:
            self.legend_count[name]=1
        else:
            self.legend_count[name]+=1   
        if self.legend_count[name] > 1:
            return
        
        hbox_layout = QtWidgets.QHBoxLayout()
        hbox_layout.setAlignment(QtCore.Qt.AlignLeft)
        hbox_layout.setContentsMargins(0, 0, 0, 0)
        hbox_layout.setSpacing(5)
        
        square_colour = ColorSquare(colour)
        hbox_layout.addWidget(square_colour)

        square_label = QtWidgets.QLabel(name)
        square_label.setStyleSheet("border: 1px solid white; padding: 3px; background-color: white; color: black")
        hbox_layout.addWidget(square_label)

        inner_widget = QtWidgets.QWidget()
        inner_widget.setLayout(hbox_layout)

        self.legend_items[name] = inner_widget        
        self.layout.addWidget(inner_widget)
        self.adjustSize()
        self.update()