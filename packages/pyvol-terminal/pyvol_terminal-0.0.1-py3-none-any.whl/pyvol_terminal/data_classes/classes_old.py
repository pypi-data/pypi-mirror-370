from __future__ import annotations 
from pydantic.dataclasses import dataclass, Field
from dataclasses import InitVar
from pyvol_terminal.axis import axis_utils as axis_utils
import numpy as np
from pyvol_terminal import utils
from typing import Any, Dict, List, Optional
from pyvol_terminal import exceptions
import warnings
from abc import ABC, abstractmethod


def custom_showwarning(message, category, filename, lineno, file=None, line=None):
    print(f"UserWarning: {message} ({filename}, line {lineno})")
warnings.showwarning = custom_showwarning



class Config:
    arbitrary_types_allowed=True
    slots=True

        
class Config2:
    arbitrary_types_allowed = True
    frozen: True

    
class Config3:
    arbitrary_types_allowed=True
    kw_only=True
    slots=True


@dataclass(slots=True, config=Config2)
class BaseDomain:
    strike: np.ndarray
    expiry: np.ndarray
    x_metric: str
    y_metric: str
    

@dataclass(config=Config)
class SquaredDomain:
    base_domain: BaseDomain
    x: np.ndarray = Field(init=False, default_factory=lambda: np.array)
    y: np.ndarray = Field(init=False, default_factory=lambda: np.array)
    x_vect: np.ndarray = Field(init=False, default_factory=lambda: np.array)
    y_vect: np.ndarray = Field(init=False, default_factory=lambda: np.array)

    def __post_init__(self):
        self.x_vect = np.unique(self.base_domain.strike)
        self.y_vect = np.unique(self.base_domain.expiry)
        self.x, self.y = np.meshgrid(self.x_vect, self.y_vect, indexing="xy")

        
@dataclass(slots=True, config=Config)
class Domain:
    base_domain: BaseDomain
    x: np.ndarray = Field(init=False, default_factory=lambda: np.array)
    y: np.ndarray = Field(init=False, default_factory=lambda: np.array)
    x_vect: np.ndarray = Field(init=False, default_factory=lambda: np.array)
    y_vect: np.ndarray = Field(init=False, default_factory=lambda: np.array)
    x_mat: np.ndarray = Field(init=False, default_factory=lambda: np.array)
    y_mat: np.ndarray = Field(init=False, default_factory=lambda: np.array)
    z_mat: np.ndarray = Field(init=False, default_factory=lambda: np.array)

    xy: np.ndarray = Field(init=False, default_factory=lambda: np.array)
    idx_ij_mapping: Dict[int, tuple] = Field(init=False, default_factory=dict)
    z_mat: float = Field(init=False, default_factory=lambda: np.array)
    
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


@dataclass(config=Config)
class BaseData:
    n_instruments: int
    name_index_map: Dict[str, int]
    price: np.ndarray
    
        
@dataclass(config=Config)
class RawFutures(BaseData):
    OTM: np.ndarray


@dataclass(config=Config)
class Greeks:
    delta: np.ndarray
    delta_mag: np.ndarray
    gamma: np.ndarray
    vega: np.ndarray
    theta: np.ndarray
    rho: np.ndarray

@dataclass(config=Config)
class Moneyness:
    moneyness: np.ndarray
    log_moneyness: np.ndarray
    standardised_moneyness: np.ndarray



@dataclass(config=Config)
class RawOptions(BaseData):
    ivol: np.ndarray
    delta: np.ndarray
    delta_mag: np.ndarray
    gamma: np.ndarray
    vega: np.ndarray
    theta: np.ndarray
    rho: np.ndarray
    moneyness: np.ndarray
    log_moneyness: np.ndarray
    standardised_moneyness: np.ndarray
    OTM: np.ndarray
    call_flag: np.ndarray
    valid_price: np.ndarray
    underlying_px: np.ndarray
    
    def getDataKwargs(self):
        return {field: getattr(self, field) for field in self.__dataclass_fields__}

    def update_IVOL(self, idx, implied_volatility):
        self.ivol[idx] = implied_volatility
    
    def update_all_metrics_name(self, ticker, price, ivol, delta, delta_mag, gamma, vega, theta, rho, moneyness,
                                log_moneyness, standardised_moneyness, OTM, call_flag, underlying_px, valid_price):
        idx = self.name_index_map[ticker]
        self.price[idx] = price
        self.ivol[idx] = ivol
        self.delta[idx] = delta
        self.delta_mag[idx] = delta_mag
        self.gamma[idx] = gamma
        self.vega[idx] = vega
        self.theta[idx] = theta
        self.rho[idx] = rho
        self.moneyness[idx] = moneyness
        self.log_moneyness[idx] = log_moneyness
        self.standardised_moneyness[idx] = standardised_moneyness
        self.OTM[idx] = OTM
        self.call_flag[idx] = call_flag
        self.valid_price[idx] = valid_price
        self.underlying_px[idx] = underlying_px
    
    def update_all_metrics(self, idx, jdx, ivol, delta, delta_mag, gamma, vega, moneyness,
                           log_moneyness, standardised_moneyness, OTM, valid_price, underlying_px):
        self.ivol[idx] = ivol[jdx]
        self.delta[idx] = delta[jdx]
        self.delta_mag[idx] = delta_mag[jdx]
        self.gamma[idx] = gamma[jdx]
        self.vega[idx] = vega[jdx]
        self.moneyness[idx] = moneyness
        self.log_moneyness[idx] = log_moneyness
        self.standardised_moneyness[idx] = standardised_moneyness[jdx]
        self.OTM[idx] = OTM
        self.valid_price[idx]=valid_price
        self.underlying_px[idx]=underlying_px
    
    def update_with_instrument_object(self, idx, option_object, ivol, update_list):
            self.ivol[idx] = ivol
            for metric in update_list:    
                getattr(self, metric)[idx] = getattr(option_object, metric)
                
