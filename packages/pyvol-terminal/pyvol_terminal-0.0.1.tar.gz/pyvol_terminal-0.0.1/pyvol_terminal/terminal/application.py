from __future__ import annotations
from typing import List, Dict, Union, Tuple, Callable, TYPE_CHECKING, Any, Optional, Any
if TYPE_CHECKING:
    from instruments.utils import InstrumentManager

from PySide6 import QtCore, QtWidgets, QtGui
from .. import windows
from pyvol_terminal import workers
from pyvol_terminal.data_classes import builders as builders_data_classes
from . import frontend, stylesheets
from ..workers import ABCCalibrationWorker
from ..interfaces.abstract_classes import ABCInterface
from ..requirements_tracker import RequirementsTracker


from PySide6 import QtCore, QtGui, QtWidgets
from pprint import pprint
from pyvol_terminal.interfaces.abstract_classes import ABCInterface

interface_container: Dict[str, ABCInterface] = {}

class Application(QtWidgets.QApplication):  
    create_window_signal = QtCore.Signal(dict, str, tuple)
    window_titles_signal = QtCore.Signal(list)
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def get_instance(cls):
        return cls._instance
    
    def __init__(self,
                 argv: List[str],
                 interface_config_container: Dict[str, Dict[str, Any]]=None,
                 ws_worker_config=None,
                 data_processing_config=None,
                 option_configurations: Dict[str, Any]=None,
                 requirements_tracker=None,
                 ):
        super().__init__(argv)
        
        self.option_configurations=option_configurations
        self.interface_configs=interface_config_container
        self.aboutToQuit.connect(self.exiting)
        self.n_windows=0
        self._calibration_workers: Dict[str, ABCCalibrationWorker]={}
        self._initialized = True
        self.requirements_tracker=requirements_tracker if not requirements_tracker is None else RequirementsTracker()
        
        self.setFont(stylesheets.get_global("font"))
        self.setStyleSheet(stylesheets.get_global("widgets"))

        main_instruments = list(option_configurations.keys())
        interfaces = list(interface_config_container.keys())
        
        self.terminal = frontend.Frontend(self.open_interface,
                                          main_instruments,
                                          interfaces
                                          )
        self.terminal.show()
        all_instruments = {}
        for option_config in self.option_configurations.values():
            all_instruments = all_instruments | option_config["instrument_manager"].all_instrument_objects
     
        self._websocket_worker = workers.WebsocketWorker(data_processing_config=data_processing_config,
                                                         ws_worker_config=ws_worker_config,
                                                         all_instruments=all_instruments,
                                                         )
        
        self.terminal.combo_box.setCurrentIndex(1)
        self.terminal.buttons[0].click()
 
    def start(self):
        self._websocket_worker.start()

    def open_interface(self, instrument: str, interface_type: str):        
        window_title = f"{instrument}: {interface_type}"
                
        option_chain_container = self.option_configurations[instrument]["options_chain_container"]
        instrument_manager: InstrumentManager = self.option_configurations[instrument]["instrument_manager"]
        
        active_instruments = set(instrument_manager.all_instrument_objects.keys())
        
        vol_vect_container = builders_data_classes.create_vol_vect_container(option_chain_container)
    
        surface_calibration_config = self.option_configurations[instrument]["surface_calibration_config"]
        
        if not instrument in self._calibration_workers:
            surface_calibration_worker=workers.SurfaceCalibration(option_chain_container=option_chain_container,
                                                                  vol_vect_container=vol_vect_container,
                                                                  calibration_engines=surface_calibration_config["engine_container"],
                                                                  active_instruments=active_instruments,
                                                                  update_timer=surface_calibration_config["update_timer"],
                                                                  )
            self._calibration_workers[instrument] = surface_calibration_worker
        else:
            surface_calibration_worker = self._calibration_workers[instrument]
        
        configs_to_add = {"instrument_manager" : instrument_manager,
                       #   "surface_calibration_config" : surface_calibration_config,
                          "vol_vect_container" : vol_vect_container,
                          }
        
        interface_configs = self.interface_configs[interface_type]
        interface_configs.update(configs_to_add)
        interface_class = interface_configs.get("widget_class")
        interface: ABCInterface = interface_class(**self.interface_configs[interface_type])
                
        interface_update_slot = interface.get_calibration_slot()
        surface_calibration_worker.calibratedSignal.connect(interface_update_slot)
        interface.aboutToCloseSig.connect(self.interface_closing)
        interface.setWindowTitle(window_title)
      #  self.connectInteraction(interface.main_view, [self._websocket_worker.setIntenseInteraction,
     #                                                 self._websocket_worker.setIntenseInteraction
     #                                                 ])
        
        interface_container[window_title] = interface
        self._websocket_worker.add_active_instruments(active_instruments)
                
    @QtCore.Slot(ABCInterface)
    def interface_closing(self, interface_closing: windows.InterfaceWindow):
        del interface_container[interface_closing.windowTitle()]

        current_active_instruments = set()
        delete_calibration_worker=True
        for remaining_interfaces in interface_container.values():
            if isinstance(remaining_interfaces, ABCInterface):
                calibration_worker = remaining_interfaces.calibration_worker
                current_active_instruments.update(calibration_worker.active_instruments)
                if calibration_worker == interface_closing.calibration_worker:
                    delete_calibration_worker = False
                    
        if delete_calibration_worker:
            interface_closing.calibration_worker.stop_worker()
            del self._calibration_workers[interface_closing.primary_instrument]

        self._websocket_worker.reset_active_instruments(current_active_instruments)
    
    def connectInteraction(self, main_view, receivers: List[Callable]):
        return
        for receiver in receivers:
            main_view.add_interact_end_callback(receiver)
                
        
    def open_sub_window(self,
                        widget: QtWidgets.QWidget,
                        geometry: QtCore.QRect=None,
                        adjustToContents: bool=False,
                        flags=None,
                        parent: QtWidgets.QWidget=None,
                        ) -> windows.SubWindow:
        
        for i in range(1, 9999):
            window_title = f"Sub Window {i}"
            if not window_title in interface_container:
                break 
        win = windows.SubWindow(widget, geometry, adjustToContents, flags, parent=parent)
        interface_container[window_title] = win

    @QtCore.Slot()
    def exiting(self):
        try:
            loop = self._websocket_worker.websocket.get_loop()
            import asyncio
            asyncio.run_coroutine_threadsafe(self._websocket_worker.websocket.stop(), loop)
            

        except:
            pass
        self._websocket_worker.stop_worker()

    def update_instrument_quantities(self, metric):
        self.requirements_tracker.add_interface_requirement(metric)
        print(self.requirements_tracker.current_requirements)
        
    def verify_object_method_returns_callable(self,
                                              obj: Any,
                                              method_name: str,
                                              *method_args,
                                              **method_kwargs
                                              ) -> tuple[bool, Optional[Callable]]:
        """
        Verify an instantiated object has a method that returns a callable.
        
        Args:
            obj: Instantiated object to check
            method_name: Name of the method to verify
            *method_args: Positional arguments to pass to the method
            **method_kwargs: Keyword arguments to pass to the method
            
        Returns:
            tuple: (success: bool, returned_callable: Optional[Callable])
                - success: True if verification passed
                - returned_callable: The callable if verification succeeded, else None
        """
        # Check if object has the method
        if not hasattr(obj, method_name):
            return (False, None)
        
        method = getattr(obj, method_name)
        
        # Check if it's a callable method
        if not callable(method):
            return (False, None)
        
        try:
            # Call the method and get its return value
            returned_value = method(*method_args, **method_kwargs)
            
            # Verify the returned value is callable
            if callable(returned_value):
                return (True, returned_value)
            return (False, None)
            
        except Exception as e:
            # Handle any exceptions during method call
            print(f"Verification failed with error: {str(e)}")
            return (False, None)