from __future__ import annotations 
from typing import List, Optional, Tuple, Union, Dict, TYPE_CHECKING, Callable, Any, Set
if TYPE_CHECKING:
    from pyvol_terminal.utils import AbstractValidPriceChecker
    from engines.yield_engines.implied_engines import AbstractYieldEngine 


import numpy as np
import math
from abc import ABC, abstractmethod
from scipy.stats import norm
from dataclasses import dataclass

import numpy as np
import math
from abc import ABC, abstractmethod
from scipy.stats import norm
from typing import Set, Dict


class ABCEuroEngine(ABC):
    
    _GREEK_REQUIREMENTS = {"delta" : {"d1",
                                     "N_flag_d1"
                                     },
                           "gamma" : {"d1",
                                     "phi_d1"
                                     },
                           "vega" : {"d1",
                                    "phi_d1"
                                    },
                           "theta": {"d1",
                                     "d2",
                                     "phi_d1",
                                     "N_flag_d1",
                                     "N_flag_d2"
                                     },
                           "rho" : {"d2",
                                   "N_flag_d2"
                                   }, 
                           "price": {"d1",
                                     "d2",
                                     "N_flag_d1",
                                     "N_flag_d2"
                                     }
                           }


    
    
    
    
    def __init__(self,
                 strike: float,
                 expiry: float,
                 flag_str: str,
                 flag_int: int=None,
                 interest_rate_engine: AbstractYieldEngine=None,
                 dividend_rate_engine: AbstractYieldEngine=None
                 ):
        self.strike=strike
        self.expiry=expiry
        self.flag=flag_str
        self.flag_str=flag_str
        self.interest_rate_engine=interest_rate_engine
        self.dividend_rate_engine=dividend_rate_engine
        self.IVOL_engine=None
        self.greek_engine_all=None
        self.greeks_engines={}
        self._cachedParams={"t" : np.nan,
                            "px_option" : np.nan,
                            "px_underlying" : np.nan,
                            "r" : np.nan,
                            "q" : np.nan,
                            }
        
        if self.dividend_rate_engine is None:
            self._dividend_off=True
        else:
            self._dividend_off=False
        
        if not flag_int is None:
            self.flag_int = flag_int
        else:
            self.flag_int = 1 if flag_str.lower() == "c" else -1
    
    
    def calculate_IVOL(self, timestamp, px_option, px_underlying): 
        self.internal_calculate_IVOL(timestamp, px_option, px_underlying)
    
    @abstractmethod
    def internal_calculate_IVOL(self, timestamp, price_opt, px_underlying): ...
    
    @abstractmethod
    def calculate_all_greeks(self, timestamp, IVOL, px_underlying): ...

    @abstractmethod
    def calculate_pair_metrics(self, *args, **kwargs): ...

    @abstractmethod
    def set_params(self, *args, **kwargs): ...
    
    def calculate(self,
                  greeks: Set[str],
                  **kwargs,
                  ) -> Dict[str, float]:
        if len(kwargs) >= 0:
            self.set_params(**kwargs)
        cache = self._calculate_intermediates(greeks)
        return self._compute_greeks(greeks, cache)

    @abstractmethod
    def _calculate_intermediates(self, greeks: Set[str]) -> Dict[str, float]: ...

    @abstractmethod
    def _compute_greeks(self, greeks: Set[str], cache: Dict[str, float]) -> Dict[str, float]: ...
    



    
