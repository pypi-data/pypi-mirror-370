from __future__ import annotations 
from typing import List, Optional, Tuple, Union, Dict, TYPE_CHECKING, Callable, Any
if TYPE_CHECKING:
    from instruments.instruments import Option
    from pandas import DataFrame
    from data_classes.classes import BaseDomain, Domain, OptionChain, VolatilityData
    from ..axis.axis_utils import MetricAxisEngine
    from ..engines.interpolation_engines import Abstract3DInterpolator

import numpy as np
import copy
from pyvol_terminal import metric_attributes
from . import classes, containers
from pyvol_terminal.axis import axis_utils as axis_utils
import functools




def _create_scatter_surface_dataclasses(px_type: str,
                                        domain: Domain,
                                        metric_axis_engine: MetricAxisEngine,
                                        interpolation_engine,
                                        n_options,
                                        name_index_map
                                        ) -> VolatilityData:
    raw_opt_kwargs = {"n_instruments" : n_options,
                      "px_type" : px_type,
                      "name_index_map" : name_index_map,
                      }
    
    greeks = metric_attributes.greeks_attr()
    moneyness=metric_attributes.moneyness_attr()
    greeks_container={}
    moneyness_container={}
    for metric in metric_attributes.get_metric_attr_all():
        if metric == "OTM" or metric == "call_flag":
            val = False
            dtype=bool
        else:
            val=np.nan
            dtype=float
        arr = np.full(n_options, val, dtype=dtype)
        if metric in greeks:
            greeks_container[metric]=arr
        elif metric in moneyness:
            moneyness_container[metric]=arr
        else:
            raw_opt_kwargs[metric]=arr
    
    greeks_container = classes.Greeks(**greeks_container)
    moneyness_container = classes.Moneyness(**moneyness_container)
    
    raw_opt_kwargs["greeks"] = greeks_container
    raw_opt_kwargs["moneyess"] = moneyness_container
    del raw_opt_kwargs["px_type"]
    raw_options = classes.OptionChain(**raw_opt_kwargs)
        
    points_kwargs = {"px_type" : px_type,
                      "x" : domain.x,
                      "y" : domain.y,
                      "z" : raw_options.ivol,
                      "metric_axis_engine" : metric_axis_engine
                      }
    del points_kwargs["px_type"]
    points = classes.Points(**points_kwargs)
    
    
    
    surface_kwargs = {"px_type" : px_type,
                      "x_p" : domain.x,
                      "y_p" : domain.y,
                      "z_p" : raw_options.ivol,
                      "metric_axis_engine" : metric_axis_engine
                      }
    
    surface_kwargs = copy.deepcopy(surface_kwargs)
    del surface_kwargs["px_type"]
    surface_kwargs["interpolator"] = interpolation_engine
    
    surface = classes.Surface.from_points(points, interpolation_engine)
    
    skew = classes.Slice.from_surface(surface,
                                      "xz",
                                      )
    term = classes.Slice.from_surface(surface,
                                      "yz",
                                      )
    volatility_data = classes.VolatilityData(px_type=px_type,
                                            raw_options=raw_options,
                                            points=points,
                                            surface=surface,
                                            skew=skew,
                                            term=term,)
    return volatility_data
    #return raw, scatter, surface, skew, term
    

    
def create_surface_dataclasses(all_price_types: List[str],
                               df: DataFrame,
                               domain: Domain,
                               metric_axis_engine,
                               option_objects: List[Option],
                               interpolation_engine_container: Dict[str, Abstract3DInterpolator]
                               ) -> Dict[str, VolatilityData]:
    n_options = df.shape[0]
    name_index_map = {v: k for k, v in df["ticker"].to_dict().items()}
    
    dataclass_type_container = {"raw" : None,
                                "scatter" : None,
                                "surface" : None,
                                "skew" : None,
                                "term" : None}
    
    volatility_data_container = {px_type : copy.deepcopy(dataclass_type_container) for px_type in all_price_types}

    for px_type in all_price_types:
        domain = copy.deepcopy(domain)
        volatility_data = _create_scatter_surface_dataclasses(px_type,
                                                                                domain,
                                                                                metric_axis_engine,
                                                                                interpolation_engine_container[px_type],
                                                                                n_options,
                                                                                name_index_map)
        volatility_data_container[px_type]["raw"] = raw
        volatility_data_container[px_type]["scatter"] = scatter
        volatility_data_container[px_type]["surface"] = surface
        volatility_data_container[px_type]["skew"] = skew
        volatility_data_container[px_type]["term"] = term

        for option_object in option_objects:
            option_object.add_child_derivative_callback(raw.update_from_instrument_object)

    return volatility_data_container
    
def create_domains(df):    
    base_domain = classes.BaseDomain(df["strike"].values, df["expiry"].values, "Strike", "Expiry")    
    domain = classes.Domain(base_domain)
    return base_domain, domain
    
