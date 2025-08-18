from __future__ import annotations 
from typing import List, Optional, Tuple, Union, Dict, TYPE_CHECKING, Callable
if TYPE_CHECKING:
    from .GL3DViewBox import GL3DViewBox 
    
from pyqtgraph import opengl
from PySide6 import QtWidgets, QtCore, QtGui
import numpy as np
from . import AbstractGLPlotItem
from pyqtgraph.Qt import QT_LIB
import importlib
from .GLGraphicsItem import AbstractGLGraphicsItem
from .AbstractGLPlotItem import AbstractGLPlotItem  


if QT_LIB in ["PyQt5", "PySide2"]:
    QtOpenGL = QtGui
else:
    QtOpenGL = importlib.import_module(f"{QT_LIB}.QtOpenGL")

__all__ = ['GLScatterPlotItem']


opengl.GLScatterPlotItem.__bases__ = (AbstractGLPlotItem,)

class GLScatterPlotItem(opengl.GLScatterPlotItem, AbstractGLPlotItem):        
    sigPlotChanged = QtCore.Signal(object)       
    def __init__(self, parentItem=None, **kwds):
        print(f"inti: {kwds}")
        AbstractGLPlotItem.__init__(self, **kwds)
        glopts = kwds.pop('glOptions', 'additive')
        self.setGLOptions(glopts)
        self.pos = None
        self.size = 10
        self.color = [1.0,1.0,1.0,0.5]
        self.pxMode = True

        self.m_vbo_position = QtOpenGL.QOpenGLBuffer(QtOpenGL.QOpenGLBuffer.Type.VertexBuffer)
        self.m_vbo_color = QtOpenGL.QOpenGLBuffer(QtOpenGL.QOpenGLBuffer.Type.VertexBuffer)
        self.m_vbo_size = QtOpenGL.QOpenGLBuffer(QtOpenGL.QOpenGLBuffer.Type.VertexBuffer)
        self.vbos_uploaded = False
        self.setData = AbstractGLPlotItem.setData.__get__(self, type(self))  
        self.setParentItem(parentItem)
        self.setData(**kwds)

    def _internal_update(self):
        return opengl.GLScatterPlotItem.update()
    
        
    def dataBounds(self,
                   ax: int,
                   frac=(1,1),
                   orthoRange=None
                   ) -> Tuple[float, float, float]:

        if not self.visible() or self._dataset is None:
            return None, None
        else:
            
            if frac >= 1.0 and orthoRange is None and not self._boundsCache[ax] is None:
                return self._boundsCache[ax]
            data = self._dataset.data()
            if data is None:
                return None, None
            if orthoRange is None:
                mask = ~np.isnan(data[ax])
            else:
                mask = (data[ax] >= orthoRange[0]) & (data[ax] <= orthoRange[1])
            data = data[ax][mask]
            self._boundsCache[ax] = [np.nanmin(data), np.nanmax(data)]
            
            return self._boundsCache[ax]
    
    
    def _setDataHelper(self, pos=None, color=None):
        print(f"\n_setDataInternal\n")
        kwargs={}
        if pos is None:
            #self._dataset=None
            if color is None:
                opengl.GLScatterPlotItem.setData(self, color=color)
                return 
        else:
            self._dataset = self.plotdataset_cls(pos[:,0], pos[:,1], pos[:,2])
            #self._dataset.update(pos)
            #self._dataset = PlotDataset(pos[:,0], pos[:,1], pos[:,2])
            self._datasetDisplay = self._getDisplayDataset()
            kwargs["pos"] = self._datasetDisplay.data()
        if not color is None:
            kwargs["color"]=color
        

        #self.blockUpdate(True)
        print(kwargs)
        opengl.GLScatterPlotItem.setData(self, **kwargs)
        #elf.blockUpdate(False)
        self.sigPlotChanged.emit(self)
        
        print(f"self.pos: {self.pos}")
        
        

    def clipDataFromVRange(self, view_range, x, y, z):
        print(f"view_range: {view_range}")
        clipped_dataset=np.column_stack((x, y, z))
        for ax in range(3):
            mask = (view_range[ax][0] <= clipped_dataset[:, ax]) & (clipped_dataset[:, ax] <= view_range[ax][1])
            clipped_dataset = clipped_dataset[mask]
        return clipped_dataset[:, 0], clipped_dataset[:, 1], clipped_dataset[:,2]


