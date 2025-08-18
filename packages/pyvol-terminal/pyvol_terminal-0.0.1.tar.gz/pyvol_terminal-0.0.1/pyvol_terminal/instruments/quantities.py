from __future__ import annotations 
from typing import List, Optional, Tuple, Union, Dict, TYPE_CHECKING, Callable, Any
from dataclasses import dataclass, field
import numpy as np

from ..engines.option_engines.base import ABCEuroEngine
from abc import ABC, abstractmethod


__GREEKS__ = {"delta" : np.nan,
              "gamma" : np.nan,
              "vega" : np.nan,
              "theta" : np.nan,
              "rho" : np.nan,
              }

__MONEYNESS__ = {"moneyness" : np.nan,
                 "log_moneyness" : np.nan,
                 "standardised_moneyness" : np.nan,
                 "forward_moneyness" : np.nan,
                 "discounted_moneyness" : np.nan,
                 }


@dataclass(slots=True)
class ABCMetric(ABC):
    targets: List[str] = field(default_factory=list)
    
    def get_targets(self): return self.targets
    
    def add_target(self, target):
        self.targets.append(target)
    
    def remove_target(self, target):
        self.targets.remove(target)
    
    @abstractmethod
    def update(self, *args, **kwargs): ...
    
    


@dataclass(slots=True, frozen=True, kw_only=True)
class IVOLConfig:
    px_type_option: str
    px_type_underlying: str
    



        
@dataclass(slots=True)
class Greeks(ABCMetric):
    delta: float=np.nan
    gamma: float=np.nan
    vega: float=np.nan
    theta: float=np.nan
    rho: float=np.nan
    
    def update(self, ivol):
        self.ivol=ivol


@dataclass(slots=True, kw_only=True)
class Moneyness(ABCMetric):
    moneyness: float=np.nan
    log_moneyness: float=np.nan
    standardised_moneyness: float=np.nan
    forward_moneyness: float=np.nan
    discounted_moneyness: float=np.nan
        
    
    
@dataclass(slots=True, kw_only=True)
class IVOLMetrics:
    
    """
    convenience class to help manage metrics that need to be calculated and prevent double calculation etc 

    """
    
    config: IVOLConfig
    last_ts: float=np.nan
    ivol: float=np.nan
    greeks: Greeks = field(default_factory=lambda : __GREEKS__.copy())
    moneyness: Moneyness = field(default_factory=lambda : __MONEYNESS__.copy())
    
    _cachedParams: Dict[str, float] = field(default_factory=dict)
    _cacheTsTol=4.

    def get_req_metrics(self):
        return self.greeks.targets + self.moneyness.targets 
    
    def set_metrics(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self.greeks, k, v)
        
    def update(self, ivol, cache: Dict[str, float]=None):
        self.ivol=ivol
        if not cache is None:
            self._cachedParams = cache.copy()

    def is_cached(self,
                  update_option: Tuple[float, float]=None,
                  update_under: Tuple[float, float]=None,
                  ) -> bool:
        
        if not update_option is None:
            return self._cacheTsTol > update_option[0] - self._cachedParams["option"][0] \
                and update_option[1] == self._cachedParams["option"][1]
        if not update_under is None:
            return self._cacheTsTol > update_under[0] - self._cachedParams["underlying"][0] \
                and update_under[1] == self._cachedParams["underlying"][1]

    
@dataclass(slots=True, kw_only=True)
class GreeksN(Greeks):
    Ndelta: float=np.nan
    




@dataclass(slots=True, kw_only=True)
class OptionState:
    constants: Dict[str, str|float]
    OTM: bool=None
    
    def check_set_get(self, attr, px_underlying):
        if attr == "OTM":
            if self.constants["flag"] == "c":
                self.OTM = px_underlying < self.constants["strike"]
            else:
                self.OTM = px_underlying > self.constants["strike"]            
            return self.OTM
    

@dataclass(slots=True, kw_only=True)
class BarrierOptionState(OptionState):
    knocked_in: bool=None
