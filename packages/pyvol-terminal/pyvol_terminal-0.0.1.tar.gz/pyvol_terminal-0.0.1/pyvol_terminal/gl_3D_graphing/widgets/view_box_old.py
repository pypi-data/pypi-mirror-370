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
        
        
class ViewBox(QtCore.QObject):
    sigXRangeChanged = QtCore.Signal(PlotView, QtCore.QObject)
    sigYRangeChanged = QtCore.Signal(PlotView, QtCore.QObject)
    sigZRangeChanged = QtCore.Signal(PlotView, QtCore.QObject)

    sigXNormChanged = QtCore.Signal(PlotView)
    sigYNormChanged = QtCore.Signal(PlotView)
    sigZNormChanged = QtCore.Signal(PlotView)

    def __init__(self, norm_dims=None, padding=None):
        super().__init__()
        self.norm_dims=norm_dims
        self.item_limit_engine = utils.ItemSetLimits("xyz")
        self.require_normalise=False
        if norm_dims is None:
            self.norm_dims = {ax : 1 for ax in range(3)}
        else:
            self.norm_dims = norm_dims

        if padding is None:
            self.padding = {ax : 0 for ax in range(3)}
        else:
            self.padding = padding
        self._item_limits={}
        self._item_internal_normalise_name_map={}
        self.overall_item_limits=self._get_null_limits()
        self._normalise_flags={}
        self.plot_views = {axis : PlotView(axis, idx) for idx, axis in enumerate(range(3))}
        self.viewRange = [[0, 0] for _ in range(3)]
        self.tt=[]
        self.addedItems=[]
        
    
    def addItem(self,
                item: GLGraphicsItem,
                ignoreBounds: bool=False
                ):
        if hasattr(item, "type"):
            if item.type=="axis":
                return
        if isinstance(item, GL3DAxisItem.GL3DViewBox):
            getattr(self, f"sig{item.axis_direction.upper()}RangeChanged").connect(item.update_values)
        else:
            if not ignoreBounds and hasattr(item, "setData") and callable(item.setData):
                original_setData = item.setData
                item.original_setData=original_setData
                
                self._normalise_flags[item.id()]=False 
                if not ignoreBounds:
                    self._add_item_check_limits(item)
                
          
                    
                def _normalise_setData_pos_wrapper(*inner_args, **inner_kwargs):
                    return utils.normalise_setData_pos(item, self, ignoreBounds, *inner_args, **inner_kwargs)
                
                def _renormalise_data_pos_wrapper(plot_view):
                    return utils.renormalise_data_pos(item, plot_view)
                
                def _filter_data_pos_wrapper(plot_view):
                    return utils.filter_data_pos(item, plot_view)

                def _normalise_setData_xyz_wrapper(*inner_args, **inner_kwargs):
                    return utils.normalise_setData_xyz(item, self, ignoreBounds, *inner_args, **inner_kwargs)
                
                def _renormalise_data_xyz_wrapper(plot_view):
                    return utils.renormalise_data_xyz(item, plot_view)
                
                def _filter_data_xyz_wrapper(plot_view):
                    return utils.filter_data_xyz(item, plot_view, self)
                
                if hasattr(item, "pos"):
                    item.setData = _normalise_setData_pos_wrapper
               #     item.renormalise_data = _renormalise_data_pos_wrapper
                   # item.filter_data = _filter_data_pos_wrapper
                    item.unnorm_pos=item.pos.copy()
                    setData_kwargs = {"pos" : item.pos}

                elif hasattr(item, "_x") and hasattr(item, "_y") and hasattr(item, "_z"):
                  #  item.unnorm_x, item.unnorm_y, item.unnorm_z = item._x.copy(), item._y.copy(), item._z.copy()
                #    item._all_x, item._all_y, item._all_z = item._x.copy(), item._y.copy(), item._z.copy()
              #      item.unnorm_pos = np.column_stack((item.unnorm_x, item.unnorm_y, item.unnorm_z))
                    item.setData = _normalise_setData_xyz_wrapper
               #     item.renormalise_data = _renormalise_data_xyz_wrapper   
                  #  item.filter_data = _filter_data_xyz_wrapper
                    setData_kwargs = {"x":item._x, "y":item._y, "z":item._z}
                
                self.blockSignals(True)
                self.connect_slot_to_norm_sig(item, item.renormalise_data)
                self.connect_slot_to_rangechanged_sig(item, item.filter_data)
                self.blockSignals(False)
                item.setData(**setData_kwargs)
                self.addedItems.append(item)
        return item

    def removeItem(self, item):
        if item in self.addedItems:
            self.addedItems.remove(item)
            
    
    def reset_normalisation(self):
        self.plot_views = {axis : PlotView(axis) for axis in range(3)}
        self.item_limit_engine = utils.ItemSetLimits("xyz")
        
    def update_normalisation(self, item, pos=None, x=None, y=None, z=None):
        if not pos is None:
            x=pos[:,0]
            y=pos[:,1]
            z=pos[:,2]
        
        for axis, arr in zip(range(3), (x,y,z)):
            self.item_limit_engine.update_item_limits(item, axis, arr)
            self._check_view_box_limits(axis, item.id(), ignore_update_signals=True)
    
    def update_plot_view(self, plot_view):
        self.viewRange[plot_view.axis_idx][0] = plot_view.min
        self.viewRange[plot_view.axis_idx][1] = plot_view.max

        getattr(self, f"sig{plot_view.axis.upper()}RangeChanged").emit(plot_view.axis, self)

    def _check_view_box_limits(self, ax, item_id, ignore_update_signals=False):
        print(f"\n_check_view_box_limits")
        limits=self.item_limit_engine.get_limit_values(ax)
        plot_view=self.plot_views[ax]
        for limit, limit_type in zip(limits, ["min", "max"]):
            if limit != np.inf:
                if plot_view.is_new_limit(limit_type, limit):
                    self.require_normalise=True
                    padding = - self.padding[ax] if limit_type == "min" else self.padding[ax]
                    getattr(plot_view, f"update_{limit_type}")(limit + padding*limit)
                    
        self.viewRange[plot_view.axis_idx][0] = plot_view.min
        self.viewRange[plot_view.axis_idx][1] = plot_view.max
        pprint(self.viewRange)
        if self.require_normalise and not ignore_update_signals:
            self.require_normalise=False
            self._normalise_flags[item_id]=True
            #getattr(self, f"sig{ax.upper()}RangeChanged").emit(plot_view.axis, self)
            getattr(self, f"sig{ax.upper()}NormChanged").emit(plot_view)
            self._normalise_flags[item_id]=False
    
    def _add_item_check_limits(self, item):
        self.item_limit_engine.addItem(item)
        for axis in range(3):
            self._check_view_box_limits(axis, item.id())
        
    def _pre_normalisation(self, item: GlPlotItemMixin, axis, values):
        self.item_limit_engine.update_item_limits(item, axis, values)
        self._check_view_box_limits(axis, item.id())
            
    def normalise(self, axis, item, values, ignoreBounds=False):
        if not ignoreBounds:
            if not self._normalise_flags[item.id()]:
                self._pre_normalisation(item, axis, values)
        return self.plot_views[axis].normalise(values)

    def connect_slot_to_norm_sig(self, internal_name, slot):
        self._normalise_flags[internal_name]=False
        self.blockSignals(True)
        for ax in "XYZ":
            getattr(self, f"sig{ax}NormChanged").connect(slot)
        self.blockSignals(False)
        
    def connect_slot_to_rangechanged_sig(self, internal_name, slot):
        self._normalise_flags[internal_name]=False
        self.blockSignals(True)
        for ax in "XYZ":
            getattr(self, f"sig{ax}RangeChanged").connect(slot)
        self.blockSignals(False)

    @classmethod
    def _get_null_limits(cls):
        return {"x" : [np.nan, np.nan], "y" : [np.nan, np.nan], "z" : [np.nan, np.nan]} 

    def setRange(self, xRange=None, yRange=None, zRange=None, padding=None):
        if all((xRange is None,
                yRange is None,
                zRange is None)):
            for axis in "xyz":
                min_val, max_val = self.item_limit_engine.get_limit_values(axis)
                getattr(self, f"sig{axis.upper()}RangeChanged").emit(
                    PlotView(axis, list("xyz").index(axis), min_val, max_val), 
                    self
                )
            return

        if not xRange is None:
            plot_view=self.plot_views["x"]
            plot_view.update_min(xRange[0])
            plot_view.update_max(xRange[1])
            self.update_plot_view(plot_view)

        if not yRange is None:
            plot_view=self.plot_views["y"]
            plot_view.update_min(yRange[0])
            plot_view.update_max(yRange[1])
            self.update_plot_view(plot_view)
            
        if not zRange is None:
            plot_view=self.plot_views["z"]
            plot_view.update_min(zRange[0])
            plot_view.update_max(zRange[1])
            self.update_plot_view(plot_view)
        
        for item in self.addedItems:
            for axes in range(3):
                self.item_limit_engine.update_item_limits(item,
                                                          axes,
                                                          )
                
    def resetToDataLimits(self):
        for axis in range(3):
            min_val, max_val = self.item_limit_engine.get_limit_values(axis)
            self.setRange(**{f"{axis}Range": [min_val, max_val]})