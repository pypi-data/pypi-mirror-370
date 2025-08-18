from __future__ import annotations 
from typing import List, Optional, Tuple, Union, Dict, TYPE_CHECKING, Callable, Any
if TYPE_CHECKING:
    from instruments.instruments import Option
    from engines.yield_engines.implied_engines import AbstractYieldEngine 

from abc import ABC, abstractmethod

class AbstractITMConversionEngine(ABC):
    
    @abstractmethod
    def ITM_ivol(otm_option: Option,
                 itm_option: Option
                 ) -> Tuple[float, float]:
        ...
    
class ITMConversionEngine(AbstractITMConversionEngine):
        
    def ITM_ivol(self,
                 otm_option: Option,
                 itm_option: Option
                 ) -> Tuple[float, float]:
        
        if otm_option.spread == 0:
            return None, None
            
        
        original_midpoint = otm_option.get_ivol("mid")
        original_output_range = otm_option.get_ivol("ask") - otm_option.get_ivol("bid")
        
        scale_factor = itm_option.spread / otm_option.spread
        new_output_range = original_output_range * scale_factor
        
        itm_ivol_bid = original_midpoint - new_output_range / 2
        itm_ivol_ask = original_midpoint + new_output_range / 2
        
        return itm_ivol_bid, itm_ivol_ask
