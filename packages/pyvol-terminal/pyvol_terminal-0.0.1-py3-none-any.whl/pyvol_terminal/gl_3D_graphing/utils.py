from __future__ import annotations 
from typing import List, Optional, Tuple, Union, Dict, TYPE_CHECKING, Callable
if TYPE_CHECKING:
    from pyvol_terminal.gl_3D_graphing.graphics_items.GL3DGraphicsItems import GlPlotItemMixin
    from pyvol_terminal.gl_3D_graphing.widgets.view_box import ViewBox, AxisNormaliser
    
    from uuid import uuid4 

import numpy as np
from dataclasses import dataclass, field
from pyqtgraph import opengl




def get_item_data(item):
    if isinstance(item, opengl.GLScatterPlotItem):
        return item.pos
    elif isinstance(item, opengl.GLMeshItem):
        return item.opts['meshdata'].vertexes()
    elif isinstance(item, opengl.GLLinePlotItem):
        return item.pos
    elif isinstance(item, opengl.GLBarGraphItem):
        return item.points()
    return None

def compute_scene_bbox(items):
    min_vals, max_vals = None, None
    
    for item in items:
        data = get_item_data(item)
        if data is None or len(data) == 0:
            continue
            
        if not isinstance(data, np.ndarray):
            data = np.array(data)
            
        if data.ndim == 1:
            data = data[np.newaxis, :]
        if data.shape[1] == 2:
            data = np.hstack([data, np.zeros((len(data), 1))])
            
        item_min = np.nanmin(data, axis=0)
        item_max = np.nanmax(data, axis=0)
        
        if min_vals is None:
            min_vals, max_vals = item_min, item_max
        else:
            min_vals = np.minimum(min_vals, item_min)
            max_vals = np.maximum(max_vals, item_max)
    
    if min_vals is None:
        return np.array([0, 0, 0]), np.array([1, 1, 1])
    
    return min_vals, max_vals







def normalise_setData_pos(item: GlPlotItemMixin,
                          vb: ViewBox,
                          ignoreBounds: bool,
                          *args,
                          **kwargs
                          ) -> np.ndarray:
    unnorm_pos = kwargs["pos"]
    if isinstance(unnorm_pos, tuple):
        unnorm_pos = np.array(unnorm_pos)
    item.unnorm_pos = unnorm_pos.copy()
    if not ignoreBounds:
        for idx, axis in enumerate("xyz"):
            vb._preNormalisation(item, axis, unnorm_pos[:, idx])
    pos=kwargs["pos"]
    _init_shape = np.shape(pos)
    x = vb.axis_normaliser_container["x"].normalise(pos[:, 0])
    y = vb.axis_normaliser_container["y"].normalise(pos[:, 1])
    z = vb.axis_normaliser_container["z"].normalise(pos[:, 2])
    kwargs["pos"] = np.column_stack((x , y , z)).reshape(_init_shape)
    return item.original_setData(*args, **kwargs)

def normalise_setData_xyz(item: GlPlotItemMixin,
                          vb: ViewBox,
                          ignoreBounds: bool,
                          *args,
                          **kwargs
                          ) -> Tuple[np.ndarray, ...]:
    new_args = list(args)
    if len(new_args) >= 3:
        for idx, axis in enumerate("xyz"):
            setattr(item, f"unnorm_{axis}", args[idx]) 
            vb._preNormalisation(item, axis, args[idx])
            #item.unnorm_pos[:, idx] = args[idx]
            
        for idx, axis in enumerate("xyz"):
            new_args[idx] = vb.axis_normaliser_container[axis].normalise(args[idx])
    else:
        for idx, axis in enumerate("xyz"):
            if axis in kwargs:
                setattr(item, f"unnorm_{axis}", kwargs[axis]) 
                #item.unnorm_pos[:, idx] = kwargs[axis]
                vb._preNormalisation(item, axis, kwargs[axis])
        for idx, axis in enumerate("xyz"):
            if axis in kwargs:
                kwargs[axis] = vb.axis_normaliser_container[axis].normalise(kwargs[axis])
    return item.original_setData(*new_args, **kwargs)

def renormalise_data_pos(item, plot_view):
    pos=item.unnorm_pos.copy()
    if plot_view.axis=="x":
        idx=0
    elif plot_view.axis=="y":
        idx=1
    else:
        idx=2
    if len(np.shape(pos)) == 1:
        if isinstance(pos, tuple):
            pos = np.array(pos)
        pos[idx] = plot_view.normalise(pos[idx])
    else:
        pos[:, idx] = plot_view.normalise(pos[:,idx])
    item.original_setData(pos=pos) 
    
def filter_data_pos(item, plot_view: AxisNormaliser):
    pos=item.unnorm_pos.copy()
    if plot_view.axis=="x":
        idx=0
    elif plot_view.axis=="y":
        idx=1
    else:
        idx=2
    if len(np.shape(pos)) == 1:
        if isinstance(pos, tuple):
            pos = np.array(pos)
        mask = plot_view.mask_from_data(pos[idx])
        pos[idx] = plot_view.normalise(pos[idx])
    else:
        mask = plot_view.mask_from_data(pos[idx])
        pos[:, idx] = plot_view.normalise(pos[:,idx])
    pos = pos[mask]
    item.original_setData(pos=pos) 

