from __future__ import annotations 
from typing import List, Optional, Tuple, Union, Dict, TYPE_CHECKING, Callable, Any
import numpy as np
from abc import ABC, abstractmethod
from scipy import interpolate


class Abstract3DInterpolator(ABC):
    def __init__(self, n_x, n_y):
        self._n_x, self._n_y= n_x, n_y
        self._fitted=False
    
    def grid_shape(self) -> Tuple[int, int]:
        return self._n_x, self._n_y
    
    @abstractmethod
    def fit(self,
            x: np.ndarray,
            y: np.ndarray,
            z: np.ndarray,
            *args: Tuple[Any],
            **kwargs: Dict[str, Any]
            ) -> None:
        ...
        
    @abstractmethod
    def evaluate(self,
                 xi: np.ndarray,
                 yi: np.ndarray,
                 *args: Tuple[Any],
                 **kwargs: Dict[str, Any]
                 ) -> np.ndarray:
        ...


class CustomRBFInterpolator(Abstract3DInterpolator, interpolate.RBFInterpolator):
    def __init__(self, n_x, n_y):
        Abstract3DInterpolator.__init__(self, n_x, n_y)
        
    def fit(self,
            x: np.ndarray,
            y: np.ndarray,
            z: np.ndarray, 
            args: Tuple[Any],
            kwargs: Dict[str, Any]
            ) -> None:
        x = x.flatten()
        y = y.flatten()
        z = z.flatten()
        points = np.column_stack((x, y))

        interpolate.RBFInterpolator.__init__(self, points, z, *args, **kwargs)
        self._fitted = True      
        
          
    def evaluate(self,
                 xi: np.ndarray,
                 yi: np.ndarray,
                 args: Tuple[Any],
                 kwargs: Dict[str, Any]
                 ) -> np.ndarray:
        if not self._fitted:
            raise RuntimeError("Call `fit` before `evaluate`.")

        xi, yi = np.meshgrid(xi, yi)
        points = np.column_stack((xi.flatten(), yi.flatten()))
        new_vals = self(points).reshape(*self.grid_shape())
        return new_vals
    
    
class CustomBSplineInterpolator(Abstract3DInterpolator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tck = None
    
    def fit(self,
            x: np.ndarray,
            y: np.ndarray,
            z: np.ndarray,
            args: Tuple[Any],
            kwargs: Dict[str, Any]
            ) -> None:
        kwargs["s"] = x.size
        self.tck = interpolate.bisplrep(x, y, z, *args, **kwargs) 
        self._fitted = True     
        
    def evaluate(self,
                 xi: np.ndarray,
                 yi: np.ndarray,
                 args: Tuple[Any],
                 kwargs: Dict[str, Any]
                 ) -> np.ndarray:
        if not self._fitted:
            raise RuntimeError("Call `fit` before `evaluate`.")

        x_vals = np.unique(xi)
        y_vals = np.unique(yi)
       #x_vals.sort()
        #y_vals.sort()
        return interpolate.bisplev(x_vals, y_vals, self.tck, *args, **kwargs) 


class CustomSplineInterpolator:
    def __init__(self, ):
        self.x=None
        self.y=None
        self.z=None
        self.spline=None
        self.k=2
    
    def fit(self,
            x: np.ndarray,
            y: np.ndarray,
            ) -> None:
        self.spline = interpolate.make_interp_spline(x, y, k=self.k)
        self._fitted = True     
    
    def evaluate(self, xi):
        return self.spline(xi)