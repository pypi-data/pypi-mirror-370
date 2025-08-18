from __future__ import annotations 
from typing import List, Optional, Tuple, Union, Dict, TYPE_CHECKING, Callable, Any
if TYPE_CHECKING:
    from instruments.instruments import Option
    from instruments.utils import InstrumentManager
    from ...engines.interpolation_engines import Abstract3DInterpolator
    from ...data_classes.classes import VolatilityData, VolVector

from PySide6 import QtWidgets
from ...quantities import engines
from . import stylesheets as vol_table_utils
import numpy as np
from PySide6.QtCore import Qt
from . import settings, main_view 
from .. import abstract_classes
from ...data_classes import builders as builders_data_classes


class Interface(abstract_classes.ABCInterface):
    def __init__(self,
                 instrument_manager: InstrumentManager=None,
                 surface_calibration_config: Dict[str, Dict[str, Any]]={},
                 tick_engine_manager=None,
                 vol_vect_container=None,
                 **configs
                 ):
        super().__init__()
        volatility_data_container = builders_data_classes.create_volatility_data_from_vol_vect(vol_vect_container)
        
        self.splot_flag=True
        self.subplots_flag=True
        self.on_view=False
        self.plot_interaction_buffer=[]
        
        if tick_engine_manager is None:
            self.tick_engine_manager = engines.TickEngineManager("Strike",
                                                                 "Date",
                                                                 "Implied Volatility"
                                                                 )
        else:
            self.tick_engine_manager=tick_engine_manager

        self.data_view = main_view.MainView(instrument_manager,
                                            interpolation_config,
                                            self.tick_engine_manager)
                
        self.initSpotPrice(instrument_manager)
        
        self.widget_settings = settings.Settings(self,
                                                 self.tick_engine_manager,
                                                 self.data_view.metric_axis_engine,
                                                 self.spot_qlabel)
        layout_v = QtWidgets.QVBoxLayout()
        layout_v.addWidget(self.widget_settings)
        layout_v.addWidget(self.data_view)
        self.setLayout(layout_v)
                
    def initSpotPrice(self, instrument_manager):
        if len(instrument_manager.spot_instrument_container.objects) > 0:
            self.spot_name = list(instrument_manager.spot_instrument_container.objects.keys())[0]
            self.spot_object = list(instrument_manager.spot_instrument_container.objects.values())[0]
            
            self.spot_qlabel = QtWidgets.QLabel(f"{self.spot_name}: {self.spot_object.mid}")
            self.spot_qlabel.setStyleSheet(vol_table_utils.get_settings_stylesheets("SpotQLabel"))
            self.spot_qlabel.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        else:
            self.spot_qlabel=None

    def update_spot_text(self):
        if not self.spot_qlabel:
            self.spot_qlabel.setText(f"{self.spot_name}:  {f"{self.spot_object.mid:,.2f}"}")
    