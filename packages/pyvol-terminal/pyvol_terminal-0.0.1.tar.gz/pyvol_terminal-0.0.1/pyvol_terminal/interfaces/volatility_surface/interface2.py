from __future__ import annotations 
from typing import List, Optional, Tuple, Union, Dict, TYPE_CHECKING, Callable, Any
if TYPE_CHECKING:
    from instruments.utils import InstrumentManager
    
from PySide6 import QtCore, QtWidgets
from . import main_view
from . import settings
from .. import abstract_classes
from ...quantities import engines
from ...data_classes import builders as builders_data_classes
from ..abstract_classes import ABCInterface, ABC


QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps)


class Interface(abstract_classes.ABCInterface):
    aboutToCloseSig = QtCore.Signal(QtWidgets.QMainWindow)
    def __init__(self,
                 instrument_manager: InstrumentManager=None,
                 surface_calibration_config: Dict[str, Dict[str, Any]]={},
                 tick_engine_manager=None,
                 vol_vect_container=None,
                 **configs
                 ):
        super().__init__()
        self.all_price_types = instrument_manager.config["options"]["price_types"]
        
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

        volatility_data_container = builders_data_classes.create_volatility_data_from_vol_vect(vol_vect_container)
        
        self.main_view: ABCInterface = main_view.MainView(instrument_manager,
                                                        engine_container=surface_calibration_config["engine_container"],
                                                        tick_engine_manager=self.tick_engine_manager,
                                                        spot_objects=instrument_manager.spot_instrument_container.get_objects(),
                                                        volatility_data_container=volatility_data_container,
                                                        **configs
                                                        )  
        #self.main_view.addIntenseInteraction("settings")
        
        self.setCentralWidget(self.main_view)
        settings = self._initSettings()
        
        self.addSettings(settings)
        
        settings.toggle_vol_src(self.all_price_types[0])
                    
        self.showMaximized()
    
        
    def addSettings(self, settings):
        if not settings is None:
            self.addToolBar(settings)
    
    
    def get_calibration_slot(self) -> Callable:
        return self.main_view.update_view

    def _initSettings(self) -> settings.Settings:
        settings_widget = settings.Settings(self)
     
        settings_widget.processIntenseInteraction=self.main_view.processInteractionState
        
        switch_axis_slots = [self.tick_engine_manager.change_function]
        switch_axis_slots = switch_axis_slots + [vola_data.vol_vector.metric_engine.change_function for vola_data in self.main_view.volatility_data_container.values()]
        switch_axis_slots = switch_axis_slots + [self.main_view.switch_axis]      
        
        settings_widget.add_window_menu(self.main_view.switch_axis_units)

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
                                             self.main_view.pyvol_gl_widget.toggle_crosshairs,
                                             )
        
        settings_widget.create_vol_src_menu(self.all_price_types,
                                            [self.main_view.toggle_price_type]
                                            )

        settings_widget.create_toggle_buttons("Toggle 3D Assets",
                                              ["surface", "scatter"], 
                                              [self.main_view.toggle_3D_objects],
                                              )
        return settings_widget
    
    
