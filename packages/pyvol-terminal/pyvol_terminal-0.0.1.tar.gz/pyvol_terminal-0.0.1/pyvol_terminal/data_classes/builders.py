from __future__ import annotations 
from typing import List, Optional, Tuple, Union, Dict, TYPE_CHECKING, Callable, Any
if TYPE_CHECKING:
    from instruments.instruments import Option
    from instruments.utils import InstrumentManager
    from pandas import DataFrame
    from data_classes.classes import BaseDomain, Domain, OptionChain, VolatilityData, VolVector
    from quantities.engines import MetricAxisEngine
    
    from ..engines.interpolation_engines import Abstract3DInterpolator

import numpy as np
import copy
from pyvol_terminal import metric_attributes
from . import classes#, containers
from ..quantities import engines


def _create_scatter_surface_dataclasses(px_type: str,
                                        domain: Domain,
                                        n_options,
                                        name_index_map,
                                        metric_engine: MetricAxisEngine,
                                        n_ticks: Tuple[int, int]
                                        ) -> VolatilityData:
    raw_opt_kwargs = {"n_instruments" : n_options,
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
    option_chain = classes.OptionChain(**raw_opt_kwargs)
    
    vol_vector = classes.VolVector(option_chain=option_chain,
                                   strikes=domain.x,
                                   expiry=domain.y,
                                   metric_engine=metric_engine,
                                   )
    points_kwargs = {"x" : domain.x,
                     "y" : domain.y,
                     "z" : option_chain.ivol,
                     }
    points = classes.Points(**points_kwargs)

    surface_kwargs = {"vol_vector" : vol_vector,
                      "n_x" : n_ticks[0],
                      "n_y" : n_ticks[1],
                      }
    surface = classes.Surface(**surface_kwargs)                   
    skew = classes.Slice(vol_vector=vol_vector,
                    #    parent_dataclass=surface,
                         axis_3D_directions="xz",
                         )
    term = classes.Slice(vol_vector=vol_vector,
                     #    parent_dataclass=surface,
                        axis_3D_directions="yz",
                        )
    volatility_data = classes.VolatilityData(px_type=px_type,
                                            vol_vector=vol_vector,
                                            points=points,
                                            surface=surface,
                                            skew=skew,
                                            term=term)
    return volatility_data
    #return raw, scatter, surface, skew, term


def create_volatility_data_from_vol_vect(vol_vect_container: Dict[str, VolVector],
                                         n_ticks: Tuple[int, int]=(30,30),
                                         ) -> Dict[str, VolatilityData]:
    volatility_data_container = {}
    for px_type, vol_vect in vol_vect_container.items():
        domain = vol_vect.domain
        x, y, z = vol_vect.data()
        points_kwargs = {"x" : x,
                        "y" : y,
                        "z" : z,
                        "domain_vect" : domain,
                 #       "strikes" : vol_vect.strikes,
                 #       "expiry" : vol_vect.expiry,
                        }
        points = classes.Points(**points_kwargs)
    
        surface_kwargs = {"domain_vect" : domain,
                          "n_x" : n_ticks[0],
                          "n_y" : n_ticks[1],
                          }
        
        
        surface = classes.Surface(**surface_kwargs)
                                
        skew = classes.Slice(domain_vect=domain,
                          #   parent_dataclass=surface,
                             axis_3D_directions="xz",
                             name="skew"
                             )
        
        term = classes.Slice(domain_vect=domain,
                           #  parent_dataclass=surface,
                             axis_3D_directions="yz",
                             name="term"
                             )
        surface.add_update_callback(skew.update_from_surface)
        surface.add_update_callback(term.update_from_surface)

        volatility_data = classes.VolatilityData(px_type=px_type,
                                                vol_vector=vol_vect,
                                                scatter=points,
                                                surface=surface,
                                                skew=skew,
                                                term=term)
        volatility_data_container[px_type]=volatility_data
    return volatility_data_container

def create_parent_option_container(all_price_types: List[str],
                                   df: DataFrame,
                                   instrument_manager: InstrumentManager,
                                   ) -> Dict[str, OptionChain]:
    n_options = df.shape[0]
    
    name_index_map = {v: k for k, v in df["ticker"].to_dict().items()}
    raw_opt_kwargs = {"n_instruments" : n_options,
                      "name_index_map" : name_index_map,
                      }
    option_chain_container={}
    for px_type in all_price_types:
        greeks = metric_attributes.greeks_attr()
        moneyness=metric_attributes.moneyness_attr()
        greeks_container={}
        moneyness_container={}
        for metric in metric_attributes.get_metric_attr_all():
            if metric == "OTM" or metric == "call_flag":
                value = False
                dtype=bool
            else:
                value=np.nan
                dtype=float
            if metric not in ["strike", "expiry"]:
                arr = np.full(n_options, value, dtype=dtype)
            else:
                arr = df[metric].values
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
        raw_opt_kwargs["px_type"]=px_type
        """
        option_chain = classes.OptionChain(**raw_opt_kwargs)

        for option_object in instrument_manager.options_instrument_container.objects.values():
            option_object.add_array_callback(option_chain.update_from_object)
        
        option_chain_container[px_type]=option_chain
        """
        for px_type in all_price_types:
            option_chain_container[px_type]={px_type : None}
        
    return option_chain_container

def create_option_chain(option_ptype: str,
                        underlying_ptype: str
                        ) -> OptionChain:
        greeks = metric_attributes.greeks_attr()
        moneyness=metric_attributes.moneyness_attr()
        greeks_container={}
        moneyness_container={}
        for metric in metric_attributes.get_metric_attr_all():
            if metric == "OTM" or metric == "call_flag":
                value = False
                dtype=bool
            else:
                value=np.nan
                dtype=float
            if metric not in ["strike", "expiry"]:
                arr = np.full(n_options, value, dtype=dtype)
            else:
                arr = df[metric].values
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
        raw_opt_kwargs["px_type"]=px_type
        """
        option_chain = classes.OptionChain(**raw_opt_kwargs)

        for option_object in instrument_manager.options_instrument_container.objects.values():
            option_object.add_stucture_callback(option_chain.update_from_object)
        
        option_chain_container[px_type]=option_chain
        """
        for px_type in all_price_types:
            option_chain_container[px_type]={px_type : None}



def create_vol_vect_container(option_chain_container: Dict[str, Dict[str, OptionChain]],
                              ) -> Dict[str, VolVector]:
    option_chain = option_chain_container[list(option_chain_container.keys())[0]]
    strike = option_chain.strike
    expiry = option_chain.expiry
    base_domain = classes.BaseDomain(strike, expiry, "Strike", "Expiry")    
    
    
    domain = classes.Domain(base_domain)
    vol_vector_container={}
    
    for px_type, inner_opt_chain_container in option_chain_container.items():
        for px_type , option_chain in inner_opt_chain_container.items():
    
            metric_engine = engines.MetricAxisEngine(base_domain.strike,
                                                    base_domain.expiry,
                                                    "Strike",
                                                    "Expiry",
                                                    "Implied Volatility"
                                                    )
            domain_vect = classes.DomainVect(base_domain=base_domain)
            vol_vector = classes.VolVector(option_chain=option_chain,
                                           strikes=domain.x,
                                           expiry=domain.y,
                                           domain=domain_vect,
                                           metric_engine=metric_engine,
                                           )
            vol_vector_container[px_type]={px_type : vol_vector}
    return vol_vector_container
        


def create_vol_vect_container2222222(option_chain_container: Dict[str, OptionChain],
                              ) -> Dict[str, VolVector]:
    option_chain = option_chain_container[list(option_chain_container.keys())[0]]
    strike = option_chain.strike
    expiry = option_chain.expiry
    base_domain = classes.BaseDomain(strike, expiry, "Strike", "Expiry")    
    
    
    domain = classes.Domain(base_domain)
    
    metric_engine = engines.MetricAxisEngine(base_domain.strike,
                                             base_domain.expiry,
                                             "Strike",
                                             "Expiry",
                                             "Implied Volatility"
                                             )
    vol_vector_container={}
    for px_type, option_chain in option_chain_container.items():
        domain_vect = classes.DomainVect(base_domain=base_domain)
        vol_vector = classes.VolVector(option_chain=option_chain,
                                       strikes=domain.x,
                                       expiry=domain.y,
                                       domain=domain_vect,
                                       metric_engine=metric_engine,
                                       )
        vol_vector_container[px_type]=vol_vector
    return vol_vector_container



def create_surface_dataclasses(all_price_types: List[str],
                               df: DataFrame,
                               domain: Domain,
                               option_objects: List[Option],
                               metric_engine,
                               n_ticks: Tuple[int, int]
                               ) -> Dict[str, VolatilityData]:
    n_options = df.shape[0]
    name_index_map = {v: k for k, v in df["ticker"].to_dict().items()}
    
    dataclass_type_container = {"raw" : None,
                                "scatter" : None,
                                "surface" : None,
                                "skew" : None,
                                "term" : None
                                }
    
    volatility_data_container = {px_type : copy.deepcopy(dataclass_type_container) for px_type in all_price_types}

    for px_type in all_price_types:
        domain = copy.deepcopy(domain)
        volatility_data = _create_scatter_surface_dataclasses(px_type,
                                                                domain,
                                                                n_options,
                                                                name_index_map,
                                                                metric_engine,
                                                                n_ticks)
        volatility_data_container[px_type]=volatility_data

        for option_object in option_objects:
            option_object.add_child_derivative_callback(volatility_data.option_chain.update_from_instrument_object)

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
    metric_axis_engine=engines.MetricAxisEngine(base_domain.strike,
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
    metric_axis_engine=engines.MetricAxisEngine(base_domain.strike, base_domain.expiry, "Strike", "Expiry", "Implied Volatility")
    
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

