from __future__ import annotations 
from typing import List, Optional, Tuple, Union, Dict, TYPE_CHECKING, Callable
if TYPE_CHECKING:
    from instruments.instruments import Option
    from instruments.utils import InstrumentManager
    from ...quantities.engines import TickEngineManager
    from ...data_classes.classes import VolatilityData, Slice
    from ...workers import SurfaceCalibration

import pyqtgraph as pg
from PySide6 import QtWidgets
from typing import List
import numpy as np
from PySide6 import QtCore, QtGui, QtWidgets
from ... import misc_widgets
from .. import subplot, custom_widgets
from ..volatility_surface.axis_widgets import CustomAxisItem
from typing import Dict
from pyvol_terminal.data_classes import builders as builders_data_classes
from ..abstract_classes import ABCMainViewQSplitter
from . import settings



class CustomPlotitem(subplot.SubPlot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.plot_items={}
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.getViewBox().disableAutoRange(0)
        self.getViewBox().disableAutoRange(1)
        
        self._plot_items: List[pg.PlotDataItem] = []
        self.x_buffer = 0.1
        self.y_buffer = 0.1

    def add_legend(self, legend):
        self.legend = legend
    
    def addPlots(self, px_type, value, line, scatter):
        self.plot_items[px_type]["line"].update({value : line})
        self.plot_items[px_type]["scatter"].update({value : scatter})
        super().addItem(line)
        super().addItem(scatter)
        line.sigPlotChanged.emit(self.calculate_limits)
            
    def removeItem(self, item):
        if isinstance(item, pg.PlotDataItem) and item in self._plot_items:
            try:
                item.sigPlotChanged.disconnect(self.calculate_limits)
            except (RuntimeError, TypeError):
                pass 
            self._plot_items.remove(item)
        result = super().removeItem(item)
        self.calculate_limits()
    
    def _set_limits(self, x_min, x_max, y_min, y_max):
        if x_min == x_max:
            x_offset = 0.5 
        else:
            x_offset = (x_max - x_min) * self.x_buffer        
        if y_min == y_max:
            y_offset = 0.5
        else:
            y_offset = (y_max - y_min) * self.y_buffer
        self.getViewBox().setXRange(x_min - x_offset, x_max + x_offset)
        self.getViewBox().setYRange(y_min - y_offset, y_max + y_offset)    
        self.update()
        
    def calculate_limits(self):
        x_data = []
        y_data = []

        for plot_item in self._plot_items:
            x_min, x_max, y_min, y_max = plot_item.get_limits()
            x_data.append(x_min)
            x_data.append(x_max)
            y_data.append(y_min)
            y_data.append(y_max)
        if any(~np.isnan(x_data)):
            self.x_min, self.x_max = np.nanmin(x_data), np.nanmax(x_data)
        else:
            self.x_min, self.x_max = np.nan, np.nan
        if any(~np.isnan(y_data)):
            self.y_min, self.y_max = np.nanmin(y_data), np.nanmax(y_data)
        else:
            self.y_min, self.y_max = np.nan, np.nan
        
        if (not np.isnan(self.x_min)
            and not np.isnan(self.x_max)
            and not np.isnan(self.y_min)
            and not np.isnan(self.y_max)):
            if len(self._plot_items) == 1:
                self._set_limits(x_min, x_max, y_min, y_max)
            else:
                x_range, y_range = self.getPlotItem().getViewBox().viewRange()
                if (x_min < x_range[0] or x_max > x_range[1] or y_min < y_range[0] or y_max > y_range[1]):
                    self._set_limits(x_min, x_max, y_min, y_max)
        

class MainView(ABCMainViewQSplitter):
    def __init__(self,
                 instrument_manager: InstrumentManager,
                 interpolation_config,
                 tick_engine_manager: TickEngineManager,
                 slice_direction: str,
                 slice_type: str,
                 **kwargs 
                ):
        super().__init__(QtCore.Qt.Horizontal)
        self.volatility_data_container: Dict[str, VolatilityData] = kwargs.get("volatility_data_container", None)
        self.displayed_domains=[]
        self.container_scatter=[]
        self.container_scatter = {}
        self.container_line = {}
        self.displayed_domains=[]
        self.displayed_slices=[]
        self.diplayed_ptypes=[]
        self.slice_direction=slice_direction
        self.slice_type=slice_type
        self.tick_engine_manager=tick_engine_manager
        

        
        
        tick_engine_x = getattr(self.tick_engine_manager, f"{slice_direction}_engine")
        self.x_axis_item = CustomAxisItem(axis_direction="x",
                                        tick_engine=tick_engine_x,
                                        orientation="bottom",
                                        ) 
        self.y_axis_item = CustomAxisItem(axis_direction="x",
                                        tick_engine=self.tick_engine_manager.z_engine,
                                        orientation="right"
                                        )
                                                    
        
        axisItems = {"right" : self.y_axis_item, "bottom" : self.x_axis_item}
        
        self.plot = pg.PlotItem(axisItems=axisItems)
        self.plot.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Expanding)
                
        self.plot.addLegend()
        self.init_layout(tick_engine_x)


    def init_layout(self, tick_engine):
        
        container_widget = QtWidgets.QWidget()
        container_layout = QtWidgets.QGridLayout(container_widget)
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        toggle_widget = settings.ScrollableToggleButtons(self, getattr(self.domain, f"{self.slice_direction}_vect"), tick_engine)
        scroll.setWidget(toggle_widget)
        
        
        
        
        plot_widget = pg.PlotWidget(plotItem=self.plot)
        plot_widget.setLayout(container_layout)
        
        
        
     #   main_view_layout.addWidget(plot_widget, 0, 0)
        
        
     #   main_view_layout.addWidget(self.legend, 0, 0, alignment=QtCore.Qt.AlignTop | QtCore.Qt.AlignRight)
        
        self.addWidget(scroll)
       # self.addWidget(blank_surface_widget)
        self.addWidget(plot_widget)
        self.setStretchFactor(0, 5) 
        self.setStretchFactor(1, 1) 
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
    
    def addPlots(self, px_type):
        for value in self.displayed_domains:
            self.create_plot_objects(px_type, value)
    
    def addPlot(self, px_type, value):
        self.create_plot_objects(px_type, value)
    
    def create_plot_objects(self, px_type, value):
        self.data_container.add_slice(px_type, value)
        slice = self.data_container.slice_container[px_type][value]
        scatter = CustomPlotDataItem(x=slice.x, y=slice.y)
        line = CustomPlotDataItem(x=slice.xi, y=slice.yi)
        self.container_scatter[px_type][value] = scatter
        self.container_line[px_type][value] = line
    #    self.plot_view.addPlots(line)
        self.plot.addPlots(px_type, value, line, scatter)
        line.show()

    
    def _internal_update_view(self, calibrated_surface_container: Dict[str, SurfaceCalibration]):
        self.update_dataclasses(calibrated_surface_container)
        
    
    def update_dataclasses(self, calibrated_surface_container: Dict[str, SurfaceCalibration]):
        for px_type in self.diplayed_ptypes:
            surface_engine = calibrated_surface_container[px_type]
            volatility_data = self.volatility_data_container[px_type]
            dataclass = volatility_data.get_dataclass(self.slice_type)
            for slice_value in self.displayed_slices:
                pass



