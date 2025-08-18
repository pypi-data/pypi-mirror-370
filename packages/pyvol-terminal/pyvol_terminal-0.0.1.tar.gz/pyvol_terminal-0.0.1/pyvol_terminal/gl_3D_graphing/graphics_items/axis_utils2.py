from datetime import datetime
import numpy as np
from ... import utils

def get_attribute_label_maps():
    metric_label_map = {"delta" : "Delta",
                        "ivol" : "Implied Volatility",
                        "IVOL_perc" : "Implied Volatility (%)",
                        "TVAR" : "Total Volatility",
                        "expiry" : "Expiry",
                        "years" : "Years",
                        "strike" : "Strike",
                        "moneyness" : "Moneyness (%)",
                        "log_moneyness" : "Log-Moneyness" ,
                        "standardised_moneyness" : "Standardised-Moneyness" 
                        }
    
    label_metric_map = {label : metric for metric, label in metric_label_map.items()}
    return metric_label_map, label_metric_map

class TickEngine:
    def __init__(self, label, valid_data=False):
        self.label=label
        self._tick_functions = {"Expiry": self.Expiry_function,
                                "Years": self._null,
                                "Delta": self.Delta_function,
                                "Strike": self._null,
                                "Moneyness (%)": self.Moneyness_func,
                                "Log-Moneyness": self._null,
                                "Implied Volatility": self._null,
                                "Total Volatility": self._null,
                                "Implied Volatility (%)" : self._null}
        
        self.function=self._tick_functions[self.label]
    
    def get_ticks(self, values, n):
        if self.label == "Delta":
            self.function()
    
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
        if not 1 in values and (values[0] + values[-1])/2 == 1:
            values = np.append(values, 1)
            values.sort()
        return [f"{round(100 * value)}" for value in values]

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
        if values[0] < 0.5 < values[-1]: 
            values = np.linspace(values[0], values[-1], len(values)).tolist()
            if not 0.5 in values:
                values = np.append(values, 0.5)
                values.sort()
            new_values=[]
            for value in values:
                if value < 50:
                    new_values.append(f"{round(value, 1)}P")
                elif value == 50:
                    new_values.append("ATM")
                else:
                    new_values.append(f"{round(1 - value, 2)}C")
            return new_values
        else:
            return [f"{round(value, 1)}P" if value < 0.5 else f"{round(1 - value, 2)}C" for value in values]
            
    @staticmethod
    def Expiry_function(values):
        return [datetime.fromtimestamp(value).strftime("%d-%b-%y").upper() if value == value and 0<value<16725186000 else str(value) for value in values]
            
    @staticmethod
    def Years_function(values):
        return [f"{val:,.2f}" for val in values]



class TickEngineManager:
    def __init__(self, x_label, y_label, z_label=None):
        self.x_engine=TickEngine(x_label)
        self.y_engine=TickEngine(y_label)
        if not z_label is None:
            self.z_engine=TickEngine(z_label)
        else:
            self.z_engine=None
    def add_valid_callbacks(self, data_container):
        data_container.add_valid_data_callback(self.x_engine.valid_data)
        data_container.add_valid_data_callback(self.y_engine.valid_data)
        if not self.z_engine is None:
            data_container.add_valid_data_callback(self.z_engine.valid_data)
    
    def change_function(self, axis_direction, axis_label):
        getattr(self, f"{axis_direction}_engine", axis_label).change_function(axis_label)
    
    def get_engine(self, axis_direction):
        return getattr(self, f"{axis_direction}_engine")
    

def get_metric_maps():    
    metric_maps = {"delta" : ["OTM", "delta", "call_flag", "delta_mag"],
                   "moneyness" : ["moneyness"],
                   "log_moneyness" : ["log_moneyness"],
                   "standardised_moneyness" : ["standardised_moneyness"],
                   "strike" : [],
                   "expiry" : [],
                   "years" : [],
                   "ivol" : [],
                   "IVOL_perc" :[],
                   "TVAR" : []}
    
    return metric_maps

def get_metric_functions():
    metric_functions = {"expiry" : null_metric,
                        "years" : years_metric_func,
                        "delta" : delta_metric_mask_sorter,
                        "strike" : null_metric,
                        "moneyness" : moneyness_mask_sorter,
                        "log_moneyness": moneyness_mask_sorter,
                        "standardised_moneyness" : moneyness_mask_sorter,
                        "ivol": null_metric,
                        "IVOL_perc" : null_metric,
                        "null" : null_metric,
                        "TVAR" : TVAR_function,
                        }
    
    return  metric_functions

def null_metric(raw_object, x, y, z):
    return x, y, z, [True]*z.size, np.arange(z.size)

