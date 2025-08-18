from __future__ import annotations 
from typing import List, Optional, Tuple, Union, Dict, TYPE_CHECKING, Callable, Any
if TYPE_CHECKING:
    from ...instruments.utils import InstrumentManager
    from ...quantities.engines import TickEngineManager
    from ...instruments.instruments import Option
    from PySide6.QtCore import Signal 
    from custom_widgets import CustomPlotDataItem
    from ...data_classes.classes import Slice

from PySide6.QtWidgets import (QMainWindow, QWidget, QDockWidget, QSplitter, 
                              QVBoxLayout, QLabel, QApplication, QWidget)

from PySide6.QtCore import Qt
from PySide6 import QtCore
from . import axis_widgets  
from .. import subplot
import pyqtgraph as pg
from .. import custom_widgets
import time

class SplitDockWidget(QDockWidget):
    __AXIS_DEPENDENCE__ ="xy"

    
    def __init__(self,
                 *,
                 tick_engine_manager: TickEngineManager=None,
                 **kwargs
                 ):
        super().__init__(**kwargs)   
        print(f"\n\n\nSplitDockWidget")
        print(f"tick_engine_manager.get_engine: {tick_engine_manager.get_engine}")
        print(f"\n\n\n")
        self._dclass_name_subplot_title_map: Dict[str, str]={"skew" : "Skew",
                                                             "term" : "Term Structure"
                                                             }
        
        self._initLayout()
        self._initSubplots(self._dclass_name_subplot_title_map.values(), tick_engine_manager)
        
        
    
    def _initSubplots(self,
                      subplot_names: List[str],
                      tick_engine_manager: TickEngineManager=None,
                      ):
        
        x_ax_2D = axis_widgets.CustomAxisItem(axis_direction=0,
                                              tick_engine=tick_engine_manager.get_engine("x") if tick_engine_manager is not None else None,
                                              orientation="bottom"
                                              )
        y_ax_2D = axis_widgets.CustomAxisItem(axis_direction=1,
                                              tick_engine=tick_engine_manager.get_engine("y") if tick_engine_manager is not None else None,
                                              orientation="bottom")
        z_ax_2D = axis_widgets.CustomAxisItem( axis_direction=2,
                                              tick_engine=tick_engine_manager.get_engine("z") if tick_engine_manager is not None else None,
                                              orientation="right") 
        zz_ax_2D = axis_widgets.CustomAxisItem(axis_direction=2,
                                               tick_engine=tick_engine_manager.get_engine("z") if tick_engine_manager is not None else None,
                                               orientation="right") 
        
        axes_2D_items = [x_ax_2D, y_ax_2D, z_ax_2D, zz_ax_2D]
        
        
        splitter: QSplitter = self.widget().layout().itemAt(0).widget()
        
        for i, (title, axis) in enumerate(zip(subplot_names, SplitDockWidget.__AXIS_DEPENDENCE__)):
            tick_engine = tick_engine_manager.get_engine(SplitDockWidget.__AXIS_DEPENDENCE__[-i-1])
            axisItems={"bottom" : axes_2D_items[i],
                       "right"   : axes_2D_items[i+2]
                       }
            subplot_item = SubPlotItem(title=title,
                                        axis_3D_dir=axis,
                                        other_axis_tick_engine=tick_engine,
                                        axisItems=axisItems
                                        )
            subplot_widget = pg.PlotWidget(plotItem=subplot_item)
            splitter.addWidget(subplot_widget)

    def _initLayout(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        splitter = QSplitter(Qt.Vertical)
        layout.addWidget(splitter)
        container.setLayout(layout)
        self.setWidget(container)



class SubPlotItem(pg.PlotItem):
    def __init__(self,
                 axis_3D_dir: str,
                 other_axis_tick_engine=None,
                 *args,
                 **kwargs
                 ):
        super().__init__(*args, **kwargs)
        self._axisSlice = 0 if axis_3D_dir=="x" else 1
        self.interacting=False
        self.setAcceptHoverEvents(True)
        self.axis_3D_directions=axis_3D_dir
        self.other_axis_tick_engine=other_axis_tick_engine
        self._other_axis_direction = "x" if axis_3D_dir == "yz" else "y"
        self._plotDataItemContainer: Dict[str, CustomPlotDataItem]={}
        self._dataclassContainer: Dict[str, Slice]={}
        self.show_text=False
        self.prev_x=None
        self.prev_y=None
        self.interacting=False
        self.other_axis_textitem = custom_widgets.CustomTextItem(text="",
                                                                 view_box_anchor=(1, 0),
                                                                 color=(0, 0, 0, 255),
                                                                 fill=pg.mkBrush(255, 255, 255, 200),
                                                                 anchor=(1, 0)
                                                                 ) 
        self.other_axis_textitem.attach_viewbox(self.getViewBox())
        self.other_axis_textitem.hide()
        self.addItem(self.other_axis_textitem)
        
        self.getViewBox().setAutoVisible(x=False, y=False)
        self.getViewBox().setBackgroundColor("k")
    
    def axisSlice(self):
            return self._axisSlice
    
        
    def hoverLeaveEvent(self, event):
        self.interacting=False
        super().hoverLeaveEvent(event)

    def sceneEventFilter(self, watched, event):
        if event.type() == QtCore.QEvent.GraphicsSceneMousePress\
            or event.type() == QtCore.QEvent.GraphicsSceneMouseMove\
            or event.type() == QtCore.QEvent.GraphicsSceneMouseRelease\
            or event.type() ==  QtCore.QEvent.GraphicsSceneWheel:
                
            self.interacting=True
        return super().sceneEventFilter(watched, event)
        
    def addItem(self, item):
        if isinstance(item, custom_widgets.CustomPlotDataItem):
            self._plotDataItemContainer[item.px_type] = item
        super().addItem(item)
        
    def removeItem(self, item):
        if isinstance(item, custom_widgets.CustomPlotDataItem):
            del self._plotDataItemContainer[item.px_type]
        super().removeItem(item)
        del item
        
    def setParentItem(self, parent):
        super().setParentItem(parent)
        if not parent is None:
            if self.width() > 0:
                self.other_axis_textitem.setPos(self.width(), 0)

    def mousePressEvent(self, ev):
        self.interacting=True
        return super().mousePressEvent(ev)
    
    def mouseReleaseEvent(self, ev):
        self.interacting=False
        return super().mouseReleaseEvent(ev)
    
    def listPricePlotDataItem(self):
        return list(self._plotDataItemContainer.values())
    
    def pricePlotDataItem(self, px_type):
        return self._plotDataItemContainer[px_type]
    
    def set_text(self, x, y):
        values = locals()[self._other_axis_direction]
        text = self.other_axis_tick_engine.function([values])[0]
        text = f"{self.other_axis_tick_engine.get_label()}: {text}"
        self.other_axis_textitem.setPlainText(text)
    
    def addDataClass(self,
                     name: str,
                     dataclass_item: Slice
                     ):
        self._dataclassContainer[name]=dataclass_item
    
    def removeDataClass(self, name: str):
        del self._dataclassContainer[name]
    
    def dataClass(self, name):
        return self._dataclassContainer.get(name, None)    
    
    def plotFromDataClass(self, dataclass: Slice, **kwargs) -> CustomPlotDataItem:
        if dataclass.valid_values:
            kwargs.update(dataclass.plot_item_kwargs())
        else:
            kwargs.update({"x" : [], "y" : []})

        plot_data_item = custom_widgets.CustomPlotDataItem(**kwargs)
        dataclass.add_update_callback(plot_data_item.update_from_dataclass)
        
        self.addDataClass(plot_data_item.px_type, dataclass)
        self.addItem(plot_data_item)
        return plot_data_item
    
    def removePricePlotDataItem(self, px_type: str) -> None:
        plot_data_item = self.pricePlotDataItem(px_type)
        dataclass = self.dataClass(px_type)
        dataclass.remove_update_callback(plot_data_item.update_from_dataclass)
        
        self.removeDataClass(px_type)
        self.removeItem(plot_data_item)
        
    @QtCore.Slot(float, float, float)
    def update3DMouseClick(self, x, y, z):
        for dataclass in self._dataclassContainer.values():
            dataclass.update_point(x, y, z)
    
    
    