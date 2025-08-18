from __future__ import annotations 
from typing import List, Optional, Tuple, Union, Dict, TYPE_CHECKING, Callable
if TYPE_CHECKING:
    from instruments.instruments import Option
    from pyvol_terminal.engines.interpolation_engines import Abstract3DInterpolator
    from pyvol_terminal.engines.surface_engines import AbstractSurfaceEngine
    from quantities.engines import MetricAxisEngine
from pydantic.dataclasses import dataclass, Field
from dataclasses import InitVar

import numpy as np
from typing import Any, List
from typing import Dict, Callable
from . import classes


class Config:
    arbitrary_types_allowed = True

@dataclass(slots=True, kw_only=True, config=Config)
class BaseContainer:
    all_price_types: List[str]
    displayed_price_types: List[str]
    instrument_names: List[str]
    metric_axis_engine: "MetricAxisEngine"
    domain: classes.Domain
    raw: Dict[str, classes.OptionChain]
    

    def update_value_by_instrument_object(self, instrument_object):
        for px_type, raw in self.raw.items():
            raw.update_all_metrics_name(instrument_object.ticker,
                                        *instrument_object.get_all_metrics_price_type(px_type))
            


@dataclass(slots=True)
class SurfaceContainer(BaseContainer):    
    surface_dataclasses: Dict[str, classes.Surface]
    scatter_dataclasses: Dict[str, classes.Points]
    x_min: float = Field(init=False, default=np.nan)
    x_max: float = Field(init=False, default=np.nan)
    y_min: float = Field(init=False, default=np.nan)
    y_max: float = Field(init=False, default=np.nan)
    z_min: float = Field(init=False, default=np.nan)
    z_max: float = Field(init=False, default=np.nan)
    valid_surface: bool = Field(init=False)
    valid_data_callback: List[Callable] = Field(init=False, default_factory=list)
    displayed_dataclasse_types: Dict[str, bool] = Field(default_factory=lambda: {"surface": True, "scatter": True})
    
    def __post_init__(self):
        self.calculate_limits()
        
    def add_valid_data_callback(self, callback):
        self.valid_data_callback.append(callback)
    
    def switch_axis(self, axis_direction, new_label):
        if new_label == self.metric_axis_engine.get_metric(axis_direction):
            return
        else:
            self.metric_axis_engine.change_function(axis_direction, new_label)
            self.cleanup()
            
    def toggle_data_dataclass(self, dataclass_type):
        self.displayed_dataclasse_types[dataclass_type]^=True
        
        dataclasses = getattr(self, f"{dataclass_type}_dataclasses")
        for dataclass in dataclasses:
            dataclass.displayed^=True
        
    def add_displayed_price_type(self, px_type):
        self.displayed_price_types.append(px_type)
        x, y, z, _ = self.metric_axis_engine.transform_values(self.raw[px_type])
        
        self.surface_dataclasses[px_type].evaluate_from_engine(x, y, z)
        self.scatter_dataclasses[px_type].evaluate_from_engine(x, y, z)
    
    def toggle_displayed_price_type(self, px_type):
        print(f"\ncontainers.toggle_displayed_price_type: {px_type}")
        if px_type in self.displayed_price_types:
            self.remove_displayed_price_type(px_type)
        else:
            self.add_displayed_price_type(px_type)
        self.calculate_limits()
    
    def remove_displayed_price_type(self, px_type):
        self.displayed_price_types.remove(px_type)

    def cleanup(self):
        for px_type in self.displayed_price_types:
            x, y, z, _ = self.metric_axis_engine.transform_values(self.raw[px_type])
            self.surface_dataclasses[px_type].evaluate_from_engine(x, y, z)
            self.scatter_dataclasses[px_type].evaluate_from_engine(x, y, z)
        self.calculate_limits()
        
    def get_dataclasses(self, px_type):
        return [self.surface_dataclasses[px_type], self.scatter_dataclasses[px_type]]
        
    def calculate_limits(self):
        if len(self.displayed_price_types) > 0:
            x_mins=[]
            x_maxs=[]
            y_mins=[]
            y_maxs=[]
            for px_type in self.displayed_price_types:
                for data_class in self.get_dataclasses(px_type):
                    if data_class.displayed:
                        x_mins.append(data_class.x_min)
                        x_maxs.append(data_class.x_max)
                        y_mins.append(data_class.y_min)
                        y_maxs.append(data_class.y_max)
                        
            if len(x_mins) > 0:
                self.x_min = np.amin(x_mins)
                self.x_max = np.amax(x_maxs)
                self.y_min = np.amin(y_mins)
                self.y_max = np.amax(y_maxs)
                
            z_mins=[]
            z_maxs=[]

            for px_type in self.displayed_price_types:
                for data_class in self.get_dataclasses(px_type):
                    if data_class.valid_values and data_class.displayed:
                        z_mins.append(data_class.z_min)
                        z_maxs.append(data_class.z_max)

            if len(z_mins) > 0:
                self.z_min = np.amin(z_mins)  
                self.z_max = np.amax(z_maxs)
                self.valid_surface = True
                for callback in self.valid_data_callback:
                    callback(True)
            else:
                self.valid_surface = False
                for callback in self.valid_data_callback:
                    callback(False)

    def get_limits(self):
        return self.x_min, self.x_max, self.y_min, self.y_max, self.z_min, self.z_max

    