def filter_data_xyz(item: GlPlotItemMixin,
                    ax: str,
                    view_box: ViewBox
                    ):
    values = getattr(item, f"_all_{ax}").copy()
    plot_view = view_box.axis_normaliser_container[ax]
    values_normalised=plot_view.normalise(values)
    mask = plot_view.mask_from_data(values)
    values_normalised[~mask]=np.nan
    values_f = values.copy()
    values_f[~mask]=np.nan
    kwargs={plot_view.axis : values_normalised}

    if plot_view.axis!="z":
        if plot_view.axis=="x":
            
            values_z = item._all_z.copy()
            values_z[~mask, :]=np.nan
            values_z_normalised = view_box.axis_normaliser_container["z"].normalise(values_z)
        else:
            values_z = item._all_z.copy()
            values_z[:, ~mask]=np.nan
            values_z_normalised = view_box.axis_normaliser_container["z"].normalise(values_z)
        print(f"values_z: {(np.nanmin(values_z).round(3), np.nanmax(values_z).round(3))}")

        kwargs["z"] = values_z_normalised
    item.original_setData(**kwargs) 

def filter_data_xyz2(item, plot_view: AxisNormaliser):
    values = getattr(item, f"_all_{plot_view.axis}")
    new_values=plot_view.normalise(values)
    mask = plot_view.mask_from_data(values)
    new_values[~mask]=np.nan
    
    kwargs={plot_view.axis : new_values}

    if plot_view.axis!="z":

        if plot_view.axis=="x":
            
            #values_z = getattr(item, f"unnorm_z")
            values_z = item._all_z
            values_z[~mask, :]=np.nan
        else:
            #values_z = getattr(item, f"unnorm_z")
            values_z = item._all_z

            values_z[:, ~mask]=np.nan
        kwargs["z"] = values_z
    item.original_setData(**kwargs) 


def renormalise_data_xyz(item, plot_view):
    values = getattr(item, f"unnorm_{plot_view.axis}")
    new_values=plot_view.normalise(values)
    kwargs={plot_view.axis : new_values}
    item.original_setData(**kwargs) 




























    def filter_on_view222(self,
                       ax: str,
                       view_box
                       ):
        
        values = self._all_pos_vect[ax]
        plot_view = view_box.plot_views[ax]
        
        mask = plot_view.mask_from_data(values)
        values_in_view = values[~mask]
        self._in_view_vect[ax] = values_in_view
        
        values_onview_normalised = plot_view.normalise(values_in_view)
        kwargs = {self._ax_idx_str_map[ax] : values_onview_normalised}
        if ax != 2:
            values_z = self._all_pos_vect[2]
            if plot_view.axis==0:
                
                zvalues_in_view = values_z[~mask, :]
            else:
                zvalues_in_view = values_z[:, ~mask]
            
            self._in_view_vect[2] = zvalues_in_view
            
            zvalues_onview_normalised = view_box.plot_views[2].normalise(zvalues_in_view)
            
            kwargs[self._ax_idx_str_map[ax]]=zvalues_onview_normalised

        super().setData(**kwargs) 


    def id(self):
        return self._id
    






























class ItemLimists22222:
    def __init__(self, axes):
        self.axes=axes
        self.items = {}
        self.heap_min = {ax:[] for ax in self.axes}
        self.heap_max = {ax:[] for ax in self.axes}
        self.min_sorted={ax:[] for ax in self.axes}
        self.max_sorted={ax:[] for ax in self.axes}
        self.min_items = {ax:{} for ax in self.axes}
        self.max_items = {ax:{} for ax in self.axes}
        
    def _calculate_limits(self, values):
        if np.any(~np.isnan(values)):
            min, max = np.nanmin(values), np.nanmax(values)
        else:
            min, max = np.inf, -np.inf 
        return [min, max]
    
    def _get_value_vectors(self, item):
        vals=[]
        if hasattr(item, "pos"):
            pos = item.pos
            pos = np.atleast_2d(pos)
            for i in range(pos.shape[1]):
                vals.append(pos[:,i])
        else:
            for axis in self.axes:
                vals.append(getattr(item, f"_{axis}"))
        return vals
    
    def _calculate_vector_limits(self, vectors):
        limits=[]
        for vector in vectors:
            limits.append(self._calculate_limits(vector))
        return limits

    def get_limit_values(self, axis):
        return self.min_sorted[axis][0], self.max_sorted[axis][-1]

    def addItem(self, item):
        vectors = self._get_value_vectors(item)
        vector_limits = self._calculate_vector_limits(vectors)
        self.items[item.id()] = {}
        for axis, limits in zip(self.axes, vector_limits):
            self.items[item.id()][axis] = limits
            self.min_items[axis][item.id()]=limits[0]
            self.max_items[axis][item.id()]=limits[1]
            self._sort_limits(axis)

    def _sort_limits(self, axis):
        self.min_sorted[axis]=list(self.min_items[axis].values())
        self.min_sorted[axis].sort()
        self.max_sorted[axis]=list(self.max_items[axis].values())
        self.max_sorted[axis].sort()
    
    def update_item_limits(self, item, axis, values):
        min_val, max_val = self._calculate_limits(values)
        self.min_items[axis][item.id()]=min_val
        self.max_items[axis][item.id()]=max_val
        self._sort_limits(axis)

    def removeItem(self, internal_id):
        if internal_id in self.items:
            del self.items[internal_id]