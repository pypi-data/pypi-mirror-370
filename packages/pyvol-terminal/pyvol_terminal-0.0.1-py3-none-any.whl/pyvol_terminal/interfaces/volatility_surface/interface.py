from __future__ import annotations 
from typing import List, Optional, Tuple, Union, Dict, TYPE_CHECKING, Callable, Any

    
from PySide6 import QtCore, QtWidgets
from . import settings
from .. import abstract_classes
from ...quantities import engines
from ...data_classes import builders as builders_data_classes
from ..abstract_classes import ABCInterface, ABC
from ...instruments.utils import InstrumentManager
from ...workers import SurfaceCalibration
from ...quantities.engines import TickEngineManager
from . import pyvol_GL3DViewWidget
from ...data_classes.classes import AbstractDataClass, VolatilityData, VolVector, Surface, Points, Slice
from ...data_classes import builders as builders_data_classes
from PySide6 import QtCore, QtWidgets, QtGui
from . import init_helpers
from .. import custom_widgets, subplot
import pyqtgraph as pg
from . import pyvol_GL3DViewWidget
from pyvol_terminal.misc_classes import PriceText
import time
from ...gl_3D_graphing.graphics_items import GL3DGraphicsItems
from .pyvol_GL3DGraphicsItems import PyVolGL3DSurfacePlotItem, PyVolGL3DScatterPlotItem

import traceback
from ..abstract_classes import ABCInterface
from dataclasses import dataclass, field, InitVar
import numpy as np
from pprint import pprint   
from .pyvol_GL3DViewWidget import PyVolGL3DViewWidget
from .dock_window import SplitDockWidget, SubPlotItem
from PySide6.QtCore import Qt

QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps)


