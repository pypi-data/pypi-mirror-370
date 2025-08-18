import numpy as np
import time


def convert_unix_maturity_to_years(unix_maturity):
    return (unix_maturity - time.time()) / 3600 / 24 / 365

def convert_to_yte(timestamp, unix_maturity):
    return (unix_maturity - timestamp) / 3600 / 24 / 365

def null_metric(raw_object, x, y, z):
    return x, y, z, [True]*z.size, np.arange(z.size)

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
    return x, y, z*convert_unix_maturity_to_years(y), [True]*z.size, np.arange(z.size)

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
    return x, convert_unix_maturity_to_years(y), z, [True]*z.size, np.arange(z.size)

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


