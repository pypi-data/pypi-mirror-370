from __future__ import annotations
from typing import List, Optional, Tuple, Union, Dict, TYPE_CHECKING, Callable
if TYPE_CHECKING:
    from pyvol_terminal.terminal.application import Application
    from pyvol_terminal.interfaces.abstract_classes import ABCInterface

from PySide6 import QtCore, QtWidgets
import time
from pyvol_terminal.settings import widgets as widgets_settings
import time

QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, app: Application, **config):
        super().__init__()
        self.app=app
        interface_configs = config["interface_configs"]

        self.last_plot_update = time.time()
        self.interfaces={}
        
        interface_classes={}
        for idx, (name, inner_dict) in enumerate(interface_configs.items()):
            interface_classes[name] = inner_dict["interface_class"]
        
        self.interface_name_slot_map = {}
                
        self._initInterfaces(interface_configs, config)
        
        self.settings_main = widgets_settings.WindowSettings([self.app.open_main_window],
                                                             self.interface_name_slot_map)
        self._initLayout()
        
        self.settings_main.toggle_price_type(name=list(interface_classes.keys())[0])
        
    def _initInterfaces(self, interface_configs, extra_configs):
        self.interfaces={}
        self.stacked_interfaces = QtWidgets.QStackedLayout()
        for interface_name, interface_config in interface_configs.items():
            interface_class = interface_config["interface_class"]
            interface: ABCInterface = interface_class(parent=self, **interface_config, **extra_configs)
            self.app.surface_engine_worker.calibratedSignal.connect(interface.main_view.update_view)
            self.interfaces[interface_name] = interface
            self.stacked_interfaces.addWidget(interface)
            self.interface_name_slot_map[interface_name] = [lambda id, checked: self.stacked_interfaces.setCurrentIndex(id-1) if checked else None]
            
            
    def _initLayout(self):     
        self.setCentralWidget(QtWidgets.QWidget())
        self.central_layout = QtWidgets.QVBoxLayout()
        self.central_layout.addWidget(self.settings_main)
        self.central_layout.addLayout(self.stacked_interfaces)
        self.centralWidget().setLayout(self.central_layout)
    
    def closeEvent(self, event):
        #self.price_process_worker.update_interface_signal.disconnect(self.current_interface.update_interface)
        #loop = asyncio.get_event_loop()
        #loop.run_nutil_complete(loop.shutdown_asyncgens()) 
        event.accept()

        
class SubWindow(QtWidgets.QMainWindow):
    def __init__(self, widget, geometry: QtCore.Qsize, **kwargs):
        super().__init__(**kwargs)
        self.setCentralWidget(widget)
        self.setGeometry(geometry)
        self.show()
        
        
        
         