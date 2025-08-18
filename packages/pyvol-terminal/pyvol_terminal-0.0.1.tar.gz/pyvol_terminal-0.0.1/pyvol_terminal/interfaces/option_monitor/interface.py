from __future__ import annotations 
from typing import List, Optional, Tuple, Union, Dict, TYPE_CHECKING, Callable, Any
if TYPE_CHECKING:
    from instruments.instruments import Option
    from instruments.utils import InstrumentManager
    from ...engines.interpolation_engines import Abstract3DInterpolator
    from ...data_classes.classes import VolatilityData, VolVector

from PySide6 import QtWidgets, QtCore, QtGui
import numpy as np
from . import stylesheets as stylesheets, settings, main_view
from pyvol_terminal.misc_classes import PriceText
from .. import abstract_classes
from .main_view import MainView

class Interface(abstract_classes.ABCInterface):
    def __init__(self,
                 instrument_manager: InstrumentManager=None,
                 tick_label_engine=None,
                 parent=None,
                 **kwargs):
        super().__init__(parent=parent)
        
        all_price_types: List[str] = instrument_manager.config["options"]["price_types"]
        price_columns = [px_type.capitalize() for px_type in all_price_types]
        if "Mid" in price_columns:
            init_other_columns = ["IVM"]
        
        total_columns = price_columns + [f"IV{px_type[0]}" for px_type in price_columns]
        

        self.main_view: MainView = MainView(instrument_manager=instrument_manager,
                                            tick_label_engine=tick_label_engine,
                                            metricLabels=price_columns + init_other_columns,
                                            **kwargs
                                            )
        
        self.options_container=instrument_manager.options_instrument_container
        underlying_objects = self._collect_underlying_objects(instrument_manager)
        spot_objects = self._spot_objects(instrument_manager.spot_instrument_container)
        if len(underlying_objects) == 1:
            self.widget_settings = settings.Settings(self.main_view.strike_table_column,
                                                     spot_objects=spot_objects,
                                                     columnCollection={"default" : price_columns + init_other_columns,
                                                                       "total" : total_columns},
                                                     )
            expiry_underlying_map=None
        else:
            expiry_underlying_map={}
            for underlying_obj in underlying_objects:
                if hasattr(underlying_obj, "expiry"):
                    expiry = underlying_obj.expiry
                    expiry_underlying_map[expiry] = underlying_obj
                    
            self.main_view.calls_table.add_expiry_underlying_map(expiry_underlying_map)
            self.main_view.puts_table.add_expiry_underlying_map(expiry_underlying_map)
            
            self.widget_settings = settings.Settings(self.main_view.strike_table_column,
                                                     spot_objects=spot_objects)

        self.main_layout_v = QtWidgets.QVBoxLayout(self)
        self.widget_settings.setSizePolicy(QtWidgets.QSizePolicy.Preferred,
                                           QtWidgets.QSizePolicy.Fixed)

        self.setup_default(instrument_manager.spot_instrument_container.objects)
        
        self.main_layout_v.addWidget(self.widget_settings)
        self.main_layout_v.addWidget(self.main_view)
        self.setLayout(self.main_layout_v)
        
        self.main_view.calls_table.right_click_menu.setParent(self)
        self.main_view.puts_table.right_click_menu.setParent(self)
    
    def setup_default(self, spot_objects):
        default_n_strikes = 5
        
        all_strikes = list(self.options_container.maps.strike_expiry_map.keys())
        if len(spot_objects) > 0:
            self.spot_object = list(spot_objects.values())[0]
            if not np.isnan(self.spot_object.mid):
                strike_center = self.spot_object.mid
            else:
                strike_center = 0.5 * (np.amin(all_strikes) + np.amax(all_strikes))
        else:
            strike_center = 0.5 * (np.amin(all_strikes) + np.amax(all_strikes))

        self.widget_settings.strike_center_line.setText(str(strike_center))
        self.widget_settings.strike_center_line.editingFinished.emit()
        self.widget_settings.n_strikes_line.setText(str(default_n_strikes))
        self.widget_settings.n_strikes_line.editingFinished.emit()

    def _collect_underlying_objects(self, instrument_manager: InstrumentManager):
        underlying_objects = []
        for option_object in instrument_manager.options_instrument_container.objects.values():
            underlying_ticker = option_object.underlying_ticker
            underlying_object = instrument_manager.all_instrument_objects[underlying_ticker]
            if not underlying_object in underlying_objects:
                underlying_objects.append(underlying_object)
        return underlying_objects

    def create_underlying_label(self, instrument_manager: InstrumentManager):
        underlying_objects = []
        for option_object in instrument_manager.options_instrument_container.objects.values():
            underlying_object = option_object.underlying_object.ticker
            if not underlying_object in underlying_objects:
                underlying_objects.append(underlying_object)
        
        if len(underlying_objects) == 1:
            self.spot_name = list(instrument_manager.spot_instrument_container.objects.keys())[0]
            self.spot_qlabel = QtWidgets.QLabel(f"{self.spot_name}: {self.spot_object.mid}")
            self.spot_qlabel.setStyleSheet(stylesheets.get_settings_stylesheets("SpotQLabel"))
            self.spot_qlabel.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        else:
            if len(instrument_manager.spot_instrument_container.objects) > 0:
                self.spot_name = list(instrument_manager.spot_instrument_container.objects.keys())[0]
                self.spot_object = list(instrument_manager.spot_instrument_container.objects.values())[0]
                
                self.spot_qlabel = QtWidgets.QLabel(f"{self.spot_name}: {self.spot_object.mid}")
                self.spot_qlabel.setStyleSheet(stylesheets.get_settings_stylesheets("SpotQLabel"))
                self.spot_qlabel.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)

    def _spot_objects(self, spot_instrument_container):
        if not spot_instrument_container is None:
            return list(spot_instrument_container.objects.values())
    
