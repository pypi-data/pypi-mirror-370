import sys
import traceback
from PySide6 import QtCore, QtWidgets, QtGui
import time
import asyncio
from pyvol_terminal import workers
from pyvol_terminal.settings import widgets
from pyvol_terminal.axis import axis_utils as axis_utils
import time

QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps)


windows = []


def open_new_window(interface_name, interface, config, main_window_collapse_func):
    interface_configs = config["interface_configs"]
    config["interface_configs"] = {interface_name : interface_configs[interface_name]}
    config["main_window_flag"]=False
    config["main_window_collapse_func"]=main_window_collapse_func
    w = SingeWindow(interface_name, interface, **config)
    w.show()
    windows.append(w)

class SingeWindow(QtWidgets.QMainWindow):
    def __init__(self, interface_name, interface, **config):
        super().__init__()
        self.interface_name=interface_name
        self.interface = interface  
        callback_dict = {interface_name : self.null_method} 
        main_window_flag=False
        
        self.settings_main = widgets.WindowSettings(self,
                                                  callback_dict,
                                                  main_window_flag=main_window_flag,
                                                  configs=config,
                                                  open_new_window=config["open_new_window"],
                                                  main_window_collapse_func=config["main_window_collapse_func"])
        self.initUI()
        self.showMaximized()
        
    def initUI(self):        
        self.setWindowTitle('PyVol Surface')
        self.widget_main = QtWidgets.QWidget()
        self.layout_main = QtWidgets.QVBoxLayout()
        self.setCentralWidget(self.widget_main)

        self.widget_main.setLayout(self.layout_main)
        self.layout_main.addWidget(self.settings_main)
        
        self.layout_interfaces = QtWidgets.QStackedLayout()
        self.layout_main.addLayout(self.layout_interfaces)
        
        self.layout_interfaces.addWidget(self.interface)
        self.layout_interfaces.setCurrentIndex(0)        
        
        
    def null_method(self):
        pass

    def create_interface_switch_callback_dict(self, interfaces):
        callback_dict = {}
        for interface_name, interface in interfaces.items():
            callback_dict[interface_name] = [self.interface_switch]
        return callback_dict    


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, **config):
        super().__init__()
        instrument_manager=config["instrument_manager"]
        interface_configs = config["interface_configs"]
        self.market_data_worker = config["market_data_worker"]
        self.price_process_worker = config["price_process_worker"]
        self.timer_update_plot = config["plotting_config"]["timer_update_plot"]
        
        self.last_plot_update = time.time()
        self.interfaces={}
        self.worker_slots={}
        main_window_collapse_func = config.get("main_window_collapse_func", None)

        
        interface_classes={}
        
        for idx, (name, inner_dict) in enumerate(interface_configs.items()):
            interface_classes[name] = inner_dict["interface_class"]
            if idx == 0:
                self.current_interface = name
                self.current_interface_name = name
        
        self.initInterfaces(interface_configs, instrument_manager)
        callback_dict = self.create_interface_switch_callback_dict(self.interfaces)
        for interface_name, interface in self.interfaces.items():
            self.worker_slots[interface_name] = interface.update_interface
        
        self.option_name_slot_map = {"Create New Window" : self.app.open}
        
        
        self.settings_main = widgets.WindowSettings(self,
                                                    self.interfaces,
                                                    configs=config,
                                                    open_new_window=config["open_new_window"],
                                                    main_window_collapse_func=main_window_collapse_func
                                                    )
        
        self.price_process_worker.update_interface_signal.connect(self.current_interface.update_interface)
        
        self.initUI()
        self.showMaximized()

    def create_interface_switch_callback_dict(self, interfaces):
        callback_dict = {}
        for interface_name, interface in interfaces.items():
            callback_dict[interface_name] = [self.interface_switch]
        return callback_dict    
    
    def initInterfaces(self, interface_configs, instrument_manager):
        self.interfaces={}
        self.idx_to_interface_name = {}
        self.interface_name_to_idx = {}
        self.current_interface_idx = 0
        for idx, (interface_name, interface_config) in enumerate(interface_configs.items()):
            interface_class = interface_config["interface_class"]
            interface = interface_class(instrument_manager=instrument_manager, **interface_config)
            self.interfaces[interface_name] = interface
            
            if interface_name == self.current_interface_name:
                self.current_interface = interface

            self.idx_to_interface_name[idx] = interface_name
            self.interface_name_to_idx[interface_name] = idx

    def initUI(self):        
        self.setWindowTitle('PyVol Surface')
        self.widget_main = QtWidgets.QWidget()
        self.layout_main = QtWidgets.QVBoxLayout()
        self.setCentralWidget(self.widget_main)

        self.widget_main.setLayout(self.layout_main)
        self.layout_main.addWidget(self.settings_main)
        
        self.layout_interfaces = QtWidgets.QStackedLayout()
        self.layout_main.addLayout(self.layout_interfaces)
        
        for interface in self.interfaces.values():
            self.layout_interfaces.addWidget(interface)
        
        self.layout_interfaces.setCurrentIndex(self.current_interface_idx)        
        

    def interface_switch(self, interface_name):
        prev_interface = self.current_interface
        
        self.current_interface_idx = self.interface_name_to_idx[interface_name]
        self.current_interface = self.interfaces[interface_name]
        self.layout_interfaces.setCurrentIndex(self.current_interface_idx)
        self.price_process_worker.update_interface_signal.disconnect(prev_interface.update_interface)
        self.price_process_worker.update_interface_signal.connect(self.current_interface.update_interface)

    def closeEvent(self, event):
        self.price_process_worker.update_interface_signal.disconnect(self.current_interface.update_interface)
        #loop = asyncio.get_event_loop()
        #loop.run_until_complete(loop.shutdown_asyncgens()) 
        event.accept()
    
    
def display(**config):
    app = QtWidgets.QApplication(sys.argv)
    
    websocket_config=config["websocket_config"]
    instrument_manager=config["instrument_manager"]
    data_processing_config=config["data_processing_config"]
    config["open_new_window"]=open_new_window

    price_process_worker = workers.PriceProcessor(instrument_manager,
                                                  data_processing_config=data_processing_config,
                                                  timer_update_plot=config["plotting_config"]["timer_update_plot"]
                                                  )
    market_data_worker = workers.WebsocketWorker(**websocket_config)
    market_data_worker.update_signal.connect(price_process_worker.update)
  
    config["market_data_worker"]=market_data_worker

    config["main_window_flag"]=True
    config["price_process_worker"] = price_process_worker
    
    global_font = QtGui.QFont("Neue Haas Grotesk")
    app.setFont(global_font)
    mainWin = MainWindow(**config)
    mainWin.show()
    windows.append(mainWin)
    market_data_worker.start()
    
    sys.exit(app.exec())
    