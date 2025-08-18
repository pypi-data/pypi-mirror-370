from __future__ import annotations
from typing import List, Dict, Union, Tuple, Callable, TYPE_CHECKING
if TYPE_CHECKING:
    from pyvol_terminal.windows import InterfaceWindow, SubWindow
    from instruments.utils import InstrumentManager

from PySide6 import QtCore, QtWidgets
from . import windows
from pyvol_terminal import workers
from pyvol_terminal.data_classes import builders as builders_data_classes

window_container: Dict[str, InterfaceWindow|SubWindow] = {}


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
                 **window_configs):
        super().__init__(argv)
        self.window_configs=window_configs
        self._initialized = True
        self.window_titles_opened=[]
        self.n_windows=0
        self._worker_threads = {}
        
        
        self._price_process_worker = workers.PriceProcessor(window_configs["instrument_manager"],
                                                            data_processing_config=window_configs["data_processing_config"],
                                                            ws_config=window_configs["websocket_config"]
                                                            )

        self._websocket_worker = workers.WebsocketWorker()
        self._websocket_worker.update_signal.connect(self._price_process_worker.update)
        self.instrument_manager: InstrumentManager=window_configs["instrument_manager"]
        self._price_types = list(window_configs["raw_options_container"].keys())
        
        self.surface_engine_worker=workers.SurfaceCalibration(**self.window_configs, **self.window_configs["surface_construction_config"])
        self._price_process_worker.processedSig.connect(self.surface_engine_worker.price_process_response)
        
    def start(self):       
        self.open_main_window()    
        self._websocket_worker.start()    
        self.surface_engine_worker.start()
        #self.aboutToQuit.connect(self._cleanup)
    
    @QtCore.Slot()
    def price_processed(self):
        pass
    
    def calibrate_surface(self):
        pass
        
    def open_main_window(self):
        for i in range(1, 9999):
            window_title = f"Main Window {i}"
            if not window_title in self.window_titles_opened:
                break 
            
        vol_vect_container = builders_data_classes.create_vol_vect_container(self.surface_engine_worker.raw_options_container,
                                                                             self.instrument_manager.options_instrument_container.original_data,
                                                                            )
        self.window_configs["vol_vect_container"]=vol_vect_container
        win = windows.InterfaceWindow(self,
                                 **self.window_configs
                                 )
        
        window_container[window_title] = win
        
        self.window_titles_opened.append(window_title)    
        self.surface_engine_worker.add_vol_vect_container(window_title,
                                                          vol_vect_container
                                                          )
        win.show()

    def open_sub_window(self, widget: QtWidgets.QWidget, geometry: QtCore.Qsize, parent: QtWidgets.QWidget) -> windows.SubWindow:
        for i in range(1, 9999):
            window_title = f"Sub Window {i}"
            if not window_title in self.window_titles_opened:
                break 
        win = windows.SubWindow(widget, geometry, parent=parent)
        window_container[window_title] = win
        self.window_titles_opened.append(window_title)


    def _init_workers(self, configs):
        self.instrument_manager: InstrumentManager=configs["instrument_manager"]
        """Initialize all workers in their own threads"""
        # Price Processor Worker
        self._price_process_worker = workers.PriceProcessor(
            configs["instrument_manager"],
            data_processing_config=configs["data_processing_config"]
        )
        price_thread = QtCore.QThread()
        self._worker_threads['price'] = price_thread
        self._price_process_worker.moveToThread(price_thread)
        price_thread.start()
        
        # Websocket Worker
        self._websocket_worker = workers.WebsocketWorker(**configs["websocket_config"])
        ws_thread = QtCore.QThread()
        self._worker_threads['websocket'] = ws_thread
        self._websocket_worker.moveToThread(ws_thread)
        ws_thread.start()
        
        # Surface Engine Worker
        self.surface_engine_worker = workers.SurfaceCalibration(
            **self.window_configs,
            **self.window_configs["surface_construction_config"]
        )
        surface_thread = QtCore.QThread()
        self._worker_threads['surface'] = surface_thread
        self.surface_engine_worker.moveToThread(surface_thread)
        surface_thread.start()
        
        # Connect signals
        self._websocket_worker.update_signal.connect(self._price_process_worker.update)
        self._price_process_worker.processedSig.connect(self.surface_engine_worker.price_process_response)
        
    def _cleanup(self):
        """Clean up all worker threads"""
        for name, thread in self._worker_threads.items():
            worker = getattr(self, f'_{name}_worker', None) or getattr(self, f'{name}_worker', None)
            if worker:
                worker.stop()  # Ensure all workers have a stop method
            thread.quit()
            thread.wait()