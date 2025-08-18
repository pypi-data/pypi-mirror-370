from __future__ import annotations 
from typing import List, Optional, Tuple, Union, Dict, TYPE_CHECKING, Callable
if TYPE_CHECKING:
    from instruments.instruments import Option, Spot
    from instruments.utils import InstrumentManager
    from ...workers import SurfaceCalibration
    from ...quantities.engines import TickEngineManager
    from ...data_classes.classes import AbstractDataClass, VolatilityData, VolVector, Surface, Points, Slice
    from ...engines.interpolation_engines import Abstract3DInterpolator
    from ...engines.surface_engines import AbstractSurfaceEngine
    from ..subplot import SubPlot

from PySide6 import QtCore, QtWidgets, QtGui
from . import init_helpers
from .. import custom_widgets, subplot
import pyqtgraph as pg
from . import pyvol_GL3DViewWidget
from pyvol_terminal.misc_classes import PriceText
import time
from ...gl_3D_graphing.graphics_items import GL3DGraphicsItems
from .pyvol_GL3DGraphicsItems import PyVolGL3DSurfacePlotItem, PyVolGL3DScatterPlotItem
from pyvol_terminal.data_classes import builders as builders_data_classes
import traceback
from ..abstract_classes import ABCMainViewQSplitter
from dataclasses import dataclass, field, InitVar
import numpy as np
from pprint import pprint   


QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps)

format = QtGui.QSurfaceFormat()
format.setSwapInterval(1)  
QtGui.QSurfaceFormat.setDefaultFormat(format)


