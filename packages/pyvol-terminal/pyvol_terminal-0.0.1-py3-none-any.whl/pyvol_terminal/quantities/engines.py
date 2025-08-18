from __future__ import annotations 
from typing import List, Optional, Tuple, Union, Dict, TYPE_CHECKING, Callable

from datetime import datetime
import numpy as np
from .. import utils
from functools import partial
from . import functions


def get_attribute_label_maps():
    metric_label_map = {"delta" : "Delta",
                        "ivol" : "Implied Volatility",
                        "TVAR" : "Total Variance",
                        "variance" : "Variance",
                        "expiry" : "Expiry",
                        "years" : "Years",
                        "strike" : "Strike",
                        "moneyness" : "Moneyness",
                        "log_moneyness" : "Log-Moneyness" ,
                        "forward_moneyness" : "Forward Moneyness",
                        "standardised_moneyness" : "Standardised-Moneyness" ,
                        "VAR" : "Variance",
                        "TVOL" : "Total Volatility"
                        }
    
    label_metric_map = {label : metric for metric, label in metric_label_map.items()}
    label_metric_map["Date"] = "expiry"
    return metric_label_map, label_metric_map


class TickEngine:
    def __init__(self, label=None, **kwargs):
        self.label=label
        self._tick_functions = {"Expiry": self.Expiry_function,
                                "Date" : self.Date_function,
                                "Variance" : self.Variance_function,
                                "Years": self._null,
                                "Delta": self.Delta_function,
                                "Strike": self._null,
                                "Moneyness": self.Moneyness_func,
                                "Log-Moneyness": self._null,
                                "Standardised-Moneyness" : self._null,
                                "Forward Moneyness" : self._null,
                                "Implied Volatility": self._null,
                                "Total Volatility": self._null,
                                "Total Variance" : self._null,
                                "Variance" : self._null,
                                }
        
        self.function=self._tick_functions[self.label] if not self.label is None else None
    
    def get_ticks(self, values, n):
        if self.label == "Delta":
            self.function()
    
    def __call__(self, values):
        return self.function(values)
        
    def valid_data(self, flag):
        if flag:
            self.function = self._tick_functions[self.label]
        else:
            self.function = self._null
    
    def get_label(self):
        return self.label
    
    def get_function(self):
        return self.function
    
    def change_function(self, label):
        self.label=label
        self.function=self._tick_functions[label]
        
    @staticmethod
    def _null(values):
        return [f"{value:,.2f}" for value in values]

    @staticmethod
    def Moneyness_func(values):
        return [f"{value:,.2f}" for value in values]

    @staticmethod
    def null_visualise(values):
        return [f"{val:,.2f}" for val in values]
    
    @staticmethod
    def rounder(tick_labels):
        rounded = np.round(tick_labels)
        can_be_integer = np.all(np.isclose(tick_labels, rounded))
        if can_be_integer:
            return rounded.astype(int).astype(str).tolist()
        else:
            round_val = int(abs(np.floor(np.log10(abs(np.diff(tick_labels)).min()))))
            return np.round(tick_labels, round_val).astype(str).tolist()
     
    @staticmethod
    def Delta_function(values):
        if max(values) > 3:
            multiplier = 100
        else:
            multiplier = 1
        if values[0] < 0.5 * multiplier < values[-1]: 
            values = np.linspace(values[0], values[-1], len(values)).tolist()
            new_values=[]
            for value in values:
                if value < 0.5 * multiplier:
                    new_values.append(f"{round(value, 1)}P")
                elif value == 0.5 * multiplier:
                    new_values.append("ATM")
                else:
                    new_values.append(f"{round(1 - value, 2)}C")
            return new_values
        else:
            new_values = [f"{round(value, 1)}P" if value < 0.5 * multiplier else f"{round(1 - value, 2)}C" for value in values]
            return new_values

    @staticmethod
    def Variance_function(values):
        return [f"{round(value**2, 2)}" for value in values]
    
    @staticmethod
    def Expiry_function(values):
        return [datetime.fromtimestamp(value).strftime("%d-%b-%y").upper() if value == value and 0<value<16725186000 else str(value) for value in values]
    
    @staticmethod
    def Date_function(values):
        return TickEngine.Expiry_function(values)
            
    @staticmethod
    def Years_function(values):
        return [f"{val:,.2f}" for val in values]


