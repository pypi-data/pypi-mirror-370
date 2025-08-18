from __future__ import annotations
from typing import List, Optional, Tuple, Union, Dict, TYPE_CHECKING
if TYPE_CHECKING:
    from ...quantities.engines import TickEngineManager
    from .settings import Settings
    from ..custom_widgets import CustomPlotDataItem
    from .main_view import MainView
    from pyvol_terminal.interfaces.volatility_surface.pyvol_GL3DViewWidget import PyVolGL3DViewWidget
    from .interface import Interface
    
from ...gl_3D_graphing.graphics_items import GL3DAxisItem
from .axes_widgets import PyVolGL3DAxisItem
import pyqtgraph as pg
from .. import custom_widgets
from . import axis_widgets 
from PySide6 import QtCore, QtGui, QtWidgets

       
def initAxis(view_widget: PyVolGL3DViewWidget,
             tick_engine_manager: TickEngineManager,
             ) -> Tuple[List[PyVolGL3DAxisItem], List[axis_widgets.CustomAxisItem]]:

    x_label = "Strike"
    y_label = "Expiry"
    z_label = "Implied Volatility"

    x_ax_3D = [[view_widget.vb.state["worldRange"], 0, (0, 0, 0), 1],
                {"text" : x_label,
                "showValues" : True,
                "valuesColor" : "white",
                "labelColor" : "white",
                "faceTickOffset" : -0.1,
                "syncToView" : True,
                "showGrid" : True,
                "showTickMargin" : True,         
                }
              ]
    
    y_ax_3D = [[view_widget.vb.state["worldRange"], 1, (0, 0, 0), 0],
                {"text" : y_label,
                "showValues" : True,
                "valuesColor" : "yellow",
                "labelColor" : "yellow",
                "faceTickOffset" : -0.1,
                "syncToView" : True,
                "showGrid" : True,
                "showTickMargin" : True,     
                }
               ]

    z_ax_3D = [[view_widget.vb.state["worldRange"], 2, (0, 0, 0), 0],
                {"text" : z_label,
                "showValues" : True,
                "valuesColor" : "cyan",
                "labelColor" : "cyan",
                "faceTickOffset" : -0.1,
                "syncToView" : True,
                "showGrid" : True,
                "showTickMargin" : True,   
                "graphFaceOffset" : -0.3,
                }
               ]
    
    zz_ax_3D = [[view_widget.vb.state["worldRange"], 2, (1, 1, 0), 1],
                {"text" : z_label,
                "showValues" : True,
                "valuesColor" : "cyan",
                "labelColor" : "cyan",
                "faceTickOffset" : -0.1,
                "syncToView" : True,
                "showGrid" : True,
                "showTickMargin" : True,     
                "graphFaceOffset" : -0.3,
                }
               ]
    
    axes_with_ticks = [x_ax_3D, y_ax_3D, z_ax_3D, zz_ax_3D]

    axes_3D_items = [PyVolGL3DAxisItem.fromViewBoxRange(*item[0], **item[1], tick_engine=tick_engine_manager.get_engine(ax)) for ax, item in zip("xyzz", axes_with_ticks)]
    
    xn_ax_3D = [[view_widget.vb.state["worldRange"], 0, (0, 0, 0), 2],
                {"text" : z_label,
                "showValues" : False,
                "faceTickOffset" : -0.1,
                "syncToView" : True,
                "showGrid" : True,
                "showTickMargin" : True,   
                "showLabel" : False,
                "graphFaceOffset" : -0.3,
                }
                ]
    
    yn_ax_3D = [[view_widget.vb.state["worldRange"], 1, (1, 1, 0), 2],
                {"text" : z_label,
                "showValues" : False,
                "faceTickOffset" : -0.1,
                "syncToView" : True,
                "showGrid" : True,
                "showTickMargin" : True,     
                "showLabel" : False,
                "graphFaceOffset" : -0.3,
                }
                ]
    
    axes_no_ticks = [xn_ax_3D,yn_ax_3D]
    
    axes_3D_items = axes_3D_items + [PyVolGL3DAxisItem.fromViewBoxRange(*item[0], **item[1]) for item in axes_no_ticks]
    
    return axes_3D_items

