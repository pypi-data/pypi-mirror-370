from __future__ import annotations 
from typing import List, Optional, Tuple, Union, Dict, TYPE_CHECKING, Callable
if TYPE_CHECKING:
    from instruments.instruments import Option
    from pyvol_terminal.engines.surface_engines import AbstractSurfaceEngine
    from quantities.engines import MetricAxisEngine

from dataclasses import dataclass, field
from dataclasses import InitVar
import numpy as np
from typing import Any, Dict, List, Optional
import warnings
from abc import ABC, abstractmethod
import time
from PySide6 import QtCore
from .. import utils
from ..instruments.quantities import IVOLConfig


def custom_showwarning(message, category, filename, lineno, file=None, line=None):
    print(f"UserWarning: {message} ({filename}, line {lineno})")
warnings.showwarning = custom_showwarning



@dataclass(slots=True, frozen=True)
class BaseDomain:
    strike: np.ndarray
    expiry: np.ndarray
    x_metric: str
    y_metric: str
    

@dataclass
class SquaredDomain:
    base_domain: BaseDomain
    x: np.ndarray = field(init=False, default_factory=lambda: np.array)
    y: np.ndarray = field(init=False, default_factory=lambda: np.array)
    x_vect: np.ndarray = field(init=False, default_factory=lambda: np.array)
    y_vect: np.ndarray = field(init=False, default_factory=lambda: np.array)

    def __post_init__(self):
        self.x_vect = np.unique(self.base_domain.strike)
        self.y_vect = np.unique(self.base_domain.expiry)
        self.x, self.y = np.meshgrid(self.x_vect, self.y_vect, indexing="xy")

        
@dataclass(slots=True)
class Domain:
    base_domain: BaseDomain
    x: np.ndarray = field(init=False, default_factory=lambda: np.array)
    y: np.ndarray = field(init=False, default_factory=lambda: np.array)
    x_vect: np.ndarray = field(init=False, default_factory=lambda: np.array)
    y_vect: np.ndarray = field(init=False, default_factory=lambda: np.array)
    x_mat: np.ndarray = field(init=False, default_factory=lambda: np.array)
    y_mat: np.ndarray = field(init=False, default_factory=lambda: np.array)
    z_mat: np.ndarray = field(init=False, default_factory=lambda: np.array)

    xy: np.ndarray = field(init=False, default_factory=lambda: np.array)
    idx_ij_mapping: Dict[int, tuple] = field(init=False, default_factory=dict)
    z_mat: float = field(init=False, default_factory=lambda: np.array)
    
    def __post_init__(self):
        self._create_domain(self.base_domain.strike.copy(), self.base_domain.expiry.copy())

    def _create_domain(self, x, y):
        self.x = x
        self.y = y
        self.xy = np.column_stack((self.x, self.y)) 

        self.x_vect = np.unique(self.base_domain.strike)
        self.y_vect = np.unique(self.base_domain.expiry)

        self.x_mat, self.y_mat = np.meshgrid(self.x_vect, self.y_vect, indexing="xy")
        self.z_mat = np.full(self.x_mat.shape, np.nan)
        
        self.idx_ij_mapping = {}
        
        for i in range(self.x_mat.shape[0]):
            for j in range(self.x_mat.shape[1]):
                match_idx = np.where((self.xy == [self.x_mat[i, j], self.y_mat[i, j]]).all(axis=1))[0]
                for idx in match_idx:
                    self.idx_ij_mapping[idx] = (i, j)

    def update_data(self, z, idx_map):
        for idx, ivol in zip(idx_map, z):
            if idx in self.idx_ij_mapping:
                i, j = self.idx_ij_mapping[idx]
                self.z_mat[i,j] = ivol 