def get_spot_metric_functions():
    metric_functions = get_metric_functions()
    metric_functions["moneyness"] = moneyness_spot
    metric_functions["log_moneyness"] = log_moneyness_spot
    return metric_functions

def _base_money_sorter(raw_object, x, y, z):
    mask_removal = raw_object.OTM
    x = x[mask_removal]
    y = y[mask_removal]
    z = z[mask_removal]
    
    mask_rearrange = np.lexsort((x, y))
    
    x = x[mask_rearrange]
    y = y[mask_rearrange]
    z = z[mask_rearrange]
    return x, y, z, mask_removal, mask_rearrange

def TVAR_function(raw_object, x, y, z):
    return x, y, z*utils.convert_unix_maturity_to_years(y), [True]*z.size, np.arange(z.size)

def IVOL_perc_function(raw_object, x, y, z):
    return x, y, 100*z, [True]*z.size, np.arange(z.size)

def moneyness_mask_sorter(raw_object, x, y, z):
    x=raw_object.moneyness
    return _base_money_sorter(raw_object, x, y, z)

def log_moneyness_mask_sorter(raw_object, x, y, z):
    x=raw_object.log_moneyness
    return _base_money_sorter(raw_object, x, y, z)

def standardised_moneyness_sorter(raw_object, x, y, z):
    x=raw_object.standardised_moneyness
    return _base_money_sorter(raw_object, x, y, z)

def years_metric_func(raw_object, x, y, z):
    return x, utils.convert_unix_maturity_to_years(y), z, [True]*z.size, np.arange(z.size)

def moneyness_spot(raw_object, x, y, z):
    return raw_object.moneyness, y, z, [True]*z.size, np.arange(z.size)

def log_moneyness_spot(raw_object, x, y, z):
    return raw_object.log_moneyness, y, z, [True]*z.size, np.arange(z.size)

def delta_metric_mask_sorter(raw_object, x, y, z):
    mask_removal = raw_object.OTM & (raw_object.delta_mag < 0.5)
    x = raw_object.delta
    x_masked = x[mask_removal] 
    y_masked = y[mask_removal]  
    z_masked = z[mask_removal]
    
    put_indices = np.where(~raw_object.call_flag[mask_removal])[0]
    call_indices = np.where(raw_object.call_flag[mask_removal])[0]

    if put_indices.size > 0:
        sorted_put_indices = put_indices[np.lexsort((y_masked[put_indices], -x_masked[put_indices]))]
    else:
        sorted_put_indices = np.array([], dtype=int)
    if call_indices.size > 0:
        sorted_call_indices = call_indices[np.lexsort((y_masked[call_indices], -x_masked[call_indices]))]
    else:
        sorted_call_indices = np.array([], dtype=int)

    mask_rearrange = np.concatenate([sorted_put_indices, sorted_call_indices])
    
    x_sorted = x_masked[mask_rearrange]
    y_sorted = y_masked[mask_rearrange]
    z_sorted = z_masked[mask_rearrange]        
    mask = x_sorted > 0
    x_sorted[~mask] = -1 * x_sorted[~mask]  
    x_sorted[mask] = 1 - x_sorted[mask]  
    return x_sorted, y_sorted, z_sorted, mask_removal, mask_rearrange