def create_slice_container(df, price_types, config):
    n_options = df.shape[0]
    name_index_map = {v: k for k, v in df["ticker"].to_dict().items()}
    
    KT_idx_map={}
    for idx, kt in enumerate(zip(df["strike"].values, df["expiry"].values)):
        KT_idx_map[kt] = idx

    base_domain = classes.BaseDomain(df["strike"].values, df["expiry"].values, "Strike", "Expiry")    
    domain = classes.Domain(base_domain)
    metric_axis_engine=axis_utils.MetricAxisEngine(base_domain.strike,
                                                   base_domain.expiry,
                                                   "Strike",
                                                   "Expiry",
                                                   "Implied Volatility"
                                                   )
    interpolator_engine = config["interpolation_engine_container"]
    
    raw_objects={}
    slice_objects={}
    dataclass_objects = {}
    domain_objects = {}

    displayed_price_types = ["mid"]
    for px_type in price_types:
        domain, raw, scatter, base_dataclass_kwargs, surface_kwargs = _create_surface_dataclass_args(px_type,
                                                                                        domain,
                                                                                        config["interpolation_engine_container"],
                                                                                        n_options,
                                                                                        name_index_map)
        surface = classes.Surface(**surface_kwargs)
        slice_kwargs = copy.deepcopy(base_dataclass_kwargs)
        slice_kwargs["surface"] = surface
        slice_kwargs["base_domain"] = base_domain
        domain_objects[px_type] = domain.x_vect if config["axis_direction"] == "xz" else domain.y_vect
        slice_kwargs["surface_axis_directions"] = config["axis_direction"]
        slice_kwargs["scatter"] = scatter
        
        
        slices = classes.Slice(**slice_kwargs)
        slice_objects[px_type] = slices
        raw_objects[px_type] = raw
        dataclass_objects[px_type] = {"slices" : slices}

    args = [price_types,
            displayed_price_types,
            df["ticker"].to_list(),
            metric_axis_engine,
            domain,
            raw_objects,
            [slice_objects],
            interpolator_engine,
            config["axis_direction"]]
    
    kwargs = {"all_price_types" : price_types,
              "displayed_price_types" : displayed_price_types,
              "instrument_names" : df["ticker"].to_list(),
              "metric_axis_engine" : metric_axis_engine,
              "domain" : domain,
              "raw" : raw_objects,
              "dataclasses" : dataclass_objects,
              "interpolator_engine" : interpolator_engine,
              "axis_direction" : config["axis_direction"],
              "slice_container" : slice_objects,
              "domain_vec" : domain_objects}
    
    
    
    return containers.SliceContainer(**kwargs)


def create_smile_container(df, price_types, config):
    return create_slice_container(df, price_types, config, 0)

def create_term_container(df, price_types, config):
    return create_slice_container(df, price_types, config, 1)



def _create_surface_dataclass_args(px_type, instrument_manager, domain, interpolation_engine, n_options, name_index_map):
        domain = copy.deepcopy(domain)
        args = [n_options, name_index_map]
        for metric in metric_attributes.get_metric_attr():
            if metric == "OTM" or metric == "call_flag":
                val = False
                dtype = bool
            else:
                val = np.nan
                dtype=float
            arr = np.full(n_options, val, dtype=dtype)
            args.append(arr) 
        raw = classes.OptionChain(*args)
        
        for option_object in instrument_manager.options_instrument_container.get_objects():
            option_object.add_update_callback(lambda px_type: option_object.get_all_metrics_price_type(px_type))
        
        base_dataclass_kwargs = {"px_type" : px_type,
                                 "x" : domain.x,
                                 "y" : domain.y,
                                 "z" : raw.ivol,
                                 }
        scatter = classes.Points(**base_dataclass_kwargs)
        
        surface_kwargs = copy.deepcopy(base_dataclass_kwargs)
        
        surface_kwargs["interpolator"] = copy.deepcopy(interpolation_engine["engine"])

        args=[px_type,domain.x, domain.y, raw.ivol, copy.deepcopy(interpolation_engine["engine"])]
        return domain, raw, scatter, base_dataclass_kwargs, surface_kwargs



def create_surface_container(df, instrument_manager, price_types, config, include_scatter=False):
    n_options = df.shape[0]
    name_index_map = {v: k for k, v in df["ticker"].to_dict().items()}
    
    base_domain = classes.BaseDomain(df["strike"].values, df["expiry"].values, "Strike", "Expiry")    
    domain = classes.Domain(base_domain)
    
    raw_objects = {}
    domain_objects = {}
    surface_objects = {}
    scatter_objects = {}
    for px_type in price_types:
        domain, raw, scatter, _, surface_kwargs = _create_surface_dataclass_args(px_type,
                                                                                 instrument_manager,
                                                                    domain,
                                                                    config["interpolation_engine_container"],
                                                                    n_options,
                                                                    name_index_map)
        surface = classes.Surface(**surface_kwargs)
        raw_objects[px_type] = raw
        domain_objects[px_type] = domain
        scatter_objects[px_type] = scatter
        surface_objects[px_type] = surface
    
    displayed_price_types = ["mid"]
    metric_axis_engine=axis_utils.MetricAxisEngine(base_domain.strike, base_domain.expiry, "Strike", "Expiry", "Implied Volatility")
    
    kwargs = {"all_price_types" : price_types,
              "displayed_price_types" : displayed_price_types,
              "instrument_names" : df["ticker"].to_list(),
              "metric_axis_engine" : metric_axis_engine,
              "domain" : domain,
              "raw" : raw_objects,
              "surface_dataclasses" : surface_objects,
              "scatter_dataclasses" : scatter_objects}    
    return containers.SurfaceContainer(**kwargs)

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


def create_data_containers(df, instrument_manager, price_types, config_interface):
    data_container_manager = {}
    for interface, config in config_interface.items():
        match interface:
            case "Vol Table":
                container=create_surface_container(df, price_types, config)
            case "OMON":
                container=create_surface_container(df, price_types, config)
            case "Surface":
                container=create_surface_container(df, instrument_manager, price_types, config, include_scatter=True)
            case "Smile":
                container=create_slice_container(df, price_types, config)
            case "Term":
                container=create_slice_container(df, price_types, config)
        data_container_manager[interface] = container
    return data_container_manager

