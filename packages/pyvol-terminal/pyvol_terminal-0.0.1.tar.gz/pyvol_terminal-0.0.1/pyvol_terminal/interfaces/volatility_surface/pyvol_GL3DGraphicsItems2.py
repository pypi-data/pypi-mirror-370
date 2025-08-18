from __future__ import annotations 
from typing import List, Optional, Tuple, Union, Dict, TYPE_CHECKING, Callable
import uuid


from ...gl_3D_graphing.graphics_items.GL3DGraphicsItems import (GL3DScatterPlotItem,
                                                                GL3DSurfacePlotItem,
                                                                GL3DLinePlotDataItem,
                                                                GL3DMeshData,
                                                                )
from ...gl_3D_graphing.graphics_items.GL3DGraphicsItemMixin import GL3DGraphicsItemMixin
from ...gl_3D_graphing.graphics_items.GL3DPlotDataItemMixin import BaseGL3DPlotDataItemMixin
import numpy as np
from PySide6 import QtCore, QtGui, QtWidgets
import traceback
from abc import abstractmethod
from pyqtgraph.opengl import MeshData, GLSurfacePlotItem


class ABCPyVolPlotItemMixin(BaseGL3DPlotDataItemMixin):
    def __init__(self, *args, **kwargs):
        self.px_type = kwargs.pop("px_type", None) 
        self.valid_values = kwargs.pop("valid_values", None) 
        
        super().__init__(*args, **kwargs)
         
    @abstractmethod
    def getValues(self):...
    
    @abstractmethod
    def id(self):...
    
    
class PyVolGL3DSurfacePlotItem(ABCPyVolPlotItemMixin, GL3DSurfacePlotItem):
    def __init__(self, *args, **kwds):
        self._internal_id=uuid.uuid4()
        self.colormap = kwds.pop("colormap", None) 
        kwds["shader"] = "shaded"
        #kwds["colors"] = (0.5, 0.5, 1, 1)
        x, y, z, color = kwds.get("x", None), kwds.get("y", None), kwds.get("z", None), kwds.get("color", None)
        super().__init__(*args, **kwds)
        self.setGLOptions('opaque')

        self._meshdata = MeshData()
        self.opts['meshdata'] = self._meshdata
        self.meshDataChanged()
        
        if x is not None or y is not None or z is not None:
            self.setData(x, y, z)

    def setData(self, *args, **kwargs):
        if len(args) >= 4 or "colors" in kwargs or "color" in kwargs:
            return super().setData(*args, **kwargs)
        else:
            if len(args) >= 3:
                z_values = args[2]             
            else:
                z_values = kwargs.get("z")       
            if z_values is not None:
                
                kwargs["colors"] = self.colormap.map(z_values)
                #kwargs["color"]=(0.5, 0.5, 1, 1)
            super().setData(*args, **kwargs)     
            self.valid_values=~np.isnan(self._z).all()
        self.sigPlotChanged.emit(self)

    def id(self):
        return self._internal_id

    def getValues(self):
        return self._x, self._y, self._z
    
    

    
class PyVolGL3DScatterPlotItem(ABCPyVolPlotItemMixin, GL3DScatterPlotItem):
    def __init__(self, *args, **kwargs):
        kwargs["size"] = 5
        self.item_type = None
        self._internal_id=uuid.uuid4()
        self.color=kwargs["color"]
        self.original_setData: Callable=None
        self.dataset = None
        self.valid_values=False
        
        if isinstance(kwargs["color"], str):
            qcolor =  QtGui.QColor(kwargs["color"])
            normalised_rgba = (qcolor.redF(), qcolor.greenF(), qcolor.blueF(), qcolor.alphaF())
            kwargs["color"] = normalised_rgba

        super().__init__(*args, **kwargs)
        
    def setData(self, *args, **kwargs):
        super().setData(*args, **kwargs)
        self.valid_values=True
        self.sigPlotChanged.emit(self)

    def id(self):
        return self._internal_id
    
    def getValues(self):
        return self.pos[:,0], self.pos[:,1], self.pos[:,2]

class PyVolLineItem(ABCPyVolPlotItemMixin, GL3DLinePlotDataItem):
    def __init__(self, px_type=None, *args, **kwargs):
        self.px_type=px_type
        self.item_type = None
        self._internal_id=uuid.uuid4()
        self.dataset = None
        super().__init__(*args, **kwargs)

    def id(self):
        return self._internal_id
    
    def getValues(self):
        return self.pos[:,0], self.pos[:,1], self.pos[:,2]