@dataclass(config=Config3)
class BaseDataClass(ABC):
    px_type: str
    x: np.ndarray 
    y: np.ndarray 
    z: np.ndarray   
    metric_axis_engine: "axis_utils.MetricAxisEngine"
    
    x_min: float = Field(init=False)
    x_max: float = Field(init=False)
    y_min: float = Field(init=False)
    y_max: float = Field(init=False)
    z_min: float = np.nan
    z_max: float = np.nan
    valid_values: bool = False
    
    def __post_init__(self):
        self.calculate_domain(self.x, self.y)
        self.z_min, self.z_max = np.nan, np.nan 
    
    def calculate_domain(self, x, y):
        if x.size > 0:
            self.x_min, self.x_max = np.min(x), np.max(x)
        else:
            self.x_min, self.x_max = np.nan, np.nan 
        if y.size > 0:
            self.y_min, self.y_max = np.min(y), np.max(y)
        else:
            self.y_min, self.y_max = np.nan, np.nan 

    def get_limits(self):
        return self.x_min, self.x_max, self.y_min, self.y_max, self.z_min, self.z_max

    def getData(self):
        return self.x, self.y, self.z
    
    def get_plotitem_args(self):
        return [self.px_type, self] 

    def update_from_raw(self, raw):
        x, y, z, _ = self.metric_axis_engine.transform_values(raw)
        x, y, z = utils.filter_nans_on_z(x, y, z)
        self.update_data(x, y, z)
    
    def setData(self, x, y, z):
        self.x, self.y, self.z = x, y, z    
    
    @abstractmethod
    def update_data(self, x, y, z):
        pass


@dataclass(config=Config3)
class Scatter(BaseDataClass):
    
    def calculate_limits(self, x, y, z):
        self.calculate_domain(x, y)
        if any(~np.isnan(z)):
            self.z_min, self.z_max = np.nanmin(z), np.nanmax(z)
        else:
            self.z_min, self.z_max = np.nan, np.nan
    
    def update_data(self, x, y, z):
        if z.size == 0:
            self.valid_values=False
        else:        
            self.x, self.y, self.z = x, y, z
            self.valid_values=True
            self.calculate_limits(self.x, self.y, self.z)
            
    def getDataKwargs(self):
        x, y, z = super().getData()
        return {"pos" :np.column_stack((x, y, z))}

@dataclass(config=Config3)
class Surface(BaseDataClass):
    interpolator: Any = None
    n_x: int = 50
    n_y: int = 50
    last_interpolation_attempt_valid: bool = Field(init=False)
    
    def __post_init__(self):   
        self.create_interpolation_domain(self.x.min(),
                                         self.x.max(),
                                         self.y.min(),
                                         self.y.max(),
                                         )
        self.z = np.full((self.n_x, self.n_y), np.nan)
        self.calculate_domain(self.x, self.y)

    def getDataKwargs(self):
        return {"x" : self.x, "y" : self.y, "z" : self.z}

    def calculate_limits(self, x, y, z):
        self.calculate_domain(x, y)
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
        
    def create_interpolation_domain(self, x_min, x_max, y_min, y_max):
        self.x = np.linspace(x_min, x_max, self.n_x)
        self.y = np.linspace(y_min, y_max, self.n_y)
             
    def _interpolate_surface(self, x, y, z):
        try:
            self.interpolator.fit(x, y, z)                
        except Exception as e:
            print(f"The interpolator could not fit: {e}")
            self.invalid_surface_cleanup()
            self.last_interpolation_attempt_valid=False
            return
        
        try:
            self.z = self.interpolator.evaluate(self.x, self.y)

        except Exception as e:
            print(f"The interpolator could not evaluate: {e}")
            self.invalid_surface_cleanup()
            self.last_interpolation_attempt_valid=False
            return
        
        self.last_interpolation_attempt_valid=True
        self.valid_values = True
        self.z_min, self.z_max = np.min(z), np.max(z)
                
        if not self.last_interpolation_attempt_valid:
            print("The last interpolation was valid")

    def update_data(self, x, y, z):
        x, y, z = utils.filter_nans_on_z(x, y, z)
        if z.size < 5:
            warnings.warn(exceptions.InsufficientDataWarning(f"Unable to interpolate: z has only {z.size} points (min 5 required)", 
                                                            code=100),
                        stacklevel=2  # Point to the caller's line
                        )
            self.last_interpolation_attempt_valid = False
            self.invalid_surface_cleanup()
            return
        else:
            self.verify_limits(np.min(x), np.max(x), np.min(y), np.max(y))
            self._interpolate_surface(x, y, z)


@dataclass(config=Config3)
class Slices(   ):
    surface: Surface = None
    surface_axis_directions: str = ""
    base_domain: InitVar[BaseDomain] = None
    scatter: Optional[Scatter] = Field(init=True)
    displayed_slices: List[float] = Field(init=False)
    slice_container: Dict[float, List[np.ndarray]] = Field(init=False)
    n_x: int = Field(init=False)
    domain_vec: np.ndarray = Field(init=False)
    domain_idx_map: Dict[str, int] = Field(init=False)
        
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

    
    def update_data(self, x, y, z):
        if not self.scatter is None:
            self.scatter.update_data(x, y, z)
        self.surface.update_data(x, y, z)

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
