from __future__ import annotations 
import numpy as np
import copy
from pyvol_terminal.plotting_engines import MetricEngine
from pyvol_terminal import metric_attributes
from classes import BaseDomain, Domain, SurfaceContainer, DataContainerManager, OptionChain, Points, surface, SmileContainer

def create_options_data_container_manager(df, config_instruments, config_interface):
    n_options = df.shape[0]
    name_index_map = {v: k for k, v in df["ticker"].to_dict().items()}
    base_domain = BaseDomain(df["strike"].values, df["expiry"].values, "Strike", "Expiry")    
    domain = Domain(base_domain)
    data_container_manager = DataContainerManager(MetricEngine(base_domain), config_instruments["price_types"])
    
    for px_type in config_instruments["price_types"]:
        domain = copy.deepcopy(domain)
        
        args = [n_options, name_index_map]
        for metric in metric_attributes.get_metric_attr():
            if metric == "OTM" or metric == "call_flag":
                val = False
            else:
                val = np.nan
            arr = np.full(n_options, val)
            args.append(arr) 
        raw = OptionChain(*args)
        
        if "Surface" in config_interface:
            scatter = Points(domain.x, domain.y, raw.ivol)
            surface = surface(base_domain,
                              scatter,
                              copy.deepcopy(config_interface["Surface"]["interpolation_config"]["engine"]),
                              config_interface["Surface"]["interpolation_config"]["n_x"],
                              config_interface["Surface"]["interpolation_config"]["n_y"])
        else:
            scatter=None
            surface=None
        if "Smile" in config_interface:
            smile = SmileContainer(base_domain,
                          raw,
                          copy.deepcopy(config_interface["Smile"]["interpolation_config"]["engine"]),
                          config_interface["Smile"]["interpolation_config"]["n_x"])
        else:
            smile=None
        data_container = SurfaceContainer(px_type,
                                       domain,
                                       raw,
                                       scatter,
                                       surface,
                                       smile)
        data_container.calculate_limits()
        data_container_manager.add_data_container(data_container)
    return data_container_manager

def create_matrices(df):
    x = df["strike"]
    y = df["expiry"]
    z = np.full(x.size, np.nan)
    instrument_names = df["ticker"].to_list()
    
    x_unique = np.unique(x)
    y_unique = np.unique(y)

    X_grid, Y_grid = np.meshgrid(x_unique, y_unique)
    Z_grid = np.full_like(X_grid, np.nan)
    name_index_map = {}
    for xi, yi, zi, name in zip(x, y, z, instrument_names):
        i = np.where(y_unique == yi)[0][0] 
        j = np.where(x_unique == xi)[0][0] 
        Z_grid[i, j] = zi
        name_index_map[name] = (i,j)

    return X_grid, Y_grid, Z_grid, name_index_map
    


def create_smile_data_containers(df, config_instruments, config_interface):
    n_options = df.shape[0]
    strike_grid, expiry_grid, price_grid, name_index_map = create_matrices(df)
    
    base_domain = BaseDomain(strike_grid, expiry_grid, "Strike", "Expiry")    
    domain = Domain(base_domain)
    data_container_manager = DataContainerManager(MetricEngine(base_domain), config_instruments["price_types"])
    
    for px_type in config_instruments["price_types"]:
        domain = copy.deepcopy(domain)
        
        args = [n_options, name_index_map]
        for metric in metric_attributes.get_metric_attr():
            if metric == "OTM" or metric == "call_flag":
                val = False
            else:
                val = np.nan
            arr = np.full(n_options, val)
            args.append(arr) 
        raw = OptionChain(*args)

    
        smile = SmileContainer(base_domain,
                    raw,
                    copy.deepcopy(config_interface["Smile"]["interpolation_config"]["engine"]),
                    config_interface["Smile"]["interpolation_config"]["n_x"])
        data_container = SurfaceContainer(px_type,
                                       domain,
                                       raw,
                                       smile)
        data_container.calculate_limits()
        data_container_manager.add_data_container(data_container)

    






def create_metric_arrays_for_view(n_options, price_types):
    metric_attr = metric_attributes.get_metric_attr()
    metric_pType_array_dict = {}
    idx_metric_array_dict = {n : {metric : None for metric in metric_attr} for n in range(n_options)}
    full_array = {}
    for metric, attr_dict in metric_attr.items():
        if metric == "OTM":
            val = False
        else:
            val = np.nan

        if attr_dict["multi_dim_flag"]:
            a1 = np.arange(1, n_options+1)
            a2 = 10*np.arange(1, n_options+1)
            a3 = 100 * np.arange(1, n_options+1)
            #array = np.column_stack((a1,a2,a3))
            array = np.full((n_options, len(price_types)), val)
            price_type_dict = {}
            
            for idx, px_type in enumerate(price_types):
                arr_col = array[:, idx]
                price_type_dict[px_type] = arr_col
                
            metric_pType_array_dict[metric] = price_type_dict
        else:
            #array = np.arange(1, n_options+1).reshape(n_options,1)
            array = np.full((n_options, 1), val)
            price_type_dict = {}
            for px_type in price_types:
                price_type_dict[px_type] = array
                
            metric_pType_array_dict[metric] = price_type_dict
        full_array[metric] = array
        for n in range(n_options):
            idx_metric_array_dict[n][metric] = array[n,:]
    return metric_pType_array_dict, idx_metric_array_dict, full_array