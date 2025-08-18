from __future__ import annotations 
from typing import List, Optional, Tuple, Union, Dict, TYPE_CHECKING, Callable
if TYPE_CHECKING:
    from instruments.instruments import Option
    from instruments.utils import InstrumentManager
    from PySide6.QtCore import Signal 
    from custom_widgets import CustomPlotDataItem
    from ..data_classes.classes import Slice
    
    
import pyqtgraph as pg
import time
from . import custom_widgets
from PySide6 import QtCore 

title_dataclass_type_map = {"Skew" : "skew",
                            "Term Structure" : "term"}