class MetricAxisEngine:
    def __init__(self, x_base, y_base, x_label, y_label, z_label):
        self.x_base = x_base.copy()
        self.y_base = y_base.copy()
        self.metric_label_map, self.label_metric_map = get_attribute_label_maps()      
        self.x_metric=self.label_metric_map[x_label]
        self.y_metric=self.label_metric_map[y_label]
        self.z_metric=self.label_metric_map[z_label]

        self.metric_functions = {"expiry": self.null_metric,
                                "years": self.years_metric_func,
                                "delta": self.delta_metric_mask_sorter,
                                "strike": self.null_metric,
                                "moneyness": self.moneyness_mask_sorter,
                                "log_moneyness": self.moneyness_mask_sorter,
                                "standardised_moneyness": self.moneyness_mask_sorter,
                                "ivol": self.null_metric,
                                "IVOL_perc": self.IVOL_perc_function,
                                "TVAR": self.TVAR_function,
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
    
    
    def transform_raw_object(self, raw_object):        
        x_orig, y_orig = self.x_base.copy(), self.y_base.copy()
        z_orig = raw_object.ivol.copy()

        x_metric, y, z, mask_removal_x, mask_rearrange_x = self.x_function(raw_object, x_orig, y_orig, z_orig)
        
        x_new = x_orig[mask_removal_x][mask_rearrange_x]
        
        x_new, y_metric, z, mask_removal_y, mask_rearrange_y = self.y_function(raw_object, x_new, y, z)
        
        x_metric = x_metric[mask_removal_y][mask_rearrange_y]
        y_new = y_orig[mask_removal_x][mask_rearrange_x][mask_removal_y][mask_rearrange_y]
        
        x, y, z_metric, mask_removal_z, mask_rearrange_z = self.z_function(raw_object, x_new, y_new, z)
        
        x_metric = x_metric[mask_removal_z][mask_rearrange_z]
        y_metric = y_metric[mask_removal_z][mask_rearrange_z]
        
        idx_map = self.base_idx[mask_removal_x][mask_rearrange_x][mask_removal_y][mask_rearrange_y][mask_removal_z][mask_rearrange_z]
        
        return x_metric, y_metric, z_metric, idx_map

    def get_metric(self, axis_direction):
        return getattr(self, f"{axis_direction}_metric")
    
    def get_function(self, axis_direction):
        return getattr(self, f"{axis_direction}_function")
    
    def change_function(self, axis_direction, label):
        setattr(self, f"{axis_direction}_metric", self.label_metric_map[label])
        setattr(self, f"{axis_direction}_function", self.metric_functions[self.label_metric_map[label]])
        
    
                                
    @staticmethod
    def null_metric(raw_object, x=None, y=None, z=None):
        return x, y, z, [True] * z.size, np.arange(z.size)
    
    @staticmethod
    def _base_money_sorter(raw_object, x=None, y=None, z=None):
        mask_removal = raw_object.OTM        
        if not y is None:
            x, y, z = x[mask_removal], y[mask_removal], z[mask_removal]
            mask_rearrange = np.lexsort((x, y))
            return x[mask_rearrange], y[mask_rearrange], z[mask_rearrange], mask_removal, mask_rearrange
        else:
            x, z = np.where(mask_removal, x, np.nan), np.where(mask_removal, z, np.nan)
            ind = np.argsort(x, axis=0)
            return x, None, z, mask_removal, ind

    @staticmethod
    def TVAR_function(raw_object, x=None, y=None, z=None):
        return x, y, z * utils.convert_unix_maturity_to_years(y), [True] * z.size, np.arange(z.size)
    
    @staticmethod
    def IVOL_perc_function(raw_object, x=None, y=None, z=None):
        return x, y, 100 * z, [True] * z.size, np.arange(z.size)
    
    def moneyness_mask_sorter(self, raw_object, x=None, y=None, z=None):
        x = raw_object.moneyness
        return self._base_money_sorter(raw_object, x, y, z)
    
    def log_moneyness_mask_sorter(self, raw_object, x=None, y=None, z=None):
        x = raw_object.log_moneyness
        return self._base_money_sorter(raw_object, x, y, z)
    
    def standardised_moneyness_sorter(self, raw_object, x=None, y=None, z=None):
        x = raw_object.standardised_moneyness
        return self._base_money_sorter(raw_object, x, y, z)
    
    @staticmethod
    def years_metric_func(raw_object, x=None, y=None, z=None):
        return x, utils.convert_unix_maturity_to_years(y), z, [True] * z.size, np.arange(z.size)

    def delta_metric_mask_sorter(self, raw_object, x=None, y=None, z=None, flatten=False):
        if flatten:
            mask_removal = raw_object.OTM.flatten() & (raw_object.delta_mag.flatten() < 0.5)
            put_indices = np.where(~raw_object.call_flag.flatten()[mask_removal])[0]
            call_indices = np.where(raw_object.call_flag.flatten()[mask_removal])[0]
            x_masked, y_masked, z_masked = raw_object.delta.flatten()[mask_removal], y[mask_removal], z[mask_removal]
        else:
            mask_removal = raw_object.OTM & (raw_object.delta_mag < 0.5)
            put_indices = np.where(~raw_object.call_flag[mask_removal])[0]
            call_indices = np.where(raw_object.call_flag[mask_removal])[0]
            x_masked, y_masked, z_masked = raw_object.delta[mask_removal], y[mask_removal], z[mask_removal]
        
        sorted_put_indices = put_indices[np.lexsort((y_masked[put_indices], -x_masked[put_indices]))] if put_indices.size > 0 else np.array([], dtype=int)
        sorted_call_indices = call_indices[np.lexsort((y_masked[call_indices], -x_masked[call_indices]))] if call_indices.size > 0 else np.array([], dtype=int)

        mask_rearrange = np.concatenate([sorted_put_indices, sorted_call_indices])
        x_sorted, y_sorted, z_sorted = x_masked[mask_rearrange], y_masked[mask_rearrange], z_masked[mask_rearrange]
        mask = x_sorted > 0
        x_sorted[~mask] = -x_sorted[~mask]
        x_sorted[mask] = 1 - x_sorted[mask]
        return x_sorted, y_sorted, z_sorted, mask_removal, mask_rearrange

