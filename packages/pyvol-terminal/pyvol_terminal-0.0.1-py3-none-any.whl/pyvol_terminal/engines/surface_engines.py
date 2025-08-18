from __future__ import annotations 
from typing import List, Optional, Tuple, Union, Dict, TYPE_CHECKING, Callable, Any
if TYPE_CHECKING:
    from ..data_classes.classes import OptionChain
    from pyvol_terminal.engines.interpolation_engines import Abstract3DInterpolator

import numpy as np
from abc import ABC, abstractmethod
from scipy import interpolate
from ..utils import filter_nans_on_z, filter_nans_on_z_OTM
import math
import time


class AbstractSurfaceEngine(ABC):
    def __init__(self, n_tolerance=5, *args, **kwargs):
        self.n_tolerance=n_tolerance
        self._calibrated=False
        
    def valid_calibration(self):
        return self._calibrated
    
    @abstractmethod
    def calibrate(self, *args, **kwargs) -> None:
        ...
        
    @abstractmethod
    def evaluate(self,
                 xi: np.ndarray,
                 yi: np.ndarray,
                 *args: Tuple[Any],
                 **kwargs: Dict[str, Any]
                 ) -> np.ndarray:
        ...
        

class ATMWeightedSurfaceEngine(AbstractSurfaceEngine):
    def __init__(self, *args, **kwargs):
        #super(ATMWeightedSurfaceEngine, self).__init__(*args, **kwargs)
        super().__init__(*args, **kwargs)
        self.kx, self.ky = 3, 3
    
    def calibrate(self,
                  x: np.ndarray,
                  y: np.ndarray,
                  z: np.ndarray,
                  OTM: np.ndarray,
                  ) -> None:
        x, y, OTM, z = filter_nans_on_z_OTM(x, y, OTM, z)
        if x.size < self.n_tolerance:
            self._calibrated=False
            return
        else:
            m = x.size
            
            if m >= (self.kx+1) * (self.ky+1):
                
                y = (y - time.time()) / 3600 / 24 / 365
                z *=z
                
                self.tck = interpolate.bisplrep(x, y, z, kx=self.kx, ky=self.ky, s=0.5 * (m-math.sqrt(2*m) + m+math.sqrt(2*m))) 
                self._calibrated=True
            else:
                self._calibrated=False
    

    
    def evaluate(self,
                 xi: np.ndarray,
                 yi: np.ndarray,
                 *args: Tuple[Any],
                 **kwargs: Dict[str, Any]
                 ) -> np.ndarray:
        if not self._calibrated:
            return 
        x_vals = np.unique(xi)
        y_vals = np.unique(yi)
        y_vals = np.unique(yi)
        y_vals = (y_vals - time.time()) / 3600 / 24 / 365
        variance = interpolate.bisplev(x_vals, y_vals, self.tck, *args, **kwargs) 
        return np.sqrt(variance)