class MainView(ABCMainViewQSplitter):
    def __init__(self,
                 instrument_manager: InstrumentManager,
                 tick_engine_manager: TickEngineManager=None,
                 queue_interaction: bool=False,
                 colour_styles_config: Dict[str, str]={},
                 **kwargs
                 ):
        super().__init__(QtCore.Qt.Horizontal)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        
        self.pyvol_gl_widget: pyvol_GL3DViewWidget.PyVolGL3DViewWidget=None
        self.volatility_data_container: Dict[str, VolatilityData] = kwargs.get("volatility_data_container", None)
        self.queue_interaction=queue_interaction
        
        self.interact_finish_callbacks=[]
        
        self.colour_styles_config=colour_styles_config

        all_price_types = instrument_manager.config["options"]["price_types"]
        
        self._dclass_name_subplot_title_map: Dict[str, str]={"skew" : "Skew",
                                                             "term" : "Term Structure"
                                                             }
        
        self.c=0
        self.nticks=50
        self.phase=0
        self.step=0
        
        self.display_map = DisplayMap(all_price_types)
        
        self._all_assets = ["surface", "scatter"]
        self._displayed_assets = ["surface", "scatter"]
        self._subplot_widget_container: Dict[str, SubPlot]={}
        
        self.displayed_price_types=[]
        self.displayed_price_plot_type_flags = {px_type: {"surface" : False, "scatter" : False} for px_type in all_price_types}
        self.displayed_price_plot_type_names = {px_type: {"surface" : None, "scatter" : None} for px_type in all_price_types}
        
        self.plot_state = {"surface" : True,
                           "scatter" : True,
                           "subplots" : True,
                           }

        self.scatter_from_calibrated=True

        spot_objects = [item for item in instrument_manager.spot_instrument_container.objects.values()]

        self._initViews(tick_engine_manager, spot_objects, self._dclass_name_subplot_title_map.values())
        self._initLayout()
        
    def _initViews(self,
                   tick_engine_manager: TickEngineManager,
                   spot_objects,
                   subplot_names,
                   ):
        spot_text = PriceText(spot_objects)
        
        self.pyvol_gl_widget = pyvol_GL3DViewWidget.PyVolGL3DViewWidget(spot_text, computeNormals=False)
        self.pyvol_gl_widget.processIntenseInteraction = self.processInteractionState
        
        self.addIntenseInteraction("view")
            
        axes_3D_items, axes_2D_items = init_helpers.initAxis(self.pyvol_gl_widget,
                                                             tick_engine_manager=tick_engine_manager)
        self.pyvol_gl_widget.setAxisItems(axes_3D_items)
        _all_axis="xy"
        for i, (title, axis) in enumerate(zip(subplot_names, _all_axis)):
            tick_engine = tick_engine_manager.get_engine(_all_axis[-i-1])
            axisItems={"bottom" : axes_2D_items[i],
                       "left"   : axes_2D_items[i+2]
                       }
            subplot_widget = subplot.SubPlot(title=title,
                                             axis_3D_dir=axis,
                                             other_axis_tick_engine=tick_engine,
                                             axisItems=axisItems
                                             )
            self.pyvol_gl_widget.rcMapCoordsSig.connect(subplot_widget.update3DMouseClick)
            self._subplot_widget_container[title]=subplot_widget
    
    def _initLayout(self):
        container_widget = QtWidgets.QWidget()
        surface_layout = QtWidgets.QGridLayout(container_widget)
        self.splitter_subplots = QtWidgets.QSplitter(QtCore.Qt.Vertical)  
        
        for subplot_item in self._subplot_widget_container.values():
            graphics_view = pg.GraphicsView()
            graphics_view.setCentralItem(subplot_item)
            self.splitter_subplots.addWidget(graphics_view)

        surface_layout.addWidget(self.pyvol_gl_widget, 0, 0)
        surface_layout.addWidget(self.pyvol_gl_widget.get_legend(), 0, 0, alignment=QtCore.Qt.AlignBottom | QtCore.Qt.AlignRight)
        self.addWidget(container_widget)
        self.addWidget(self.splitter_subplots)
        self.setSizes([20000, 10000])   
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        
    def set_aw(self, aw):
        self.another_window=aw
        
    def _internal_update_view(self, calibrated_surface_container: Dict[str, SurfaceCalibration]):
            print(calibrated_surface_container)
        #if not self._intense_interaction:
            self.update_dataclasses(calibrated_surface_container)
            self.update_plots()     
            self._queued_update=False
        #else:
        #    self._queued_update=True

    def update_dataclasses(self, calibrated_surface_container: Dict[str, SurfaceCalibration]):
        for px_type in self.displayed_price_types:
            surface_engine = calibrated_surface_container[px_type]
            volatility_data = self.volatility_data_container[px_type]
            for plot_type in self._displayed_assets:
                dataclass = volatility_data.get_dataclass(plot_type)
                dataclass.evaluate_from_engine(surface_engine)
                
    

    def update_plots(self):
        for px_type in self.displayed_price_types:
            volatility_data = self.volatility_data_container[px_type]
            for plot_type in self._displayed_assets:
                dataclass = volatility_data.get_dataclass(plot_type)
                internal_id = self.displayed_price_plot_type_names[px_type][plot_type]
                
                gl_plotdataitem = self.pyvol_gl_widget.plotItem(internal_id)
                gl_plotdataitem.setData(**dataclass.plot_item_kwargs())
                                
                if plot_type == "surface":
                    for sub_dataclass in volatility_data.surface_children():
                        if sub_dataclass.valid_values:
                            subplot_title = self._dclass_name_subplot_title_map[sub_dataclass.name]
                            subplot_widget = self._subplot_widget_container[subplot_title]
                            subplot_widget.pricePlotDataItem(px_type).setData(**sub_dataclass.plot_item_kwargs())
                                                
    def _add_surface_plot_data_item(self, px_type):
        if not self.displayed_price_plot_type_flags[px_type]["surface"]: 
            volatility_data = self.volatility_data_container[px_type]            
            surface_plotdataitem = PyVolGL3DSurfacePlotItem(px_type=px_type,
                                                            colormap=self.colour_styles_config["surface"][px_type],
                                                            color=self.colour_styles_config["scatter"][px_type],
                                                            **volatility_data.surface.plot_item_kwargs()
                                                            )
            self.pyvol_gl_widget.addItem(surface_plotdataitem, ignoreBounds=False)
            
            self.displayed_price_plot_type_flags[px_type]["surface"]=True
            self.displayed_price_plot_type_names[px_type]["surface"]=surface_plotdataitem.id()
            
            if self.plot_state["subplots"]:
                self._add_subplot_line(px_type, volatility_data)

    def _add_subplot_line(self, px_type: str, volatility_data: VolatilityData):
        pen = pg.mkPen(color=self.colour_styles_config["scatter"][px_type])
        for sub_dataclass in volatility_data.surface_children():
            subplot_title = self._dclass_name_subplot_title_map[sub_dataclass.name]
            if subplot_title in self._subplot_widget_container:
                subplot_widget = self._subplot_widget_container[subplot_title]
                _ = subplot_widget.plotFromDataClass(sub_dataclass,
                                                     px_type=px_type,
                                                     pen=pen
                                                     )

    def _add_scatter_plot_data_item(self, px_type):        
        if not self.displayed_price_plot_type_flags[px_type]["scatter"]:
            volatility_data = self.volatility_data_container[px_type]
            scatter_plotdataitem = PyVolGL3DScatterPlotItem(px_type=px_type,
                                                            color=self.colour_styles_config["scatter"][px_type],
                                                            **volatility_data.scatter.plot_item_kwargs()
                                                            )
            
            self.pyvol_gl_widget.addItem(scatter_plotdataitem, ignoreBounds=False)
            
            self.displayed_price_plot_type_flags[px_type]["scatter"]=True
            self.displayed_price_plot_type_names[px_type]["scatter"]=scatter_plotdataitem.id()

    def _remove_surface_plot_data_item(self, px_type):
        if px_type in self.pyvol_gl_widget.surface_plotitems:
            self.pyvol_gl_widget.removeItem(self.pyvol_gl_widget.surface_plotitems[px_type])
            self.displayed_price_plot_type_names[px_type]["surface"]=None
            self.displayed_price_plot_type_flags[px_type]["surface"]=False
            
            if self.plot_state["subplots"]:
                volatility_data = self.volatility_data_container[px_type]

                for sub_dataclass in volatility_data.surface_children():
                    subplot_title = self._dclass_name_subplot_title_map[sub_dataclass.name]
                    if subplot_title in self._subplot_widget_container:
                        subplot_widget = self._subplot_widget_container[subplot_title]
                        subplot_widget.removePricePlotDataItem(px_type)              

    def _remove_scatter_plot_data_item(self, px_type):
        if px_type in self.pyvol_gl_widget.scatter_plotitems:
            self.pyvol_gl_widget.removeItem(self.pyvol_gl_widget.scatter_plotitems[px_type])
            self.displayed_price_plot_type_names[px_type]["scatter"]=None
            self.displayed_price_plot_type_flags[px_type]["scatter"]=False
            
    def toggle_price_type(self, flag, px_type):
        if flag:
            if not px_type in self.displayed_price_types:
                if self.plot_state["surface"]:
                    self._add_surface_plot_data_item(px_type)
                if self.plot_state["scatter"]:
                    self._add_scatter_plot_data_item(px_type)
                self.displayed_price_types.append(px_type)    
        else:
            if px_type in self.displayed_price_types:
                if self.plot_state["surface"]:
                    self._remove_surface_plot_data_item(px_type)
                if self.plot_state["scatter"]:
                    self._remove_scatter_plot_data_item(px_type)
                self.displayed_price_types.remove(px_type)

    def _toggle_surface(self, check):
        if check == self.plot_state["surface"]:
            return
        if not self.plot_state["surface"]:
            for px_type in self.pyvol_gl_widget.get_displayed_price_types().copy():
                self._add_surface_plot_data_item(px_type)
        else:
            for px_type in self.pyvol_gl_widget.get_displayed_price_types().copy():
                self._remove_surface_plot_data_item(px_type)
        self.plot_state["surface"] = not self.plot_state["surface"]
        
    def _toggle_scatter(self, check):
        if check == self.plot_state["scatter"]:
            return 
        if not self.plot_state["scatter"]:
            for px_type in self.pyvol_gl_widget.get_displayed_price_types().copy():
                self._add_scatter_plot_data_item(px_type)
        else:
            for px_type in self.pyvol_gl_widget.get_displayed_price_types().copy():
                self._remove_scatter_plot_data_item(px_type)
        self.plot_state["scatter"] = not self.plot_state["scatter"]
        
    def toggle_3D_objects(self, check, plot_type):
        if plot_type == "surface":
            self._toggle_surface(check)
        elif plot_type == "scatter":
            self._toggle_scatter(check)
             
    def toggle_subplots(self, state):
        if state=="On" and not self.plot_state["subplots"]:
            self.splitter_subplots.show()
            self.plot_state["subplots"]=True

        elif state=="Off" and self.plot_state["subplots"]:
            self.splitter_subplots.hide()
            self.plot_state["subplots"]=False
            
    def interface_switch(self, *args):
        self._internal_update_view()

    def plot_queued_update(self):
        if self._queued_update:
            self.update_plots()    
            self._queued_update=False
    
    def generate_random(self):
        pass
    
    def switch_axis(self, axis_label, axis_direction):
        if isinstance(axis_direction, str):
            str_int_map = {"x" : 0,
                           "y" : 1,
                           "z" : 2,
                           }
            axis_direction=str_int_map[axis_direction]
        for axis_item in self.pyvol_gl_widget.axes[axis_direction]:
            if axis_item.style["showLabel"]:
                axis_item.setLabel(axis_label)
            
        for subplot in self._subplot_widget_container.values():
            if subplot.axisSlice() == axis_direction:
                if axis_direction == 2:
                    axis_item = subplot.getAxis("left")
                else:
                    axis_item = subplot.getAxis("bottom")
                axis_item.setLabel(axis_label)
       # self.pyvol_gl_widget.vb.
      #  self.pyvol_gl_widget.vb.enableAutoRange(enable=True)

    def switch_axis_units(self, scale, axis):
        scale = float(scale)
        if isinstance(axis, str):
            if axis == "x":
                ax=0
            elif axis == "y":
                ax=1
            elif axis == "z":
                ax=2
        for axis_item in self.pyvol_gl_widget.axes[ax]:
            axis_item.setScale(scale)
        
        for subplot in self._subplot_widget_container.values():
            if ax == 2:
                axis_item = subplot.getAxis("left")
                axis_item.setScale(scale)
                axis_item.update()
            else:
                if subplot.axisSlice() == ax:
                    axis_item = subplot.getAxis("bottom")
                    axis_item.setScale(scale)
                    axis_item.update()       
    
    def dataRange(self):
        x_values, y_values, z_values = [], [], []
        for px_type in self.displayed_price_types:
            volatility_data = self.volatility_data_container[px_type]
            for plot_type in self._displayed_assets:
                dataclass = volatility_data.get_dataclass(plot_type)
                x, y, z = dataclass.data()
                x_values = np.append(x_values, x)
                y_values = np.append(y_values, y)
                z_values = np.append(z_values, z.flatten())
        
        x_range = np.nanmin(x_values), np.nanmax(x_values)
        y_range = np.nanmin(y_values), np.nanmax(y_values)
        z_range = np.nanmin(z_values), np.nanmax(z_values)
        return x_range, y_range, z_range
    

@dataclass(slots=True)
class DisplayMap:
    all_price_types: InitVar[List[str]]
    price_types: List[str] = field(default=list)
    plot_types: List[str] = field(default=list)
    price_plot_flag: Dict[str, Dict[str, bool]] = field(default_factory=dict)
    price_plot_name: Dict[str, Dict[str, str|None]] = field(default_factory=dict)

    def __post_init__(self, all_price_types):
        self.price_plot_flag.update({px_type: {"surface" : False, "scatter" : False} for px_type in all_price_types})
        self.price_plot_name.update({px_type: {"surface" : None, "scatter" : None} for px_type in all_price_types})
    
    def add_plots_for_price_type(self, px_type):
        plots_to_add = []
        for plot_type, flag in self.price_plot_flag[px_type].items():
            if not flag:
                self.price_plot_flag[px_type][plot_type]=True        
        return plots_to_add
    
    def remove_plots_for_price_type(self, px_type):
        plots_to_remove = []
        for plot_type, flag in self.price_plot_flag[px_type].items():
            if not flag:
                self.price_plot_flag[px_type][plot_type]=True        
     #   return plots_to_add


