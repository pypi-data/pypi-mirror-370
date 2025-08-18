from __future__ import annotations 
from typing import List, Optional, Tuple, Union, Dict, TYPE_CHECKING, Callable
if TYPE_CHECKING:
    from instruments.instruments import Option, Spot
    from ..graphics_items.GL3DGraphicsItems import GL3DLinePlotDataItem
    from pyqtgraph.opengl.GLGraphicsItem import GLGraphicsItem
    from uuid import uuid4 

from PySide6 import QtCore, QtGui
import numpy as np
import numpy as np
from dataclasses import dataclass, InitVar, field
from PySide6 import QtCore
from ..graphics_items import GL3DAxisItem
from .. import utils
from pprint import pprint   




@dataclass
class ItemLimitContainer:
    axes: str
    item_ids: List[str] = field(init=False, default_factory=list)
    min_sorted: Dict[str, List[float]] = field(init=False, default_factory=dict)
    max_sorted: Dict[str, List[float]] = field(init=False, default_factory=dict)

    min_items: Dict[str, Dict[uuid4, float]] = field(init=False, default_factory=dict)
    max_items: Dict[str, Dict[uuid4, float]] = field(init=False, default_factory=dict)
    
    def __post_init__(self):
        self.min_sorted = {ax : [] for ax in self.axes}
        self.max_sorted = {ax : [] for ax in self.axes}
        self.min_items = {ax : {} for ax in self.axes}
        self.max_items = {ax : {} for ax in self.axes}
        
    def _calculate_limits(self, values):
        if np.any(~np.isnan(values)):
            min, max = np.nanmin(values), np.nanmax(values)
        else:
            min, max = np.inf, -np.inf 
        return [min, max]
        
    def limitsFromAxis(self, axis):
        return self.min_sorted[axis][0], self.max_sorted[axis][-1]
    
    def limits(self):
        return [list(self.limitsFromAxis(idx)) for idx in range(3)]

    def addItem(self, item: GL3DLinePlotDataItem):
        self.item_ids.append(item.id())
        for ax in range(3):
            min_val, max_val = item.dataset.limits_subset[ax]
            self.min_items[ax][item.id()]=min_val
            self.max_items[ax][item.id()]=max_val
            self._sort_limits(ax)

    def _sort_limits(self, axis):
        self.min_sorted[axis]=list(self.min_items[axis].values())
        self.min_sorted[axis].sort()
        self.max_sorted[axis]=list(self.max_items[axis].values())
        self.max_sorted[axis].sort()
    
    def updateAxisFromItem(self, item: GL3DLinePlotDataItem, axis):
        min_val, max_val = item.dataset.limits_subset[axis]
        self.min_items[axis][item.id()]=min_val
        self.max_items[axis][item.id()]=max_val
        self._sort_limits(axis)

    def removeItem(self, internal_id):
        if internal_id in self.item_ids:
            self.item_ids.remove(internal_id)
            del self.min_sorted[internal_id]
            del self.max_sorted[internal_id]
            del self.min_items[internal_id]
            del self.max_items[internal_id]
            
        for ax in range(3):
            self._sort_limits(ax)


@dataclass(slots=True)
class AxisNormaliser:
    axis: str
    axis_str: int
    padding: float
    min: float = field(init=False,default=np.nan)
    max: float = field(init=False,default=np.nan)
    min_UB: float = field(init=False,default=np.nan)
    max_LB: float = field(init=False,default=np.nan)
    
    def limits(self):
        return self.min, self.max
    
    def normalise(self, values):
        return (values - self.min) / (self.max - self.min)
    
    def unnormalise(self, values):
        return values * (self.max - self.min) + self.min
    
    def updateFromItemLimit(self, limit: List[float, float]):
        self.min = limit[0] - self.padding * (limit[1] - limit[0])
        self.max = limit[1] + self.padding * (limit[1] - limit[0])
        self._computeMinUB()
        self._computeMaxLB()
    
    def setMax(self, max):
        self.max = max
        self._computeMaxLB()
    
    def _computeMinUB(self):
        if not np.isnan(self.max):
            d = self.max - self.min
            self.min_UB = self.min + 0.4 * d
            
    def _computeMaxLB(self):
        if not np.isnan(self.min):
            d = self.max - self.min
            self.max_LB = self.max - 0.4 * d

    def checkLimit(self, limit: List[float, float]):
        flag=False
        if limit[0] < self.min or limit[1] > self.min_UB:
            flag=True
        if limit[1] > self.max or limit[0] < self.max_LB:
            flag=True
        return flag
    
    def mask_from_data(self, data):
        return (data >= self.min) & (data <= self.max)
    
        
