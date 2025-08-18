from __future__ import annotations 
from typing import List, Optional, Tuple, Union, Dict, TYPE_CHECKING, Callable
if TYPE_CHECKING:
    from data_classes.classes import BaseDomain, Domain, Surface, Points
    from instruments.instruments import Option, Spot
    from instruments.utils import InstrumentManager
    from ...quantities.engines import TickEngineManager
    from ...data_classes.classes import AbstractDataClass, VolatilityData, VolVector, Surface, Points, Slice
    from ...engines.interpolation_engines import Abstract3DInterpolator
    
from PySide6 import QtWidgets
from pyvol_terminal.axis import axis_utils as utils_axis
from . import extra_widgets, stylesheets as vol_table_utils
import numpy as np
from PySide6.QtCore import Qt
from . import settings
import time
from pyvol_terminal.data_classes import builders as builders_data_classes
from ..option_monitor.extra_widgets import CustomDelegate, OptionExpiryCellItem

class MainView(QtWidgets.QTableWidget):
    def __init__(self,
                 instrument_manager: InstrumentManager,
                 tick_engine_manager: TickEngineManager=None,
                 queue_interaction: bool=False,
                 colour_styles_config: Dict[str, str]={},
                 **kwargs
                 ):
        super().__init__(**kwargs)
        self.px_type = "mid"
        self.instrument_manager=instrument_manager
        self.tick_engine_manager=tick_engine_manager

        self.volatility_data_container: Dict[str, VolatilityData] = kwargs.get("volatility_data_container", None)
        self.queue_interaction=queue_interaction

        self.ncols = 10

    
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

        self._initLayout(base_domain, domain, self.data_container)
        self._initCellItems()

    def _initLayout(self, base_domain: BaseDomain, domain: Domain, data_container):
        self.domain = domain
        
        
        self.setRowCount(self.domain.y_vect.size)
        self.setColumnCount(self.ncols)
      #  self.setItemDelegate(CustomDelegate(self))
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.horizontalHeader().setSectionsMovable(False)
        self.verticalHeader().setVisible(True)
        self.verticalHeader().setSectionsMovable(False)
        self.setStyleSheet(vol_table_utils.get_settings_stylesheets("QTableWidget"))
        
        
        self.setShowGrid(False)

    def _initCellItems(self):
        
        row_values = self.domain.y_vect
        column_values = self.domain.x_vect

        row_values = self.metric_axis_engine.transform_axis("y", row_values)
        column_values = self.metric_axis_engine.transform_axis("x", column_values)
        
        self.data_container[self.px_type]["surface"].set_interpolation_domain(column_values, row_values)
        self.row_values = row_values
        self.column_values = np.linspace(column_values.min(), column_values.max(), self.ncols)
        dataclass = self.data_container[self.px_type]["surface"]
        raw = self.data_container[self.px_type]["raw"]
        
        x_metric, y_metric, z_metric, _ = self.metric_axis_engine.transform_values(self.metric_axis_engine.x_base,
                                                                                   self.metric_axis_engine.y_base,
                                                                                   **raw.getDataKwargs())
        
        dataclass.update_data(x_metric, y_metric, z_metric)
        
        self.row_labels = self.tick_engine_manager.y_engine.function(self.row_values)
        self.column_labels=self.tick_engine_manager.x_engine.function(self.column_values)
        
        for idx, label_row in enumerate(self.row_values):
            text_item = OptionExpiryCellItem(label_row)
            self.setVerticalHeaderItem(idx, text_item)
            
        for jdx, label_col in enumerate(self.column_labels):
            text_item = extra_widgets.TableColumnItem(label_col)
            self.setHorizontalHeaderItem(jdx, text_item)
        
        for idx, label_row in enumerate(self.row_values):            
            for jdx, label_col in enumerate(self.column_values):
                
                if dataclass.valid_values:
                    value = dataclass.interpolator.evaluate([label_col], [label_row])
                    new_val_str = self.tick_engine_manager.z_engine.function([value])[0]

                else:
                    new_val_str = ""                
                item = extra_widgets.OptionMetricCellItem(new_val_str)
                self.setItem(idx, jdx, item)


    def update_view(self):
        self.update_data()
        self.update_table()

    def update_data(self):
        dataclass = self.data_container[self.px_type]["surface"]
        raw = self.data_container[self.px_type]["raw"]
        x_metric, y_metric, z_metric, _ = self.metric_axis_engine.transform_values(self.metric_axis_engine.x_base,
                                                                                   self.metric_axis_engine.y_base,
                                                                                   **raw.getDataKwargs())
        dataclass.update_data(x_metric, y_metric, z_metric)
        

    def update_table(self):    
    #    self.setItemDelegate(None)
        if self.data_container[self.px_type]["surface"].valid_values:
            self.blockSignals(True)
            self.setUpdatesEnabled(False)        
            for idx, value_row in enumerate(self.row_values):
                for jdx, value_col in enumerate(self.column_values):
                    value = self.data_container[self.px_type]["surface"].interpolator.evaluate([value_col], [value_row])
                    new_val_str = self.tick_engine_manager.z_engine.function([value])[0]
                    item = self.item(idx, jdx)
                    item.setText(new_val_str)
        #    self.setItemDelegate(CustomDelegate(self))
            self.blockSignals(False)
            self.setUpdatesEnabled(True)
    
    def interface_switch(self):
        pass
    
    def switch_column_metric(self, *args):
        dataclass = self.data_container[self.px_type]["surface"]
        raw = self.data_container[self.px_type]["raw"]
        x_metric, y_metric, z_metric, _ = self.metric_axis_engine.transform_values(self.metric_axis_engine.x_base,
                                                                                   self.metric_axis_engine.y_base,
                                                                                   **raw.getDataKwargs())
        
        dataclass.update_data(x_metric, y_metric, z_metric)
        self.column_values = np.linspace(x_metric.min(), x_metric.max(), self.ncols)
        self.column_labels = self.tick_engine_manager.x_engine.function(self.column_values)
        
        for jdx, label_col in enumerate(self.column_labels):
            self.horizontalHeaderItem(jdx).setText(label_col)
        
        self.update_table()

    def table_domain(self):
        raw = self.data_container[self.px_type]["raw"]

        x_metric, y_metric, z_metric, _ = self.metric_axis_engine.transform_values(self.metric_axis_engine.x_base,
                                                                                   self.metric_axis_engine.y_base,
                                                                                   **raw.getDataKwargs())
        
        
    def switch_price_type(self, px_type):
        self.px_type=px_type
        self.update_data()
        self.update_table()