@dataclass(slots=True, kw_only=True)
class DomainVect:
    base_domain: InitVar[BaseDomain]
    _x: np.ndarray = field(default=None)
    _y: np.ndarray = field(default=None)
    
    def __post_init__(self, base_domain: BaseDomain):
        self.update(base_domain.strike, base_domain.expiry)

    def limits(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        return np.nanmin(self._x), np.nanmax(self._x), np.nanmin(self._y), np.nanmax(self._y)
    
    def update(self, x, y):
        self._x = x
        self._y = y
    
    def data(self):
        return self._x, self._y
    

@dataclass(slots=True)
class BaseData:
    n_instruments: int
    px_type: str
    name_index_map: Dict[str, int]
    price: np.ndarray
    
        
@dataclass(slots=True)
class RawFutures(BaseData):
    OTM: np.ndarray


@dataclass(slots=True)
class _AbstractMetrics(ABC):
    
    @abstractmethod
    def update(self, **kwargs):
        ...


@dataclass(slots=True, kw_only=True)
class Greeks(_AbstractMetrics):
    delta: np.ndarray
    gamma: np.ndarray
    vega: np.ndarray
    theta: np.ndarray
    rho: np.ndarray
    
    def update(self,
               idx,
               delta,
               gamma,
               vega,
               theta,
               rho,
               ):
        self.delta[idx] = delta
        self.gamma[idx] = gamma
        self.vega[idx] = vega
        self.theta[idx] = theta
        self.rho[idx] = rho
    

@dataclass(slots=True, kw_only=True)
class Moneyness(_AbstractMetrics):
    moneyness: np.ndarray
    log_moneyness: np.ndarray
    forward_moneyness: np.ndarray
    standardised_moneyness: np.ndarray

    def update(self,
               idx,
               moneyness,
               log_moneyness,
               forward_moneyness,
               standardised_moneyness,

               ):
        self.moneyness[idx] = moneyness
        self.log_moneyness[idx] = log_moneyness
        self.forward_moneyness[idx] = forward_moneyness
        self.standardised_moneyness[idx] = standardised_moneyness

@dataclass(slots=True, kw_only=True, frozen=True)
class Specifications:
    strike: np.ndarray
    expiry: np.ndarray
    

@dataclass(slots=True, kw_only=True)
class OptionChain(BaseData):
    ivol_config: IVOLConfig
    ivol: np.ndarray
    
    greeks: Greeks
    moneyess: Moneyness
    OTM: np.ndarray
    call_flag: np.ndarray
    valid_price: np.ndarray
    underlying_px: np.ndarray
    
    def getDataKwargs(self):
        result = {field : getattr(self, field) for field in self.__dataclass_fields__ if not field in ["greeks", "moneyness"]}
        result = result | {field : getattr(self.greeks, field) for field in self.greeks.__dataclass_fields__}
        return result | {field : getattr(self.moneyess, field) for field in self.moneyess.__dataclass_fields__}

    def update_IVOL(self, idx, implied_volatility):
        self.ivol[idx] = implied_volatility
    
    def update_from_object(self, instrument_object: Option):
        idx = self.name_index_map[instrument_object.ticker]
        self.price[idx] = getattr(instrument_object, self.px_type)
        self.ivol[idx] = instrument_object.get_ivol(self.px_type)
        self.greeks.update(idx, *instrument_object.get_greeks(self.px_type))
        self.moneyess.update(idx, *instrument_object.moneyness_metrics(self.px_type))
        self.OTM[idx] = instrument_object.OTM
        self.call_flag[idx] = instrument_object.call_flag
        self.valid_price[idx] = instrument_object.valid_price
        self.underlying_px[idx] = instrument_object.underlying_px
    
    def update_all_metrics_name(self, ticker, price, ivol, delta, gamma, vega, theta, rho, moneyness,
                                log_moneyness, standardised_moneyness, OTM, call_flag, underlying_px, valid_price):
        idx = self.name_index_map[ticker]
        self.price[idx] = price
        self.ivol[idx] = ivol
        self.greeks.update(idx, delta, gamma, vega, theta, rho)
        self.moneyess.update(idx, moneyness, log_moneyness, standardised_moneyness)
        self.OTM[idx] = OTM
        self.call_flag[idx] = call_flag
        self.valid_price[idx] = valid_price
        self.underlying_px[idx] = underlying_px
    
    def update_with_instrument_object(self, idx, option_object, ivol, update_list):
            self.ivol[idx] = ivol
            for metric in update_list:    
                getattr(self, metric)[idx] = getattr(option_object, metric)


@dataclass(slots=True, kw_only=True)
class VolVector:
    option_chain: InitVar[OptionChain]
    strikes: np.ndarray
    expiry: np.ndarray
    domain: DomainVect
    metric_engine: MetricAxisEngine
    
    _x: np.ndarray = field(init=False)
    _y: np.ndarray = field(init=False)
    _z: np.ndarray = field(init=False)
    _OTM: np.ndarray = field(init=False)
    idx_map: np.ndarray = field(default=None)
    _domain_updated_callbacks: List[Callable] = field(default_factory=list)
    
    def __post_init__(self, option_chain: OptionChain):
        self.update(**option_chain.getDataKwargs())
    
    def add_domain_updated_callback(self, callback):
        self._domain_updated_callbacks.append(callback)
    
    def update(self, **option_chain_data_kwargs):
        self._x, self._y, self._z, self.idx_map = self.metric_engine.transform_values(self.strikes,
                                                                                      self.expiry,
                                                                                      **option_chain_data_kwargs,
                                                                                      )
        self._OTM=option_chain_data_kwargs["OTM"][self.idx_map]
        self.domain.update(self._x, self._y)

    def data(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        return *self.domain.data(), self._z
    
    def plot_item_kwargs(self):
        return {"pos" : np.column_stack((self._x, self._y, self._z))}
    
    def calibration_args(self):
        return *self.data(), self._OTM
    
    
    


@dataclass(slots=True, kw_only=True)
class AbstractDataClass(ABC):
    domain_vect: DomainVect
    x: np.ndarray = field(default=None)
    y: np.ndarray = field(default=None)
    z: np.ndarray = field(default=None)
    
    x_min: float = field(init=False)
    x_max: float = field(init=False)
    y_min: float = field(init=False, default=None)
    y_max: float = field(init=False, default=None)
    z_min: float = np.nan
    z_max: float = np.nan
    
    valid_values: bool = False
    _update_callbacks: List[Callable] = field(default_factory=lambda: [])

    def __post_init__(self):
        self.evaluate_domain_limits(*self.domain_vect.data())
        self.z_min, self.z_max = np.nan, np.nan 

    def add_update_callback(self, callback):
        self._update_callbacks.append(callback)
    
    def remove_update_callback(self, callback):
        self._update_callbacks.remove(callback)
    
    def update_callbacks(self):
        return self._update_callbacks
    
    def evaluate_domain_limits(self, x: np.ndarray=None, y: np.ndarray=None):
        if not x is None:
            if x.size > 0:
                self.x_min, self.x_max = np.min(x), np.max(x)
            else:
                self.x_min, self.x_max = np.nan, np.nan 
        if not y is None:
            if y.size > 0:
                self.y_min, self.y_max = np.min(y), np.max(y)
            else:
                self.y_min, self.y_max = np.nan, np.nan 

    def dataRange(self):
        dataRange=[]
        for axis in "xyz":
            data = getattr(self, axis)
            data = data[~np.isnan(data)]
            if data.size == 0:
                dataRange.append(None)
            else:
                dataRange.append((data.min(), data.max()))
        return dataRange
    
    def limits(self):
        lims=[self.x_min, self.x_max]
        if not self.y_min is None:
            lims.append(self.y_min)
            lims.append(self.y_max)
        if not self.z_min is None:
            lims.append(self.z_min)
            lims.append(self.z_max)
        return tuple(lims)

    
    def get_plotitem_args(self):
        return [self.px_type, self] 
    
    def set_data2(self, x=None, y=None, z=None):
        self.x, self.y, self.z = x, y, z
        
    @abstractmethod
    def data(self):...

    @abstractmethod
    def evaluate_from_engine(self, *args):...
    
    @abstractmethod
    def plot_item_kwargs(self) -> Dict[str, Any]:...


@dataclass(slots=True, kw_only=True)
class Points(AbstractDataClass):
    
    _last_valid: np.ndarray = field(default=None)
    
    def calculate_limits(self, x, y, z):
        self.evaluate_domain_limits(x, y)
        if np.any(~np.isnan(z)):
            self.z_min, self.z_max = np.nanmin(z), np.nanmax(z)
        else:
            self.z_min, self.z_max = np.nan, np.nan
    
    def data(self)->Tuple[np.ndarray, ...]:
        return *self.domain_vect.data(), self.z
    
    def evaluate_from_engine(self, surface_engine: AbstractSurfaceEngine):
        vals = [surface_engine.evaluate([xi], [yi]) for xi, yi in zip(self.domain_vect.data()[0], self.domain_vect.data()[1])]
        try:
            z = np.array(vals)
        except:
            self.valid_values=False
            return 
        if z.size == 0:
            self.valid_values=False
        else:        
            self.z=z
            self.valid_values=True
            self._last_valid=np.column_stack(self.data())
    
    def plot_item_kwargs(self):
        x, y, z = self.data()
        
        if x.shape != z.shape or y.shape != z.shape:
            if self._last_valid is not None:
                arr=self._last_valid
            else:
                arr = np.full((1, 3), np.nan)
        else:
            arr = np.column_stack((x, y, z))
            self._last_valid=arr
        return {"pos" : arr}


@dataclass(slots=True, kw_only=True)
class Surface(AbstractDataClass):
    n_x: int
    n_y: int
    
    def __post_init__(self):   
        self.update_domain(*self.domain_vect.data())
        self.z = np.full((self.n_x, self.n_y), np.nan)

    def plot_item_kwargs(self):
        return {"x" : self.x, "y" : self.y, "z" : self.z}

    def calculate_limits(self, x, y, z):
        self.evaluate_domain_limits(x, y)
        if np.any(~np.isnan(z)):
            self.z_min, self.z_max = np.nanmin(z), np.nanmax(z)
        else:
            self.z_min, self.z_max = np.nan, np.nan

    def verify_limits(self, x_min, x_max, y_min, y_max):
        if (self.x_min != x_min
            or self.x_max != x_max
            or self.y_min != y_min
            or self.y_max != y_max):

            self.x_min = x_min 
            self.x_max = x_max
            self.y_min = y_min
            self.y_max = y_max
            self.create_interpolation_domain(x_min, x_max, y_min, y_max)
    
    def invalid_surface_cleanup(self):
        self.valid_values=False
        self.z *= np.nan
        
    def set_interpolation_domain(self, x, y):
        self.x = x
        self.y = y
    
    def update_domain(self, x, y):
        self.x_min, self.x_max = np.nanmin(x), np.nanmax(x)
        self.y_min, self.y_max = np.nanmin(y), np.nanmax(y)
        self.create_interpolation_domain(*self.limits()[:4])
    
    def calculate_interpolation_domain(self, x_min, x_max, y_min, y_max, grid_shape):
        return np.linspace(x_min, x_max, grid_shape[0]), np.linspace(y_min, y_max, grid_shape[1])

    def create_interpolation_domain(self, x_min, x_max, y_min, y_max):
        self.x, self.y = self.calculate_interpolation_domain(x_min, x_max, y_min, y_max, (self.n_x, self.n_y))
             
    def _evaluate_surface(self, surface_engine: AbstractSurfaceEngine):
        try:
            self.z = surface_engine.evaluate(self.x, self.y)
        except Exception as e:
            print(f"The interpolator could not evaluate: {e}")
            self.invalid_surface_cleanup()
            return 
        
        self.valid_values = True
        self.z_min, self.z_max = np.min(self.z), np.max(self.z)
    
    def point_data(self):
        return self.x_p, self.y_p, self.z_p
          
    def evaluate_from_engine(self, surface_engine):
        """
        if z.size < 5:
            warnings.warn(exceptions.InsufficientDataWarning(f"Unable to interpolate: z has only {z.size} points (min 5 required)", 
                                                            code=100),
                        stacklevel=2  # Point to the caller's line
                        )
            _ = self.invalid_surface_cleanup()
        else:
        """
        self.verify_limits(*self.domain_vect.limits())
        self._evaluate_surface(surface_engine)
        if self.valid_values:
            for callback in self._update_callbacks:
                callback(self)
                    
    @classmethod
    def from_points(cls,
                    points: Points,
                    n_ticks: Tuple[int, int],
                   ) -> 'Surface':
        x, y = cls.calculate_interpolation_domain(cls, *points.limits()[:4], n_ticks)
        return cls(x=x,
                   y=y,
                   x_p=points.x,
                   y_p=points.y,
                   z_p=points.z,
                   n_x=n_ticks[0],
                   n_y=n_ticks[1],
                   )
        
    def data(self)->Tuple[np.ndarray, ...]:
        return self.x, self.y, self.z


@dataclass(slots=True, kw_only=True)
class VolatilityData:
    px_type: str
    
    vol_vector: VolVector
    scatter: Points = field(default=None)
    surface: Surface = field(default=None)
    skew: Slice = field(default=None)
    term: Slice = field(default=None)   
    _last_update: float = field(default_factory=lambda: time.time())
    
    def surface_children(self) -> Tuple[Slice, Slice]:
        return self.skew, self.term
    
    def get_dataclass(self, plot_type):
        match plot_type:
            case "surface":
                return self.surface
            case "scatter":
                return self.scatter
            case "skew":
                return self.skew
            case "term":
                return self.term



@dataclass(slots=True, kw_only=True)
class Slice(AbstractDataClass):
    #domain_vect=DomainVect
    axis_3D_directions: str
    name: str = field(default=None)
    
    xi: np.ndarray = field(default_factory=lambda: np.array([]))
    yi: np.ndarray = field(default_factory=lambda: np.array([]))
    
    perp_x_point: float|None = field(default=None)
    
    _last_engine: AbstractSurfaceEngine|None = field(default=None)
    _last_surface: Tuple[np.ndarray, np.ndarray, np.ndarray] = field(default=None)
    _qt_object: QtCore.QObject = field(default_factory=QtCore.QObject)
    _last_point: Tuple[float, float]|None = field(default=None)
    
    def update_from_surface(self,
                            surface: Surface
                            ):
        self._last_surface=surface.data()
        if not self._last_point is None:
            self.update_data(*self._last_surface,
                             *self._last_point)
        
    def set_perpendicular_x(self, point: float):
        self.perp_x_point=point
        self._update_point_axis()
    
    def _update_point_axis(self):
        xi, yi = self.domain_vect.data()
        if self.axis_3D_directions=="xz": 
            self.yi = [self.perp_x_point] * xi.size
        else:
            self.xi = [self.perp_x_point] * yi.size

    def update_domain(self, x, y):
        if self.axis_3D_directions=="xz": 
            self.x=x
            self.yi = [self.perp_x_point] * x.size
            self.xi=x
        else:
            self.x = y
            self.xi = [self.perp_x_point] * y.size
            self.yi=x
        
    def plot_item_kwargs(self):
        return {"x" : self. x, "y" : self.y}
        
    def update_point(self, *args):
        self._last_point = args[0], args[1]
        if not self._last_surface is None:
            self.update_data(*self._last_surface,
                             *self._last_point)
            for callback in self._update_callbacks:
                callback(self)
        
    def update_data(self,
                    x_surf: np.ndarray,
                    y_surf: np.ndarray,
                    z_surf: np.ndarray,
                    x_p: float,
                    y_p: float
                    ):
        
        line = utils.calculate_xy_lines(x_surf,
                                        y_surf,
                                        z_surf,
                                        x_p,
                                        y_p,
                                        self.axis_3D_directions=="xz"
                                        )
        if self.axis_3D_directions=="xz":
            self.x = line[:,0]
        else:
            self.x = line[:,1]
        
        self.y = line[:,2]
        self.valid_values=True
        
    def data(self):
        return self.x, self.y

    def connect(self, *args, **kwargs):
        return self._qt_object.connect(*args, **kwargs)
    
    def disconnect(self, *args, **kwargs):
        return self._qt_object.disconnect(*args, **kwargs)
    
    def evaluate_from_engine(self, *args):
        return            
    

@dataclass(slots=True, kw_only=True)
class SliceContainer:
    dependent_axis: int
    points: Points
    
    def get_slice(self, point: float):
        pass
            

@dataclass(slots=True, kw_only=True)
class Slices222(AbstractDataClass):
    surface: Surface = None
    surface_axis_directions: str = ""
    base_domain: InitVar[BaseDomain] = None
    scatter: Optional[Points] = field(init=True)
    displayed_slices: List[float] = field(init=False)
    slice_container: Dict[float, List[np.ndarray]] = field(init=False)
    n_x: int = field(init=False)
    domain_vec: np.ndarray = field(init=False)
    domain_idx_map: Dict[str, int] = field(init=False)
        
    def __post_init__(self, base_domain):
        if self.surface_axis_directions == "xz":
            self.domain_vec = np.unique(base_domain.expiry)
            domain_matrix = self.x
            self.n_x = self.surface.y.size
        else:
            self.domain_vec = np.unique(base_domain.strike)
            domain_matrix = self.y
            self.n_x = self.surface.x.size
            
        if self.domain_vec.size > 15:
            self.filter_domain(base_domain)

        self.domain_idx_map = {val: idx for idx, val in enumerate(self.domain_vec)}
        self.slice_container={}

        for x_val in self.domain_vec:
            self.slice_container[x_val] = np.full(self.n_x, np.nan)
        
    def filter_domain(self, base_domain):
        value_dict = {}
        for value in self.domain_vec:
            if self.surface_axis_directions == "xz":
                mask = base_domain.expiry == value
                filtered_domain = base_domain.expiry[mask]
            else:
                mask = base_domain.strike == value
                filtered_domain = base_domain.strike[mask]
            value_dict[value] = len(filtered_domain)
        top_12 = sorted(value_dict, key=value_dict.get, reverse=True)[:12]
        top_12 = np.sort(top_12)
        self.domain_vec = self.domain_vec[np.isin(self.domain_vec, top_12)]

    def evaluate_from_engine(self, x, y, z):
        if not self.scatter is None:
            self.scatter.evaluate_from_engine(x, y, z)
        self.surface.evaluate_from_engine(x, y, z)

        if not self.valid_values:
            return 
        else:
            self.update_slice(x, y, z)
    
    def _interpolate_slice(self, dependent_values, constant_values):
        if self.surface_axis_directions == "xz":
            z_interp = self.interpolator.evaluate(dependent_values, constant_values)
        else:
            z_interp = self.interpolator.evaluate(constant_values, dependent_values)

        if z_interp.ndim != 1:
            if z_interp.shape[1] == 1 or z_interp.shape[0] == 1:
                z_interp = z_interp.flatten()
            else:
                if self.surface_axis_directions=="yz":
                    z_interp = z_interp[0,:]
                else:
                    z_interp = z_interp[:,0]
        return z_interp

    def update_slice(self, x, y, z):
        dependent_values = x if self.surface_axis_directions == "xz" else y
        size = dependent_values.size
        constant_values = [np.nan] * size
        for constant_value in self.displayed_slices:
            constant_values[:] = [constant_value] * size
            z_interp = self._interpolate_slice(dependent_values, constant_values)        