class TickEngineManager:
    def __init__(self, x_label=None, y_label=None, z_label=None):
        self.x_engine=TickEngine(x_label) if not x_label is None else None
        self.y_engine=TickEngine(z_label) if not y_label is None else None
        self.z_engine=TickEngine(z_label) if not z_label is None else None

        self._int_str_map = {i : s for i, s in enumerate("xyz")}
            
    def add_valid_callbacks(self, data_container):
        data_container.add_valid_data_callback(self.x_engine.valid_data)
        data_container.add_valid_data_callback(self.y_engine.valid_data)
        if not self.z_engine is None:
            data_container.add_valid_data_callback(self.z_engine.valid_data)
    
    def change_function(self, axis_label, axis_direction):
        getattr(self, f"{axis_direction}_engine", axis_label).change_function(axis_label)
    
    def get_engine(self, axis_direction):
        if isinstance(axis_direction, str):
            return getattr(self, f"{axis_direction}_engine")
        elif isinstance(axis_direction, int):
            ax_str = self._int_str_map.get(axis_direction, None)
            return getattr(self, f"{ax_str}_engine")

def get_metric_maps():    
    metric_maps = {"delta" : ["OTM", "delta", "call_flag", "delta_mag"],
                   "moneyness" : ["moneyness"],
                   "log_moneyness" : ["log_moneyness"],
                   "forward_moneyness" : ["forward_moneyness"],
                   "standardised_moneyness" : ["standardised_moneyness"],
                   "strike" : [],
                   "expiry" : [],
                   "years" : [],
                   "ivol" : [],
                   "IVOL_perc" :[],
                   "TVAR" : [],
                   }
    
    return metric_maps

