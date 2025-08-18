from __future__ import annotations 
from typing import List, Optional, Tuple, Union, Dict, TYPE_CHECKING, Callable, Any
if TYPE_CHECKING:
    from instruments.instruments import Option, ABCInstrument, Derivative
    from instruments.utils import InstrumentManager
    from ..data_classes.classes import Slice
    
import pyqtgraph as pg
import numpy as np
from PySide6 import QtCore, QtWidgets, QtGui
from ..metric_attributes import get_metric_category
from .option_monitor import extra_widgets, stylesheets as utils_omon
from pprint import pprint


class CustomTextItem(pg.TextItem):
    def __init__(self, text=None, view_box_anchor=None, **kwargs):
        self.view_box_anchor=view_box_anchor
        if self.view_box_anchor[0] == 0:
            self.use_vb_xmin=True
        else:
            self.use_vb_xmin=False
        if self.view_box_anchor[1] == 0:
            self.use_vb_ymin=False
        else:
            self.use_vb_ymin=True

        super().__init__(text=text, **kwargs)
        self.p=[self.pos()[0], self.pos()[1]]
    
    def attach_viewbox(self, vb: pg.ViewBox):
        self.vb=vb 
        self.vb.sigResized.connect(self.view_box_resize)
        self.vb.sigRangeChanged.connect(self.view_box_resize)
        self.vb.sigRangeChangedManually.connect(self.view_box_resize)


    def right_click(self, *args):
        if not self.isVisible():
            super().show()
    
    def view_box_resize(self, args):
        if not self.view_box_anchor is None:
            vb_range = self.vb.viewRange()
            if self.use_vb_xmin:
                self.p[0] = vb_range[0][0]
            else:
                self.p[0] = vb_range[0][1]
            if self.use_vb_ymin:
                self.p[1] = vb_range[1][0]
            else:
                self.p[1] = vb_range[1][1]
            super().setPos(*self.p)

class CustomPlotDataItem(pg.PlotDataItem):
    def __init__(self, px_type, *args, **kwargs):
        self.px_type=px_type  
        super().__init__(*args, **kwargs)
    
    def update_from_dataclass(self, dclass: Slice):
        self.setData(**dclass.plot_item_kwargs())
    

class OptionInfoTable(QtWidgets.QWidget):
    def __init__(self, name_metric_map, getattr_map, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.getattr_map=getattr_map
        self.price_types=name_metric_map["price_types"]    
        self.cellitem_container={}
        self._on_view=True
        self._initLayout()
        self._initTables(name_metric_map, getattr_map)
        
    def _initLayout(self):
        self.setLayout(QtWidgets.QVBoxLayout())

    """
    def _initTables(self, name_metric_map, getattr_map):
        self.name_table = NameTable(name_metric_map["object"].ticker,
                                    name_metric_map["object"].underlying_px)
        
        self.metric_table = MetricTable(name_metric_map, getattr_map)
        self.layout().addWidget(self.name_table)
        self.layout().addWidget(self.metric_table)
        
        self.autoFillBackground()
        self.pop_table=False
        self.metric_table.verticalHeader().sectionResized.connect(self.update_vertical_dims)
        self.name_table.horizontalHeader().sectionResized.connect(self.update_horizontal_dims)
        self.showEvent = self.on_show_event
    """
    def update_horizontal_dims(self, *args):
        self.name_table.horizontalHeader().setFixedWidth(self.metric_table.horizontalHeader().width())
        
    def update_vertical_dims(self, *args):
        self.metric_table.verticalHeader().setFixedWidth(self.metric_table.verticalHeader().width())
        

    def on_show_event(self, event):
        self.name_table.verticalHeader().resizeSections(QtWidgets.QHeaderView.ResizeMode.ResizeToContents) 
        self.update_vertical_dims(0, 0, 0) 
        super().showEvent(event)


