from __future__ import annotations 
from typing import List, Optional, Tuple, Union, Dict, TYPE_CHECKING, Callable, Any
if TYPE_CHECKING:
    from instruments.instruments import Option
    from instruments.utils import InstrumentManager
    
import pyqtgraph.opengl as gl
import numpy as np
from PySide6 import QtGui, QtCore
import uuid

class GlPlotItemMixin:
    sigPlotChanged = QtCore.Signal(object)
    
    def __init__(self, px_type, type, *args, **kwargs):
        self.px_type=px_type
        self.item_type=type
        self._internal_id=uuid.uuid4()
        self.color=kwargs["color"]
        self.original_setData: Callable=None
        self.dataset = PlotDataset(real_all)
        
        if isinstance(kwargs["color"], str):
            qcolor =  QtGui.QColor(kwargs["color"])
            normalised_rgba = (qcolor.redF(), qcolor.greenF(), qcolor.blueF(), qcolor.alphaF())
            kwargs["color"] = normalised_rgba
        super().__init__(*args, **kwargs)

    def setData(self, *args, **kwargs):
        super().setData(*args, **kwargs)
        self.sigPlotChanged.emit(self)

    def id(self):
        return self._internal_id
    
class glSurface(GlPlotItemMixin, gl.GLSurfacePlotItem):
    def __init__(self, px_type, colormap, color, *args, **kwargs):
        kwargs["shader"] = "shaded"
        self.colormap=colormap
        self.color=color
        self.init=True
        kwargs["color"]=color
        kwargs["colors"]=colormap.map(kwargs["z"])
        self.valid_values=False
        super().__init__(px_type, "surface", *args, **kwargs)
        self.setGLOptions('opaque')
    
    def setData(self, *args, **kwargs):
        if len(args) >= 4 or "colors" in kwargs:
            return super().setData(*args, **kwargs)
        else:
            if len(args) >= 3:
                z_values = args[2]             
            else:
                z_values = kwargs.get("z")       
            if z_values is not None:
                kwargs["colors"] = self.colormap.map(z_values)
            super().setData(*args, **kwargs)     
            self.valid_values=~np.isnan(self._z).all()
            
    def getValues(self,):
        return self._x, self._y, self._z
    
class glScatter(GlPlotItemMixin, gl.GLScatterPlotItem):
    def __init__(self, px_type, *args, **kwargs):
        kwargs["size"] = 10
        super().__init__(px_type, "scatter", *args, **kwargs)
        
    def getValues(self):
        return self.pos[:,0], self.pos[:,1], self.pos[:,2]
