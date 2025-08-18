from __future__ import annotations
from typing import List, Optional, Tuple, Union, Dict, TYPE_CHECKING, Callable
if TYPE_CHECKING:
    from pyvol_terminal.terminal.application import Application
    from pyvol_terminal.interfaces.abstract_classes import ABCInterface
    from .workers import ABCCalibrationWorker
    

from PySide6 import QtCore, QtWidgets
import time
from pyvol_terminal.settings import widgets as widgets_settings
import time
from pyqtgraph import opengl

QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps)


class InterfaceWindow1(QtWidgets.QMainWindow):
    aboutToCloseSig = QtCore.Signal(QtWidgets.QMainWindow)
    
    def __init__(self,
                 primary_instrument,
                 calibration_worker: ABCCalibrationWorker,
                 **interface_configs
                 ):
        super().__init__()
        self.primary_instrument=primary_instrument

        widget_class = interface_configs["widget_class"]
        
        self.interface: ABCInterface = widget_class(parent=self, **interface_configs)

        self.calibration_worker=calibration_worker
        self.calibration_worker.calibratedSignal.connect(self.interface.main_view.update_view)

        if not self.calibration_worker.isRunning():
            self.calibration_worker.start_worker()
        
        self._initLayout()
        self.showMaximized()
        
    def _initLayout(self):     
        self.stacked_interfaces = QtWidgets.QStackedLayout()
        self.stacked_interfaces.addWidget(self.interface)

        self.setCentralWidget(QtWidgets.QWidget())
        self.central_layout = QtWidgets.QVBoxLayout()
        self.central_layout.addLayout(self.stacked_interfaces)
        self.centralWidget().setLayout(self.central_layout)
    
    def closeEvent(self, event):
        self.calibration_worker.calibratedSignal.disconnect(self.interface.main_view.update_view)
        self.aboutToCloseSig.emit(self)
        super().closeEvent(event)
        
        
class SubWindow(QtWidgets.QMainWindow):
    def __init__(self, widget, geometry: QtCore.QRect=None, adjustToContents: bool=False, flags=None, **kwargs):
        super().__init__(**kwargs)
        self.setCentralWidget(widget)
        if not geometry is None:
            self.setGeometry(geometry)
        if flags:
            self.setWindowFlags(flags)
        self._adjustToContents = adjustToContents
        if adjustToContents:
            QtCore.QTimer.singleShot(0, self.adjustToContents)
        self.show()
    
    def adjustToContents(self):
        self.adjustSize()
        self.setFixedSize(self.size())

class SubWindowTable(SubWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.adjustWindowToTable()

    def adjustWindowToTable(self):
        width = self.centralWidget().verticalHeader().width() + \
                self.centralWidget().horizontalHeader().length() + \
                self.centralWidget().frameWidth() * 2
        
        height = self.centralWidget().horizontalHeader().height() + \
                 self.centralWidget().verticalHeader().length() + \
                 self.centralWidget().frameWidth() * 2
        self.adjustSize()

