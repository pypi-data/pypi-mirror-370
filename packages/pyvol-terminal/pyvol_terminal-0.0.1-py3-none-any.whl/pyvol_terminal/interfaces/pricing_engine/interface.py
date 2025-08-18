from __future__ import annotations 
from typing import List, Optional, Tuple, Union, Dict, TYPE_CHECKING, Callable
if TYPE_CHECKING:
    from ...data_classes.classes import AbstractDataClass, VolatilityData, VolVector, Surface, Points, Slice
    from instruments.utils import InstrumentManager
    from instruments.instruments import Spot, Option, Future

from PySide6 import QtWidgets, QtCore
from pyvol_terminal.settings import utils as settings_utils
from datetime import datetime
import numpy as np
from PySide6.QtCore import Qt
import QuantLib as ql
from pyvol_terminal.data_classes import builders as builders_data_classes
from ...quantities import engines
import math
from .main_view import MainView
from .settings import Settings


class Interface(QtWidgets.QWidget):
    def __init__(self,
                 instrument_manager: InstrumentManager=None,
                 data_container=None,
                 tick_engine_manager=None,
                 **kwargs):
        super().__init__()
        
        
        self.data_view = MainView(instrument_manager, data_container, tick_engine_manager, **kwargs)
        self.settings = Settings(self.data_view)
        
        
    
    def _initLayout(self):
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().addWidget(self.settings)
        self.layout().addWidget(self.data_view)

        