class MetricAxisEngine:
    def __init__(self, x_base, y_base, x_label, y_label, z_label):
        self.x_base = x_base.copy()
        self.y_base = y_base.copy()
        self.metric_label_map, self.label_metric_map = get_attribute_label_maps()      
        self.x_metric=self.label_metric_map[x_label]
        self.y_metric=self.label_metric_map[y_label]
        self.z_metric=self.label_metric_map[z_label]

        self.metric_functions = {"expiry": self.null_metric,
                                 "date": self.null_metric,
                                 "years": self.years_metric_func,
                                 "delta": self.delta_metric_mask_sorter,
                                 "strike": self.null_metric,
                                 "moneyness": self.moneyness_mask_sorter,
                                 "log_moneyness": self.log_moneyness_mask_sorter,
                                 "standardised_moneyness": self.standardised_moneyness_sorter,
                                 "forward_moneyness" : self.forward_moneyness_sorter,
                                 "ivol": self.null_metric,
                                 "TVAR": self.TVAR_function,
                                 "TVOL" : self.TVOL_function,
                                 "VAR" : self.VAR_function,
                                 }
        self.base_idx = np.arange(self.y_base.size, dtype=int)       
        
        self.x_function = self.metric_functions[self.x_metric]      
        self.y_function = self.metric_functions[self.y_metric]      
        self.z_function = self.metric_functions[self.z_metric]      
        self.x_singular = self.singular_null
        self.y_singular = self.singular_null
        self.z_singular = self.singular_null

    def singular_null(self, x):
        return x
        
    def transform_axis(self, axis_direction, args):
        return getattr(self, f"{axis_direction}_singular")(args)
    
    def transform_values(self,
                         x: np.ndarray,
                         y: np.ndarray,
                         ivol: np.ndarray=None,
                         **kwargs
                         ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:        
        x_orig, y_orig = x, y
        z_orig = ivol.copy()
        x_metric, y, z, mask_removal_x, mask_rearrange_x = self.x_function(x=x_orig, y=y_orig, z=z_orig, **kwargs)
        
        x_new = x_orig[mask_removal_x][mask_rearrange_x]
        
        x_new, y_metric, z, mask_removal_y, mask_rearrange_y = self.y_function(x=x_new, y=y, z=z, **kwargs)
        
        x_metric = x_metric[mask_removal_y][mask_rearrange_y]
        y_new = y_orig[mask_removal_x][mask_rearrange_x][mask_removal_y][mask_rearrange_y]
        
        x, y, z_metric, mask_removal_z, mask_rearrange_z = self.z_function(x=x_new, y=y_new, z=z, **kwargs)
        
        x_metric = x_metric[mask_removal_z][mask_rearrange_z]
        y_metric = y_metric[mask_removal_z][mask_rearrange_z]
        
        idx_map = self.base_idx[mask_removal_x][mask_rearrange_x][mask_removal_y][mask_rearrange_y][mask_removal_z][mask_rearrange_z]
        
        return x_metric, y_metric, z_metric, idx_map

    def get_metric(self, axis_direction):
        return getattr(self, f"{axis_direction}_metric")
    
    def get_function(self, axis_direction):
        return getattr(self, f"{axis_direction}_function")
    
    def change_function(self, label, axis_direction):
        metric = self.label_metric_map[label]
        setattr(self, f"{axis_direction}_metric", metric)
        setattr(self, f"{axis_direction}_function", self.metric_functions[metric])
                   
    @staticmethod
    def null_metric(x=None, y=None, z=None, **kwargs):
        return x, y, z, [True] * z.size, np.arange(z.size)
    
    @staticmethod
    def _base_money_sorter(x=None, y=None, z=None, OTM=None, **kwargs):
        mask_removal = OTM        
        if not y is None:
            x, y, z = x[mask_removal], y[mask_removal], z[mask_removal]
            mask_rearrange = np.lexsort((x, y))
            return x[mask_rearrange], y[mask_rearrange], z[mask_rearrange], mask_removal, mask_rearrange
        else:
            x, z = np.where(mask_removal, x, np.nan), np.where(mask_removal, z, np.nan)
            ind = np.argsort(x, axis=0)
            return x, None, z, mask_removal, ind

    @staticmethod
    def TVAR_function(x=None, y=None, z=None, **kwargs):
        return x, y, (z**2) * utils.convert_unix_maturity_to_years(y), [True] * z.size, np.arange(z.size)

    @staticmethod
    def TVOL_function(x=None, y=None, z=None, **kwargs):
        return x, y, z * utils.convert_unix_maturity_to_years(y), [True] * z.size, np.arange(z.size)
    
    @staticmethod
    def VAR_function(x=None, y=None, z=None, **kwargs):
        return x, y, z**2, [True] * z.size, np.arange(z.size)

    @staticmethod
    def IVOL_perc_function(x=None, y=None, z=None, **kwargs):
        return x, y, 100 * z, [True] * z.size, np.arange(z.size)
    
    def moneyness_mask_sorter(self, x=None, y=None, z=None, moneyness=None, OTM=None, **kwargs):
        x = moneyness
        return self._base_money_sorter(x=x, y=y, z=z, OTM=OTM)
    
    def log_moneyness_mask_sorter(self, x=None, y=None, z=None, log_moneyness=None, OTM=None, **kwargs):
        x = log_moneyness
        return self._base_money_sorter(x=x, y=y, z=z, OTM=OTM)
    
    def standardised_moneyness_sorter(self, x=None, y=None, z=None, standardised_moneyness=None, OTM=None, **kwargs):
        x = standardised_moneyness
        return self._base_money_sorter(x=x, y=y, z=z, OTM=OTM)
    
    def forward_moneyness_sorter(self, x=None, y=None, z=None, forward_moneyness=None, OTM=None, **kwargs):
        x = forward_moneyness
        return self._base_money_sorter(x=x, y=y, z=z, OTM=OTM)

    @staticmethod
    def years_metric_func(x=None, y=None, z=None, **kwargs):
        return x, utils.convert_unix_maturity_to_years(y), z, [True] * z.size, np.arange(z.size)

    def delta_metric_mask_sorter(self, x=None, y=None, z=None, flatten=False, OTM=None, delta=None, call_flag=None, **kwargs):
        delta_mag=np.abs(delta)
        if flatten:
            mask_removal = OTM.flatten() & (delta_mag.flatten() < 0.5)
            put_indices = np.where(~call_flag.flatten()[mask_removal])[0]
            call_indices = np.where(call_flag.flatten()[mask_removal])[0]
            x_masked, y_masked, z_masked = delta.flatten()[mask_removal], y[mask_removal], z[mask_removal]
        else:
            mask_removal = OTM & (delta_mag < 0.5)
            put_indices = np.where(~call_flag[mask_removal])[0]
            call_indices = np.where(call_flag[mask_removal])[0]
            x_masked, y_masked, z_masked = delta[mask_removal], y[mask_removal], z[mask_removal]
        
        sorted_put_indices = put_indices[np.lexsort((y_masked[put_indices], -x_masked[put_indices]))] if put_indices.size > 0 else np.array([], dtype=int)
        sorted_call_indices = call_indices[np.lexsort((y_masked[call_indices], -x_masked[call_indices]))] if call_indices.size > 0 else np.array([], dtype=int)

        mask_rearrange = np.concatenate([sorted_put_indices, sorted_call_indices])
        x_sorted, y_sorted, z_sorted = x_masked[mask_rearrange], y_masked[mask_rearrange], z_masked[mask_rearrange]
        mask = x_sorted > 0
        x_sorted[~mask] = -x_sorted[~mask]
        x_sorted[mask] = 1 - x_sorted[mask]
        return x_sorted, y_sorted, z_sorted, mask_removal, mask_rearrange

