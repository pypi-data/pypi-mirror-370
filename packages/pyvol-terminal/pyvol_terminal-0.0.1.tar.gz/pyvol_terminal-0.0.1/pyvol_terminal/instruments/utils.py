from __future__ import annotations 
from typing import List, Optional, Any, Tuple, Union, Dict, TYPE_CHECKING, Callable
if TYPE_CHECKING:
    from instruments.instruments import Option, ABCInstrument, Future, Spot, ABCNestedInstrument
    from pandas import DataFrame
import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from collections import defaultdict

    
@dataclass(slots=True, frozen=True)
class BaseMap:
    index_name_map: Dict
    name_index_map: Dict
    
    
@dataclass(slots=True, frozen=True, kw_only=True)
class OptionMap(BaseMap):
    put_call_map: Dict[str, str] = field(default_factory=dict)
    underlying_ticker_map: Dict[str, List[str]] = field(default_factory=dict)
    name_underlying_map: Dict[str, str] = field(default_factory=dict)
    expiry_strike_map: Dict[float, np.ndarray] = field(default_factory=dict)
    strike_expiry_map: Dict[float, np.ndarray] = field(default_factory=dict)
    expiry_instrument_map: Dict[str, List[str]] = field(default_factory=dict)
    strike_instrument_map: Dict[float, List[str]] = field(default_factory=dict)
    expiry_strike_instrument_map: Dict[str, Dict[float, List[str]]] = field(default_factory=dict)
    strike_expiry_instrument_map: Dict[float, Dict[str, List[str]]] = field(default_factory=dict)
    expiry_strike_type_instrument_map: Dict[float, Dict[float, Dict[str, str]]] = field(default_factory=dict)
    strike_expiry_type_instrument_map: Dict[float, Dict[str, Dict[str, str]]] = field(default_factory=dict)
    type_expiry_strike_instrument_map: Dict[str, Dict[float, Dict[float, str]]] = field(default_factory=dict)

@dataclass(slots=True, frozen=True)
class ManagerMap:
    name_type_map: Dict[str, str] = field(default_factory=dict)

@dataclass(slots=True)
class InstrumentContainer:
    objects: Dict[str, ABCInstrument]
    price_types: List[str,]
    maps: OptionMap
    instrument_type: str
    original_data: pd.DataFrame
    
    def get_objects(self) -> List[ABCInstrument]:
        return list(self.objects.values())
    
@dataclass(slots=True)
class NestedInstrumentContainer:
    objects: Dict[str, ABCNestedInstrument]
    price_types: List[str,]
    maps: Dict[str, Any]
    instrument_type: str
    original_data: pd.DataFrame
    
    def get_objects(self) -> List[ABCInstrument]:
        return self.get_nested_object()
    
    def get_nested_object(self):
        total_objects = []
        for obj in self.objects.values():
            total_objects.append(obj.get_nested_objects())
        return total_objects
    

    

@dataclass(slots=True, kw_only=True)
class InstrumentManager:
    config: Dict[str, Dict[str, Any]]
    name: str = field(default=None)
    manager_map: ManagerMap
    all_instrument_objects: Dict[str, ABCInstrument] = field(default_factory=dict)
    spot_instrument_container: InstrumentContainer = field(default=None)
    futures_instrument_container: InstrumentContainer = field(default=None)
    options_instrument_container: InstrumentContainer = field(default=None)
    
    def __post_init__(self):
        if self.name is None:
            if not self.spot_instrument_container is None:
                self.name = [obj.ticker for obj in self.spot_instrument_container.get_objects()][0]
            if self.name is None and not self.futures_instrument_container is None:
                self.name = longest_common_prefix([obj.ticker for obj in self.futures_instrument_container.get_objects()])
            if self.name is None and not self.options_instrument_container is None:
                self.name = longest_common_prefix([obj.ticker for obj in self.options_instrument_container.get_objects()])

    def update_metric_calculations(self,
                                   flag: bool,
                                   option_ptype: str,
                                   underyling_ptype: str
                                   ):
        for option in self.options_instrument_container.get_objects():
            if flag:
                option.add_active_ivol_ptype(metric_calculation)
            else:
                option.remove_active_ivol_ptype(metric_calculation)
    

def longest_common_prefix(strings: List[str]):
    prefix = strings[0]
    for s in strings[1:]:
        while not s.startswith(prefix):
            prefix = prefix[:-1]
            if not prefix:
                return ""
    return prefix