@dataclass(slots=True)
class SliceContainer(BaseContainer):
    interpolator_engine: InitVar[Any]
    n_x: int
    axis_direction: str
    slice_container: Dict[str, classes.Slice]
    
    domain_idx_map: Dict[str, int] = None
    domain_vec: Dict[str, np.ndarray] = None
    domain_matrix: Dict[str, np.ndarray]  = None
    displayed_slices: List[str] = Field(init=False)  
    z_values: Dict[str, np.ndarray] = Field(init=False)
    x_metric: str = ""
    y_metric: str = ""
    
    
    def filter_domain(self):
        value_dict = {}
        for value in self.domain_vec:
            if self.axis_direction == 0:
                mask = self.domain.base_domain.expiry == value
                filtered_domain = self.domain.base_domain.expiry[mask]
            else:
                mask = self.domain.base_domain.strike == value
                filtered_domain = self.domain.base_domain.strike[mask]
            value_dict[value] = len(filtered_domain)
        top_12 = sorted(value_dict, key=value_dict.get, reverse=True)[:12]
        top_12 = np.sort(top_12)
        self.domain_vec = self.domain_vec[np.isin(self.domain_vec, top_12)]
        
    def update_value_by_instrument_object(self, instrument_object):
        for px_type, raw_dataclass in self.raw.items():
            raw_dataclass.update_all_metrics_name(instrument_object.ticker,
                                                  *instrument_object.get_all_metrics_price_type(px_type))
    
    def add_slice(self, px_type, value):
        self.update_slice(px_type, value)
        self.displayed_slices.append(value)
        
    def remove_slice(self, value):
        self.displayed_slices.remove(value)
    
    def switch_axis(self, new_axis_label, axis_direction):
        metric = self.metric_axis_engine.label_metric_map[new_axis_label]
        self.transformer = self.metric_axis_engine.get_function(metric)
        setattr(self, f"{axis_direction}_metric", metric)
        
        for px_type in self.displayed_price_types:
            self.update_slices(px_type)
    
    
    def update_slice(self, px_type, value):
        idx = self.domain_idx_map[value]
        x_old = self.domain_matrix[px_type]
        y_old = self.raw[px_type].ivol
        
        if self.x_metric == "delta":
            x_old = self.domain.x.flatten()
            y_old = self.domain.y.flatten()
            z_old = self.raw[px_type].ivol.flatten()
            x, y, z, idx_remove, idx_sort = self.transformer(self.raw[px_type],
                                                            x=x_old,
                                                            y=y_old,
                                                            z=z_old,
                                                            flatten=True)
            mask = y == value
            x, y, z = x[mask], y[mask], z[mask] 

            x_all = self.domain.x.flatten()[idx_remove][idx_sort][mask]
            nan_vec_x = np.full_like(self.domain.x_vect, np.nan)
            nan_vec_y = np.full_like(self.domain.x_vect, np.nan)
            
            mask2 = np.isin(self.domain.x_vect, x_all)
            
            nan_vec_x[mask2] = x
            nan_vec_y[mask2] = z
            
            x = nan_vec_x
            z = nan_vec_y        
        else:
            x, y, z, idx_remove, idx_sort = self.transformer(self.raw[px_type],
                                                            x=x_old,
                                                            z=y_old)
        if self.x_metric != "delta":
            if self.axis_direction == 0:
                x = x[idx]
                z = z[idx]
                self.domain_matrix[px_type][idx] = x 
                self.z_values[px_type][idx] = z
            else:
                x = x[:,idx]
                z = z[:,idx]
                self.domain_matrix[px_type][:, idx] = x
                self.z_values[px_type][:, idx] = z
        else:
            self.domain_matrix[px_type][idx] = x
            self.z_values[px_type][idx] = z

            
        if self.x_metric != "delta":
            xi = np.linspace(np.nanmin(x), np.nanmax(x), self.n_x)
        else:
            
            xi = np.linspace(0, 1, self.n_x)
            
        slice = self.slice_container[px_type][value]
        slice.update_domain(x, xi)
        slice.interpolate(x, z)
        
    def update_slices(self, px_type):
        for slice_value in self.displayed_slices:
            self.update_slice(px_type, slice_value)

    def cleanup(self):
        for px_type in self.displayed_price_types:
            self.update_slices(px_type)
            for slice_value in self.displayed_slices:
                slice = self.slice_container[px_type][slice_value]
                try:
                    if self.axis_direction == 0:
                        slice.interpolate(self.domain_matrix[px_type][self.domain_idx_map[slice_value]],
                                        self.z_values[px_type][self.domain_idx_map[slice_value]])
                    else:
                        slice.interpolate(self.domain_matrix[px_type][:, self.domain_idx_map[slice_value]],
                                        self.z_values[px_type][:, self.domain_idx_map[slice_value]])
                except:
                    pass