class CustomPlotWidget(pg.PlotWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.getPlotItem().getViewBox().disableAutoRange(0)
        self.getPlotItem().getViewBox().disableAutoRange(1)
        self._plot_items: List[pg.PlotDataItem] = []
        self.x_buffer = 0.1
        self.y_buffer = 0.1

    def add_curve(self, item):
        self.getPlotItem().addItem(item)
        self._plot_items.append(item)
        self.calculate_limits()  
        item.sigPlotChanged.emit(self.calculate_limits)
            
    def removeItem(self, item):
        if isinstance(item, pg.PlotDataItem) and item in self._plot_items:
            try:
                item.sigPlotChanged.disconnect(self.calculate_limits)
            except (RuntimeError, TypeError):
                pass 
            self._plot_items.remove(item)
        result = super().removeItem(item)
        self.calculate_limits()
    
    def _set_limits(self, x_min, x_max, y_min, y_max):
        if x_min == x_max:
            x_offset = 0.5 
        else:
            x_offset = (x_max - x_min) * self.x_buffer        
        if y_min == y_max:
            y_offset = 0.5
        else:
            y_offset = (y_max - y_min) * self.y_buffer
        self.getPlotItem().getViewBox().setXRange(x_min - x_offset, x_max + x_offset)
        self.getPlotItem().getViewBox().setYRange(y_min - y_offset, y_max + y_offset)    
        self.update()
        
    def calculate_limits(self):
        x_data = []
        y_data = []

        for plot_item in self._plot_items:
            x_min, x_max, y_min, y_max = plot_item.get_limits()
            x_data.append(x_min)
            x_data.append(x_max)
            y_data.append(y_min)
            y_data.append(y_max)
        if any(~np.isnan(x_data)):
            self.x_min, self.x_max = np.nanmin(x_data), np.nanmax(x_data)
        else:
            self.x_min, self.x_max = np.nan, np.nan
        if any(~np.isnan(y_data)):
            self.y_min, self.y_max = np.nanmin(y_data), np.nanmax(y_data)
        else:
            self.y_min, self.y_max = np.nan, np.nan
        
        if (not np.isnan(self.x_min)
            and not np.isnan(self.x_max)
            and not np.isnan(self.y_min)
            and not np.isnan(self.y_max)):
            if len(self._plot_items) == 1:
                self._set_limits(x_min, x_max, y_min, y_max)
            else:
                x_range, y_range = self.getPlotItem().getViewBox().viewRange()
                if (x_min < x_range[0] or x_max > x_range[1] or y_min < y_range[0] or y_max > y_range[1]):
                    self._set_limits(x_min, x_max, y_min, y_max)
        
class CustomScatterPlotItem(pg.ScatterPlotItem):
    pen_map: Dict[str, pg.mkPen]
    def __init__(self, px_type, *args, **kwargs):
        kwargs["symbol"] = "x"
        kwargs["size"]=10
        kwargs["pxMode"]=True
        self.px_type = px_type
        super().__init__(*args, **kwargs)



class CustomPlotDataItem(pg.PlotDataItem):
    pen_map: Dict[str, pg.mkPen]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._calculate_limits(*self.getData())
    
    def _calculate_limits(self, x, y):
        if any(~np.isnan(x)):
            self.x_min, self.x_max = np.min(x), np.max(x)
        else:
            self.x_min, self.x_max = np.nan, np.nan
        if any(~np.isnan(y)):
            self.y_min, self.y_max = np.min(y), np.max(y)
        else:
            self.y_min, self.y_max = np.nan, np.nan
    
    def get_limits(self):
        return self.x_min, self.x_max, self.y_min, self.y_max
    
    def get_xlim(self):
        return self.x_min, self.x_max
    
    def get_ylim(self):
        return self.y_min, self.y_max

    def setData(self, **kwargs):
        self._calculate_limits(kwargs["x"], kwargs["y"])
        super().setData(**kwargs)
        
       