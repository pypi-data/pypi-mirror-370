from __future__ import annotations 
from typing import List, Optional, Tuple, Union, Dict, TYPE_CHECKING, Callable
if TYPE_CHECKING:
    from instruments.instruments import Option, Spot
    from ..graphics_items.GL3DGraphicsItems import GlPlotItemMixin
    from pyqtgraph.opengl.GLGraphicsItem import GLGraphicsItem

from PySide6 import QtCore, QtGui
import numpy as np
import numpy as np
from dataclasses import dataclass, InitVar, field
from PySide6 import QtCore
from ..graphics_items import GL3DAxisItem
from .. import utils
from pprint import pprint   
from pyqtgraph import opengl

@dataclass(slots=True)
class PlotView:
    axis: str
    axis_idx: int
    min: float = np.nan
    max: float = np.nan
    min_UB: float = np.nan
    max_LB: float = np.nan
    
    
    def normalise(self, values):
        return (values - self.min) / (self.max - self.min)
    
    def unnormalise(self, values):
        return values * (self.max - self.min) + self.min
    
    def update_min(self, min):
        self.min = min
        self._get_min_UB()
    
    def update_max(self, max):
        self.max = max
        self._get_max_LB()
    
    def _get_min_UB(self):
        if not np.isnan(self.max):
            d = self.max - self.min
            self.min_UB = self.min + 0.4 * d
            
    def _get_max_LB(self):
        if not np.isnan(self.min):
            d = self.max - self.min
            self.max_LB = self.max - 0.4 * d

    def is_new_limit(self, limit_type, value):
        if np.isnan(getattr(self, limit_type)):
            return True
        else:
            if limit_type == "min":
                if np.isnan(self.min_UB) and not np.isnan(self.max):
                    self._get_min_UB()
                if value < self.min or value > self.min_UB:
                    return True
                else:
                    return False
            else:
                if np.isnan(self.max_LB) and not np.isnan(self.min):
                    self._get_max_LB()
                if value > self.max or value < self.max_LB:
                    return True
                else:
                    return False
    
    def mask_from_data(self, data):
        return (data >= self.min) & (data <= self.max)

    
    
    
    
class CustomGLGraphicsItem(opengl.GLGraphicsItem.GLGraphicsItem):
    def __init__(self, *args, **kwargs):
        self.__children=[]
        super().__init__(*args, **kwargs)

    def addChildItem(self, item):
        self.__children.append(item)
        
    def childItems(self):
        return list(self.__children)
    


class ViewBox(CustomGLGraphicsItem):
    sigXRangeChanged = QtCore.Signal(float, float)
    sigYRangeChanged = QtCore.Signal(float, float)
    sigZRangeChanged = QtCore.Signal(float, float)

    
    def __init__(self,
                 norm_dims=[1,1,1],
                 padding=0.1,
                 *args, **kwargs):
        self.norm_dims=norm_dims
        self.padding=padding*np.array(norm_dims)
        self.min_vals, self.max_vals = None, None
        self.vb_min, self.vb_max = None, None
        self.viewRange = [[0, 1] for _ in range(3)]
        self.transform_matrix=None
        super().__init__(*args, **kwargs)
    
    def addChildItem(self, item):
        super().addChildItem(item)
        if hasattr(item, "linktoView"):
            item.linktoView(self)
        self.normalize_scene()
        item.setTransform(self.transform_matrix)
    
    def transformChildItems(self):
        for child in self.childItems():
            child.setTransform(self.transform_matrix)


    def normalize_scene(self):
        min_vals, max_vals = utils.compute_scene_bbox(self.childItems())
        if self.min_vals is None or any(min_vals < self.vb_min) or any(max_vals > self.vb_max):
            self.min_vals = min_vals
            self.max_vals = max_vals
            self.vb_min = min_vals - self.padding
            self.vb_max = max_vals + self.padding
            
            self.viewRange[0] = [self.vb_min[0], self.vb_max[0]]
            self.viewRange[1] = [self.vb_min[1], self.vb_max[1]]
            self.viewRange[2] = [self.vb_min[2], self.vb_max[2]]

            self.createTransformMatrix()
            self.transformChildItems()

    def setRange(self, xRange=None, yRange=None, zRange=None, padding=None):
        if all((xRange is None,
                yRange is None,
                zRange is None)):
            return 
        x,y,z=[False]*3
        
        if not xRange is None:
            x=True
            self.vb_min[0], self.vb_max[0] = xRange[0], xRange[1]
            self.viewRange[0]=xRange
            self.sigXRangeChanged.emit(*xRange)
            
                

        if not yRange is None:
            y=True
            self.vb_min[1], self.vb_max[1] = yRange[0], yRange[1]
            self.viewRange[1]=yRange
            self.sigYRangeChanged.emit(*yRange)
            
        
        if not zRange is None:
            z=True
            self.vb_min[2], self.vb_max[2] = zRange[0], zRange[1]
            self.viewRange[2]=zRange
            self.sigZRangeChanged.emit(*zRange)
            
        self.createTransformMatrix()
        
        for child in self.childItems():
            if hasattr(child, "filter_data"):
                child.filter_data(self)
            else:
                print(child)
                print(child.childItems())
            child.setTransform(self.transform_matrix)

    def createTransformMatrix(self):
        ranges = self.vb_max - self.vb_min
        ranges[ranges == 0] = 1.0
        
        self.transform_matrix = QtGui.QMatrix4x4()

        self.transform_matrix.scale(1/ranges[0], 1/ranges[1], 1/ranges[2])
        self.transform_matrix.translate(-self.vb_min[0], -self.vb_min[1], -self.vb_min[2])
