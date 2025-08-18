from __future__ import annotations 
from typing import List, Optional, Tuple, Union, Dict, TYPE_CHECKING, Callable
if TYPE_CHECKING:
    from instruments.instruments import Option
    from instruments.utils import InstrumentManager
    from axis.axis_utils import TickEngineManager, TickEngine
    
import pyqtgraph as pg
from PySide6 import QtWidgets
from typing import List
import numpy as np
from PySide6 import QtCore, QtGui, QtWidgets
from ... import misc_widgets
from .. import subplots
from pyvol_terminal.axis import widgets as axis_widgets
from typing import Dict
from pyvol_terminal.data_classes import builders as builders_data_classes
from pyvol_terminal.axis import axis_utils as utils_axis


class CustomPlotitem(subplots.SubPlot):
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
        

class MainView(QtWidgets.QSplitter):
    def __init__(self,
                 instrument_manager: InstrumentManager,
                 interpolation_config,
                 tick_engine_manager: TickEngine,
                 slice_direction: str,
                 update_timer=0,
                 **kwargs 
                ):
        super().__init__(QtCore.Qt.Horizontal)
        self.displayed_domains=[]
        self.container_scatter=[]
        self.container_line=[]
        self.data_container=[]
        base_domain, domain = builders_data_classes.create_domains(instrument_manager.options_instrument_container.original_data)
    
        self.metric_axis_engine=utils_axis.MetricAxisEngine(base_domain.strike,
                                                            base_domain.expiry,
                                                            "Strike",
                                                            "Expiry",
                                                            "Implied Volatility")
        self.data_container = builders_data_classes.create_surface_dataclasses(instrument_manager.config["options"]["price_types"], 
                                                                               instrument_manager.options_instrument_container.original_data,
                                                                               domain,
                                                                               self.metric_axis_engine,
                                                                               instrument_manager.options_instrument_container.get_objects(),
                                                                               interpolation_config)
        tick_engine = getattr(tick_engine_manager, f"{slice_direction}_engine")
        self.x_axis_item = axis_widgets.CustomAxisItem(axis_direction="x",
                                                       tick_engine=tick_engine,
                                                       orientation="bottom") 
        self.y_axis_item = axis_widgets.CustomAxisItem(axis_direction="x",
                                                       tick_engine=tick_engine_manager.z_engine,
                                                       orientation="right") 
        
        axisItems = {"right" : self.y_axis_item, "bottom" : self.x_axis_item}
        self.plot.setAxisItems(axisItems)
        self.plot = CustomPlotitem(axisItems=axisItems)
        self.plot.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Expanding)
                
        self.legend = misc_widgets.Legend()
        self.plot.addLegend(offset=(0, 0))   
        self.init_layout(tick_engine_manager.x_engine)


    def init_layout(self, tick_engine):
        self.setLayout(QtWidgets.QGridLayout(self))
        
        self.layout().addWidget(self.plot, 0, 0)
        self.layout().addWidget(self.legend, 0, 0, alignment=QtCore.Qt.AlignTop | QtCore.Qt.AlignRight)
        
    
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
        self.addPlots(line)
        self.addPlots(scatter)
        line.show()



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
        
