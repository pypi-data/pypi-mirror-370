from typing import List, Optional, Tuple, Union, Dict, TYPE_CHECKING, Callable, Any
if TYPE_CHECKING:
    
    from ...data_classes.classes import VolatilityData, VolVector
    
from PySide6 import QtWidgets
from pyvol_terminal.settings import utils as settings_utils
from . import main_view
import pyqtgraph as pg
from . import utils
from pyvol_terminal import misc_widgets
from .. import abstract_classes, custom_widgets
from . import settings, main_view
from ...quantities import engines
from ...instruments.utils import InstrumentManager
from ...data_classes import builders as builders_data_classes


class Interface(abstract_classes.ABCInterface):
    def __init__(self,
                 instrument_manager: InstrumentManager=None,
                 surface_calibration_config: Dict[str, Dict[str, Any]]={},
                 tick_engine_manager=None,
                 vol_vect_container=None,
                 **configs
                 ):        
        self.instrument_manager=instrument_manager
        self.tick_engine_manager=tick_engine_manager
        settings_slots = {"Change Dimensions" : lambda:None,
                          "Toggle Price Types" : lambda:None
                          }
                          
        if tick_engine_manager is None:
            self.tick_engine_manager = engines.TickEngineManager("Strike",
                                                                 "Date",
                                                                 "Implied Volatility"
                                                                 )
        else:
            self.tick_engine_manager=tick_engine_manager
            
        volatility_data_container = builders_data_classes.create_volatility_data_from_vol_vect(vol_vect_container)


        self.widget_settings = settings.Settings(settings_slots)
        
        self._initLayout(instrument_manager,
                         surface_calibration_config["engine_container"],
                         self.tick_engine_manager,
                         self.instrument_manager.spot_instrument_container.get_objects(),
                         volatility_data_container
                         )
        
        
        
        self.all_price_types = self.instrument_manager.config["options"]["price_types"]
        self.splot_flag=True
        self.line_objects = {}
        self.displayed_price_types=["mid"]
        self.surface_flag=True
        self.scatter_flag=True
        self.subplots_flag=True


        #self.axis_transform_engine = plotting_engines.MetricEngine(self.data_container.domain.base_domain)

        self.line_objects = {px_type : {} for px_type in self.all_price_types}
        self.scatter_objects = {px_type : {} for px_type in self.all_price_types}
        self.displayed_domains=[]
    
    def _initLayout(self,
                    instrument_manager,
                    engine_container,
                    tick_engine_manager,
                    spot_objects,
                    volatility_data_container,
                    **configs
                    ):


        stacked_layout = QtWidgets.QStackedLayout()
        
        for axis, slice_type in "xy", ["smile", "term"]:         
            subplot = main_view.MainView(instrument_manager,
                                         engine_container=engine_container,
                                         tick_engine_manager=tick_engine_manager,
                                         spot_objects=spot_objects,
                                         volatility_data_container=volatility_data_container,
                                         **configs
                                         )  
            stacked_layout.addWidget(subplot)
            lines = subplot.plot.listDataItems()
            
            
            """
            domain_vect = getattr(subplot.data_container.domain, f"{axis}_vect")
            self.domain_str = [self.tick_engine_manager.function(axis, val) for val in domain_vect]
            
            colourmap = utils.legend_colour_getter(self.domain_str)
            main_view.CustomPlotDataItem.pen_map = {exp : pg.mkPen(color=colourmap[exp_str]) for exp, exp_str in zip(domain_vect.domain_vec, self.domain_str)}
            main_view.CustomScatterPlotItem.pen_map = {exp : pg.mkPen(color=colourmap[exp_str]) for exp, exp_str in zip(domain_vect.domain_vec, self.domain_str)}
            """
        
        stacked_layout.setCurrentIndex(0)
        
        central_layout = QtWidgets.QVBoxLayout()
        central_layout.addWidget(self.widget_settings)        
        central_layout.addLayout(stacked_layout)
        self.setLayout(central_layout)
        
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
            

    def create_plot_objects(self, px_type, value):
        self.data_container.add_slice(px_type, value)
        slice = self.data_container.slice_container[px_type][value]
        scatter = main_view.CustomPlotDataItem(x=slice.x, y=slice.y)
        line = main_view.CustomPlotDataItem(x=slice.xi, y=slice.yi)
        self.scatter_objects[px_type][value] = scatter
        self.line_objects[px_type][value] = line
        self.plot_view.add_curve(line)
        
        self.plot_view.addItem(scatter)
        line.show()
        
    def add_line(self, value):
        self.displayed_domains.append(value)
        for px_type in self.displayed_price_types:
            self.main_view.addPlot(px_type, value)
        #value_str = self.generator_func(value)
        #self.legend.add_legend_item(value_str)
        
    def remove_line(self, value):
        self.displayed_domains.remove(value)
        self.data_container.remove_slice(value)
        for px_type in self.displayed_price_types:
            self.plot_view.removeItem(self.line_objects[px_type][value])
            self.plot_view.removeItem(self.scatter_objects[px_type][value])
        value_str = self.generator_func(value)
        self.legend.remove_legend_item(value_str)
        
    def toggle_price_type222(self, px_type):
        if not px_type in self.displayed_price_types:
            self.displayed_price_types.append(px_type)
            for value in self.displayed_domains:
                self.create_plot_objects(px_type, value)
        else:
            self.displayed_price_types.remove(px_type)
            for value in self.displayed_domains:
                self.plot_view.removeItem(self.line_objects[px_type][value])
                self.plot_view.removeItem(self.scatter_objects[px_type][value])
        self.update_line_plots()
    
    def interface_switch(self):
        for instrument_object in self.instrument_manager.options_instrument_container.objects.values():
            self.data_container.update_value_by_instrument_object(instrument_object)
        self.data_container.cleanup()
        self._internal_update_interface()

    def update_line_plots(self):
        for px_type in self.displayed_price_types:
            for value in self.displayed_domains:
                slice = self.data_container.slice_container[px_type][value]
                if slice.valid_data:
                    self.scatter_objects[px_type][value].setData(x=slice.x, y=slice.y)
                    self.line_objects[px_type][value].setData(x=slice.xi, y=slice.yi)
                    
    def switch_axis(self, axis_direction, new_axis_name):
        self.tick_engine_manager.change_function(axis_direction, new_axis_name)
        
        self.data_container.switch_axis(new_axis_name, axis_direction)
        self.tick_engine.update_tick_func(new_axis_name, axis_direction)
        getattr(self, f"{axis_direction}_axis_item").setTitle(new_axis_name)
        self._internal_update_interface()
        
    def _internal_update_interface(self):
        self.update_line_plots()
        
    def update_price_cleanup(self):
        return

        