class Interface(ABCInterface):
    aboutToCloseSig = QtCore.Signal(QtWidgets.QMainWindow)
    
    
    def __init__(self,
                 instrument_manager: InstrumentManager=None,
                 tick_engine_manager=None,
                 vol_vect_container=None,
                 queue_interaction: bool=False,
                 colour_styles_config: Dict[str, str]={},
                 **configs
                 ):
        super().__init__()

        self.all_price_types = instrument_manager.config["options"]["price_types"]
        self.splot_flag=True
        self.subplots_flag=True
        self.on_view=False
        self.plot_interaction_buffer=[]
        self._first_show=True
        
        if tick_engine_manager is None:
            tick_engine_manager = engines.TickEngineManager("Strike",
                                                            "Date",
                                                            "Implied Volatility"
                                                            )
            
        self.volatility_data_container = builders_data_classes.create_volatility_data_from_vol_vect(vol_vect_container)

        self.pyvol_gl_widget: PyVolGL3DViewWidget=None
        
        self.queue_interaction=queue_interaction
        
        self.interact_finish_callbacks=[]
        
        self.colour_styles_config=colour_styles_config

        all_price_types = instrument_manager.config["options"]["price_types"]
        
        self._dclass_name_subplot_title_map: Dict[str, str]={"skew" : "Skew",
                                                             "term" : "Term Structure"
                                                             }
        self._all_assets = ["surface", "scatter"]
        self._displayed_assets = ["surface", "scatter"]
        self._subplot_widget_container: Dict[str, SubPlotItem]={}
        
        self.displayed_price_types=[]
        self.displayed_price_plot_type_flags = {px_type: {"surface" : False, "scatter" : False} for px_type in self.all_price_types}
        self.displayed_price_plot_type_names = {px_type: {"surface" : None, "scatter" : None} for px_type in all_price_types}
        
        self.plot_state = {"surface" : True,
                           "scatter" : True,
                           "subplots" : True,
                           }

        self.scatter_from_calibrated=True

        self._initScene(instrument_manager, tick_engine_manager, **configs)
        self.showMaximized()
        
    
    def addSettings(self, settings):
        if not settings is None:
            self.addToolBar(settings)
    
    def get_calibration_slot(self) -> Callable:
        return self.update_view

    def _initScene(self,
                   instrument_manager: InstrumentManager,
                   tick_engine_manager: TickEngineManager,
                   **configs
                   ):
        spot_objects = [item for item in instrument_manager.spot_instrument_container.objects.values()]
        spot_text = PriceText(spot_objects)
        central_widget = PyVolGL3DViewWidget(spot_text, computeNormals=False, **configs)
        self.setCentralWidget(central_widget)
        
        settings_widget = self._buildSettings(instrument_manager, tick_engine_manager)
        settings_widget.setAllowedAreas(Qt.TopToolBarArea | Qt.BottomToolBarArea)

        split_dock_widget = SplitDockWidget(tick_engine_manager=tick_engine_manager)
        split_dock_widget.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        self.addDockWidget(Qt.RightDockWidgetArea, split_dock_widget)
        self.addToolBar(settings_widget)
        
    def _buildSettings(self,
                       instrument_manager: InstrumentManager,
                       tick_engine_manager: TickEngineManager
                       ) -> settings.Settings:
        
        settings_widget = settings.Settings(self)

        
        settings_widget.add_window_menu(self.switch_axis_units)
        settings_widget.add_vol_src_window_menu(self.all_price_types, 
                                                [self.toggle_price_type, instrument_manager.update_metric_calculations]
                                                )
        
        switch_axis_slots = [tick_engine_manager.change_function]
        switch_axis_slots = switch_axis_slots + [vola_data.vol_vector.metric_engine.change_function for vola_data in self.volatility_data_container.values()]
        switch_axis_slots = switch_axis_slots + [self.switch_axis]      

        settings_widget.create_combobox_menu("Moneyness",
                                             ["Strike", "Delta", "Moneyness", "Log-Moneyness", "Standardised-Moneyness"],
                                             switch_axis_slots,
                                             "x"
                                             )

        settings_widget.create_combobox_menu("Tenor",
                                             ["Date", "Years"],
                                             switch_axis_slots,
                                             "y"
                                             )

        settings_widget.create_combobox_menu("Volatility",
                                             ["Implied Volatility", "Variance", "Total Volatility", "Total Variance"],
                                             switch_axis_slots,
                                             "z"
                                             )

        settings_widget.create_combobox_menu("Toggle Crosshairs",
                                             ["On", "Off"],
                                             self.centralWidget().toggle_crosshairs,
                                             )
        
        #settings_widget.create_vol_src_menu(self.all_price_types,
                                            #[self.toggle_price_type, instrument_manager.update_metric_calculations]
                                            #)

        settings_widget.create_toggle_buttons("Toggle 3D Assets",
                                              ["surface", "scatter"], 
                                              [self.toggle_3D_objects],
                                              )
        return settings_widget
    
    def _internal_update_view(self, calibrated_surface_container: Dict[str, SurfaceCalibration]):
            print(calibrated_surface_container)
            self.update_dataclasses(calibrated_surface_container)
            self.update_plots()     
            self._queued_update=False

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
                
                gl_plotdataitem = self.centralWidget().plotItem(internal_id)
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
            self.centralWidget().addItem(surface_plotdataitem, ignoreBounds=False)
            
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
            
            self.centralWidget().addItem(scatter_plotdataitem, ignoreBounds=False)
            
            self.displayed_price_plot_type_flags[px_type]["scatter"]=True
            self.displayed_price_plot_type_names[px_type]["scatter"]=scatter_plotdataitem.id()

    def _remove_surface_plot_data_item(self, px_type):
        if px_type in self.centralWidget().surface_plotitems:
            self.centralWidget().removeItem(self.centralWidget().surface_plotitems[px_type])
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
        if px_type in self.centralWidget().scatter_plotitems:
            self.centralWidget().removeItem(self.centralWidget().scatter_plotitems[px_type])
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
            for px_type in self.centralWidget().get_displayed_price_types().copy():
                self._add_surface_plot_data_item(px_type)
        else:
            for px_type in self.centralWidget().get_displayed_price_types().copy():
                self._remove_surface_plot_data_item(px_type)
        self.plot_state["surface"] = not self.plot_state["surface"]
        
    def _toggle_scatter(self, check):
        if check == self.plot_state["scatter"]:
            return 
        if not self.plot_state["scatter"]:
            for px_type in self.centralWidget().get_displayed_price_types().copy():
                self._add_scatter_plot_data_item(px_type)
        else:
            for px_type in self.centralWidget().get_displayed_price_types().copy():
                self._remove_scatter_plot_data_item(px_type)
        self.plot_state["scatter"] = not self.plot_state["scatter"]
        
    def toggle_3D_objects(self, check, plot_type):
        if plot_type == "surface":
            self._toggle_surface(check)
        elif plot_type == "scatter":
            self._toggle_scatter(check)
            
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
        for axis_item in self.centralWidget().axes[axis_direction]:
            if axis_item.style["showLabel"]:
                axis_item.setLabel(axis_label)
            
        for subplot in self._subplot_widget_container.values():
            if subplot.axisSlice() == axis_direction:
                if axis_direction == 2:
                    axis_item = subplot.getAxis("left")
                else:
                    axis_item = subplot.getAxis("bottom")
                axis_item.setLabel(axis_label)
       # self.centralWidget().vb.
      #  self.centralWidget().vb.enableAutoRange(enable=True)
    
    

    def switch_axis_units(self, scale, axis):
        scale = float(scale)
        if isinstance(axis, str):
            if axis == "x":
                ax=0
            elif axis == "y":
                ax=1
            elif axis == "z":
                ax=2
        for axis_item in self.centralWidget().axes[ax]:
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
    
    def centralWidget(self) -> PyVolGL3DViewWidget:
        return super().centralWidget()
    
    def showEvent(self, event):
        super().showEvent(event)
        if self._first_show:
            dockwidget = self.findChild(QtWidgets.QDockWidget)
            QtCore.QTimer.singleShot(100, lambda: dockwidget.size().setWidth(self.size().width()/3))
            self._first_show = False
        return 