class ViewBox(QtCore.QObject):
    sigXRangeChanged = QtCore.Signal(QtCore.QObject)
    sigYRangeChanged = QtCore.Signal(QtCore.QObject)
    sigZRangeChanged = QtCore.Signal(QtCore.QObject)
    
    sigViewChanged = QtCore.Signal(QtCore.QObject)

    #sigXNormChanged = QtCore.Signal(AxisNormaliser)
    #sigYNormChanged = QtCore.Signal(AxisNormaliser)
    #sigZNormChanged = QtCore.Signal(AxisNormaliser)

    def __init__(self,
                 norm_dims=None,
                 padding=[0, 0, 0]
                 ):
        super().__init__()
        self.item_limit_container = ItemLimitContainer([idx for idx in range(3)])
        
        if norm_dims is None:
            self.norm_dims = {ax : 1 for ax in range(3)}
        else:
            self.norm_dims = norm_dims
        self.padding=padding
        self._recursive_flag_container={}
        self.axis_normaliser_container = {ax_idx : AxisNormaliser(ax_idx, ax_str, pad_val) for ax_idx, (ax_str, pad_val) in enumerate(zip("xyz", self.padding))}
        self._viewRange = [[0, 0] for _ in range(3)]
        self.addedItems=[]
        self.state={
                    "autoRange" : [True]*3,
                    "aspectLocked" : False,
                    }
        self._idx_str_map = {i : s for i, s in enumerate("xyz")}        
    
    def addItem(self,
                item: GLGraphicsItem,
                ignoreBounds: bool=False
                ):
        if hasattr(item, "type"):
            if item.type=="axis":
                return
        if isinstance(item, GL3DAxisItem.GL3DViewBox):
            getattr(self, f"sig{self._idx_str_map[item.direction].upper()}RangeChanged").connect(item.update_values)
        else:
            if not ignoreBounds and hasattr(item, "setData") and callable(item.setData):
                self._recursive_flag_container[item.id()]=False 
                
                item.linktoView(self)
                self.blockSignals(True)
                self.connect_slot_to_norm_sig(item.id(), item.setDataFromView)
                self.connect_item_to_rangechanged_sig(item)
                self.blockSignals(False)
                self.addedItems.append(item)
                if not ignoreBounds:
                    self._addItemLimitCheck(item)
                item
        return item

    def removeItem(self, item):
        if item in self.addedItems:
            self.addedItems.remove(item)
            self.item_limit_container.removeItem(item)
    
    def normaliseToView(self, x, y, z):
        return [self.axis_normaliser_container[0].normalise(x),
                self.axis_normaliser_container[1].normalise(y),
                self.axis_normaliser_container[2].normalise(z)]
    
    def normaliseToView2(self, x=None, y=None, z=None):
        values_normalised = []
        for idx, arr in enumerate([x, y, z]):
            if not arr is None:
                val_norm = self.axis_normaliser_container[idx].normalise(arr)
                values_normalised.append(val_norm)
        return values_normalised

    def resetNormalisation(self):
        self.axis_normaliser_container = {axis : AxisNormaliser(axis) for axis in range(3)}
        self.item_limit_container = ItemLimitContainer([idx for idx in range(3)])
        
    def updateNormalisation2222222(self, item, pos=None, x=None, y=None, z=None):
        if not pos is None:
            x=pos[:,0]
            y=pos[:,1]
            z=pos[:,2]
        
        for axis, arr in zip(range(3), (x,y,z)):
            self.item_limit_container.updateAxisFromItem(item, axis)
            self._check_view_box_limits(axis, item.id(), ignore_update_signals=True)
    
    def viewRange(self) -> List[List[np.ndarray]]:
        return [vr[:] for vr in self._viewRange] 
    
    def _ProcessLimitUpdate(self, item_id, ax, limits):
        plot_limits = self.axis_normaliser_container[ax]
        plot_limits.updateFromItemLimit(limits)
        self._viewRange[ax][:] = plot_limits.limits()
        self._recursive_flag_container[item_id]=True
        self.sigViewChanged.emit(self)
        self._recursive_flag_container[item_id]=False

    def _check_view_box_limits(self, ax, item_id, ignore_update_signals=False):
        if self.state[]=="OnBoundary":
            item_limits=self.item_limit_container.limitsFromAxis(ax)
            plot_view_item=self.axis_normaliser_container[ax]
            if all((not np.isinf(item_limits).any(),
                    not np.isnan(item_limits).any()
                    )):

                new_limit = plot_view_item.checkLimit(item_limits)
                if new_limit: 
                    self._ProcessLimitUpdate(item_id, ax, item_limits)

    def _addItemLimitCheck(self, item):
        self.item_limit_container.addItem(item)
        for axis in range(3):
            limits = self.item_limit_container.limitsFromAxis(axis)
            self._ProcessLimitUpdate(item.id(), axis, limits)
        
    def _preNormalisation(self, item: GL3DLinePlotDataItem, axis, values):
        self.item_limit_container.updateAxisFromItem(item, axis)
        self._check_view_box_limits(axis, item.id())
            
    def normalise(self, axis, item, values, ignoreBounds=False):
        if not ignoreBounds:
            if not self._recursive_flag_container[item.id()]:
                self._preNormalisation(item, axis, values)
        return self.axis_normaliser_container[axis].normalise(values)

    def connect_slot_to_norm_sig(self, internal_name, slot):
        self._recursive_flag_container[internal_name]=False
        self.blockSignals(True)
        self.sigViewChanged.connect(slot)
        #for ax in "XYZ":
            #getattr(self, f"sig{ax}NormChanged").connect(slot)
        self.blockSignals(False)
        
    def connect_item_to_rangechanged_sig(self, item):
        self._recursive_flag_container[item.id()]=False
        self.blockSignals(True)
        for ax in "XYZ":
            getattr(self, f"sig{ax}RangeChanged").connect(getattr(item, f"update{ax}View"))
        self.blockSignals(False)
    
    def setRange(self, xRange=None, yRange=None, zRange=None):
        if all((xRange is None,
                yRange is None,
                zRange is None)):
            for axis in range(3):
                min_val, max_val = self.item_limit_container.limitsFromAxis(axis)
                getattr(self, f"sig{axis.upper()}RangeChanged").emit(AxisNormaliser(axis, [0,1,2].index(axis), min_val, max_val), self)
            return
        x=False
        if not xRange is None:
            self.axis_normaliser_container[0].updateFromItemLimit(xRange)
            self.updateViewRange(0)
            x=True
            
        y=False
        if not yRange is None:
            self.axis_normaliser_container[1].updateFromItemLimit(yRange)
            self.updateViewRange(1)
            y=True
        
        z=False
        if not zRange is None:
            self.axis_normaliser_container[2].updateFromItemLimit(zRange)
            self.updateViewRange(2)
            z=True
        
        for item in self.addedItems:
            for ax, flag in enumerate((x,y,z)):
                if flag:
                    self.item_limit_container.updateAxisFromItem(item, ax)
        
        self.sigViewChanged.emit(self)
        
    def updateViewRange(self, ax):
        self._viewRange[ax][:]=self.axis_normaliser_container[ax].limits()
        getattr(self, f"sig{self._idx_str_map[ax].upper()}RangeChanged").emit(self)
    
                
    def resetToDataLimits(self):
        for axis in range(3):
            min_val, max_val = self.item_limit_container.limitsFromAxis(axis)
            self.setRange(**{f"{axis}Range": [min_val, max_val]})