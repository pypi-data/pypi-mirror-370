from __future__ import annotations 
from dataclasses import dataclass, field, InitVar
import numpy as np
from pyvol_terminal import utils
from typing import Any, List
import copy
from pyvol_terminal.plotting_engines import MetricEngine
from typing import Dict, ClassVar, Optional
from pyvol_terminal import exceptions
import warnings

def custom_showwarning(message, category, filename, lineno, file=None, line=None):
    print(f"UserWarning: {message} ({filename}, line {lineno})")
warnings.showwarning = custom_showwarning


@dataclass(slots=True)
class BaseData:
    n_instruments: int
    name_index_map: Dict[str, int]
    price: np.ndarray
    
        
@dataclass(slots=True)
class RawFutures(BaseData):
    OTM: np.ndarray
    

@dataclass(slots=True)
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
        

@dataclass(slots=True, frozen=True)
class BaseDomain:
    strike: np.ndarray
    expiry: np.ndarray
    x_metric: str
    y_metric: str
    
        
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

    def update(self, x=None, y=None, xy=None, z=None, x_metric=None, y_metric=None, z_metric=None):
        if not xy is None:
            self.xy = xy
            self.x = xy[:,0]
            self.y = xy[:,1]
        else:
            self.x = x
            self.y = y
            self.xy = np.column_stack((x,y))
        if not z is None:
            self.z = z
        if x_metric:
            self.x_metric = x_metric
        if y_metric:
            self.y_metric = y_metric
        self._calc_metrics()
    
    
@dataclass(slots=True)
class Scatter:  
    x: np.ndarray 
    y: np.ndarray 
    z: np.ndarray
    
    x_min: float = np.nan
    x_max: float = np.nan
    y_min: float = np.nan
    y_max: float = np.nan
    z_min: float = np.nan
    z_max: float = np.nan
    valid_values: bool = False
    
    x_min: float = field(init=False, default = np.nan)
    x_max: float = field(init=False, default = np.nan)
    y_min: float = field(init=False, default = np.nan)
    y_max: float = field(init=False, default = np.nan)
    z_min: float = field(init=False, default = np.nan)
    z_max: float = field(init=False, default = np.nan)
    
    valid_values: bool = field(init=False, default=False)
    
    def __post_init__(self):
        self.update_data(self.x, self.y, self.z)
        
    def get_limits(self,):
        return self.x_min, self.x_max, self.y_min, self.y_max, self.z_min, self.z_max
    
    def update_data(self, x, y, z):
        self.valid_values=False
        self.x, self.y, self.z = utils.filter_nans_on_z(x, y, z)
        if self.z.size > 0:
            self.valid_values=True
            self._calculate_metrics()

    def _calculate_metrics(self):
        self.x_min = np.amin(self.x)
        self.x_max = np.amax(self.x)
        self.y_min = np.amin(self.y)
        self.y_max = np.amax(self.y)
        self.z_min = np.amin(self.z)
        self.z_max = np.amax(self.z)

    def _calc_domain_metrics(self):
        self.x_min = np.amin(self.x)
        self.x_max = np.amax(self.x)
        self.y_min = np.amin(self.y)
        self.y_max = np.amax(self.y)

    def _calc_z_metrics(self):
        self.z_min = np.amin(self.z)
        self.z_max = np.amax(self.z)
                
        
@dataclass(slots=True)
class Surface:
    base_domain: BaseDomain
    scatter: Scatter
    interpolator: Any
    n_x: int
    n_y: int

    x: np.ndarray = field(init=False, default_factory=lambda: np.array)
    y: np.ndarray = field(init=False, default_factory=lambda: np.array)
    z: np.ndarray = field(init=False, default_factory=lambda: np.array)
            
    x_min: float = field(init=False, default=np.nan)
    x_max: float = field(init=False, default=np.nan)
    y_min: float = field(init=False, default=np.nan)
    y_max: float = field(init=False, default=np.nan)
    
    z_min: float = field(init=False, default=np.nan)
    z_max: float = field(init=False, default=np.nan)
    
    valid_values: bool = field(init=False, default=False)
    last_interpolation_attempt_valid: bool = field(init=False, default=False)
    current_view_selection: str = field(init=False, default="Surface")
    
    def __post_init__(self):   
        self.x=self.scatter.x
        self.y=self.scatter.y
        self._create_interpolation_limits(self.scatter)
        if self.scatter.valid_values:
            self.interpolate_surface()
        else:
            self.z = np.nan * np.zeros((self.n_x, self.n_y))
        
    def get_limits(self,):
        return self.x_min, self.x_max, self.y_min, self.y_max, self.z_min, self.z_max
    
    def update_data_from_scatter_object(self, scatter_object):
        if (self.x_min != scatter_object.x_min
            or self.x_max != scatter_object.x_max
            or self.y_min != scatter_object.y_min
            or self.y_max != scatter_object.y_max):

            self.x_min = scatter_object.x_min 
            self.x_max = scatter_object.x_max
            self.y_min = scatter_object.y_min
            self.y_max = scatter_object.y_max

            self.x = np.linspace(self.x_min, self.x_max, self.n_x)
            self.y = np.linspace(self.y_min, self.y_max, self.n_y)

    def _create_interpolation_limits(self, scatter_object):
        self.x_min = self.base_domain.strike.min()
        self.x_max = self.base_domain.strike.max()
        self.y_min = self.base_domain.expiry.min()
        self.y_max = self.base_domain.expiry.max()

        """
        self.x_min = scatter_object.x_min
        self.x_max = scatter_object.x_max 
        self.y_min = scatter_object.y_min 
        self.y_max = scatter_object.y_max
        """
        self.x = np.linspace(self.x_min, self.x_max, self.n_x)
        self.y = np.linspace(self.y_min, self.y_max, self.n_y)

    def interpolate_surface(self):
        self.valid_values=False
        x, y, z = utils.filter_nans_on_z(self.scatter.x, self.scatter.y, self.scatter.z)
        if z.size < 5:
            warnings.warn(exceptions.InsufficientDataWarning(
                        f"Unable to interpolate: z has only {z.size} points (min 5 required)", 
                code=100
            ),
            stacklevel=2  # Point to the caller's line
        )
            self.last_interpolation_attempt_valid = False
            return
        try:
            self.interpolator.fit(x, y, z)                
        except Exception as e:
            print(f"The interpolator could not fit: {e}")
            self.last_interpolation_attempt_valid=False
            return
        try:
            self.z = self.interpolator.evaluate(self.x, self.y)
        except Exception as e:
            print(f"The interpolator could not evaluate: {e}")
            self.last_interpolation_attempt_valid=False
            return
        
        if not self.last_interpolation_attempt_valid:
            print("The last interpolation was valid")
        self.last_interpolation_attempt_valid=True
        self.z_min = np.nanmin(self.z)
        self.z_max = np.nanmax(self.z)
        self.valid_values=True

@dataclass
class Slice:
    x: np.ndarray
    y: np.ndarray
    xi: np.ndarray
    yi: np.ndarray
    valid_data: bool = field(init=False)
    interpolator: Any

    def __post_init__(self):
        self.x, self.y = utils.filter_nans_2D(self.x, self.y)
        if self.y.size > 1:
            self.interpolate(self.x, self.y)
            self.valid_data=True
        else:
            self.valid_data=False
        
    def interpolate(self, x, y):
        self.x, self.y = utils.filter_nans_2D(self.x, self.y)
        if self.y.size > 2:
            self.interpolator.fit(x, y)
            self.yi = self.interpolator.evaluate(self.xi)
            self.valid_data=True
        else:
            self.valid_data = False


@dataclass
class Smile:
    base_domain: BaseDomain
    raw: RawOptions
    interpolator: Any
    n_x: int
    slice: Dict[Slice]
    
    x: np.ndarray = field(init=False)
    z_dict: Dict[np.ndarray] = field(init=False)
    x_min: float = field(init=False)
    x_max: float = field(init=False)
    expiry_vect: np.ndarray = field(init=False)
    
    def __post_init__(self):
        self.expiry_vect = np.unique(self.base_domain.expiry)
        x = self.base_domain.strike
        y = self.base_domain.expiry
        
        self.x_min = x.min()
        self.x_max = x.max()
        self.x = np.linspace(self.x_min, self.x_max, self.n_x)
        self.z_dict = {exp : [] for exp in self.expiry_vect}
        self.slice = {}
        for expiry in self.expiry_vect:
             slice = Slice(x, y, self.x, np.full(self.x.shape, np.nan))
             self.slice[expiry] = slice
             
    def update_data(self, x, y, z):
        if z.size > 2:
            pass
        
     
    def interpolate(self):
        x = self.base_domain.strike
        y = self.base_domain.expiry
        z = self.raw.ivol
        x = x[self.raw.OTM]
        y = y[self.raw.OTM]
        z = z[self.raw.OTM]
        x, y, z = utils.filter_nans_on_z(x, y, z)
        for expiry in self.expiry_vect:
            mask = y == expiry
            x_filtered = x[mask]
            z_filtered = z[mask]
            slice = self.slice[expiry]
            slice.update_data(x_filtered, z_filtered)   
            if z_filtered.size > 3:
                self.interpolator.fit(x_filtered, z_filtered)
                z_new = self.interpolator.evaluate(self.x)
                self.z_dict[expiry] = z_new
                self.valid_data_dict[expiry] = True
            else:
                self.valid_data_dict[expiry] = False


@dataclass
class DataContainer:
    px_type: str
    domain: Optional["Domain"] = None
    raw: Optional["RawOptions"] = None
    scatter: Optional["Scatter"] = None
    surface: Optional["Surface"] = None
    smile: Optional["Smile"] = None
        
    def __post_init__(self):
        if not self.surface is None and not self.scatter is None:
            self._calculate_data_limits()
    
    def update_dataclasses(self, x, y, z, idx_map):
        if not self.domain is None:
            self.domain.update_data(z, idx_map)
        if not self.scatter is None:
            self.scatter.update_data(x, y, z)
        if not self.surface is None:
            self.surface.update_data_from_scatter_object(self.scatter)

    def update_dataclasss_transform(self, transform_engine):
        x, y, z, idx_map = transform_engine.transform_data(self.raw)
        self.update_dataclasses(x, y, z, idx_map)
        
    def data_container_cleanup(self):
        if not self.surface is None:
            self.surface.interpolate_surface()
        if not self.smile is None:
            self.smile.interpolate()
        self._calculate_data_limits()
    
    def _calculate_data_limits(self):
        self.x_min = np.minimum(self.scatter.x_min, self.surface.x_min)
        self.x_max = np.maximum(self.scatter.x_max, self.surface.x_max) 
        self.y_min = np.minimum(self.scatter.y_min, self.surface.y_min)
        self.y_max = np.maximum(self.scatter.y_max, self.surface.y_max) 
        
        if self.scatter.valid_values and self.surface.valid_values:
            self.z_min = np.minimum(self.scatter.z_min, self.surface.z_min)
            self.z_max = np.maximum(self.scatter.z_max, self.surface.z_max) 
        elif self.scatter.valid_values:
            self.z_min = self.scatter.z_min
            self.z_max = self.scatter.z_max
        elif self.surface.valid_values:
            self.z_min=self.surface.z_min
            self.z_max=self.surface.z_max
        

@dataclass
class DataFeatureManager:
    price_types: list

    limit_dict: dict = field(init=False)
    valid_values_dict: dict = field(init=False)
    valid_values_any: bool = False
    
    all_axis: ClassVar[list] = ["x","y","z"]
    plot_types: ClassVar[list] = ["scatter", "surface"]
    _reset_dict: ClassVar[dict] = {"min" : np.nan, "max" : np.nan}
    
    def __post_init__(self):
        self.limit_dict = {}
        self.valid_values_dict = {}
        for px_type in self.price_types:
            plot_dict_lim = {}
            plot_dict_bool = {}
            for plot_type in self.plot_types:
                axis_dict_lim = {}
                for axis in self.all_axis:
                    axis_dict_lim[axis] = copy.deepcopy(self._reset_dict)
                plot_dict_lim[plot_type] = axis_dict_lim
                plot_dict_bool[plot_type] = False
                
            self.limit_dict[px_type] = plot_dict_lim
            self.valid_values_dict[px_type] = plot_dict_bool

    def remove_data(self, px_type):
        for axis in self.all_axis:
            self.limit_dict[px_type]["surface"][axis] = copy.deepcopy(self._reset_dict)
            self.limit_dict[px_type]["scatter"][axis] = copy.deepcopy(self._reset_dict)
            
        self.valid_values_dict[px_type]["surface"]=False
        self.valid_values_dict[px_type]["scatter"]=False

    def find_any_valid_values(self, data_container_manager_object: DataContainerManager.object):
        bool_arr = []
        z_vals = []
        for px_type, data_container in data_container_manager_object.items():
            if data_container.surface.valid_values:
                for axis in self.all_axis:
                    axis_min = getattr(data_container.surface, f"{axis}_min")
                    axis_max = getattr(data_container.surface, f"{axis}_max")
                    self.limit_dict[px_type]["surface"][axis]["min"] = axis_min
                    self.limit_dict[px_type]["surface"][axis]["max"] = axis_max
                    bool_arr.append(True)
                    self.valid_values_dict[px_type]["surface"] = True
                z_vals.append(self.limit_dict[px_type]["surface"]["z"]["min"])
                z_vals.append(self.limit_dict[px_type]["surface"]["z"]["max"])
            else:
                for axis in self.all_axis:
                    self.limit_dict[px_type]["surface"][axis]["min"] = np.nan
                    self.limit_dict[px_type]["surface"][axis]["max"] = np.nan
                    self.valid_values_dict[px_type]["surface"] = False

            if data_container.scatter.valid_values:
                for axis in self.all_axis:
                    axis_min = getattr(data_container.scatter, f"{axis}_min")
                    axis_max = getattr(data_container.scatter, f"{axis}_max")
                    self.limit_dict[px_type]["scatter"][axis]["min"] = axis_min
                    self.limit_dict[px_type]["scatter"][axis]["max"] = axis_max
                    bool_arr.append(True)
                    self.valid_values_dict[px_type]["scatter"] = True
                z_vals.append(self.limit_dict[px_type]["scatter"]["z"]["min"])
                z_vals.append(self.limit_dict[px_type]["scatter"]["z"]["max"])
            else:
                self.limit_dict[px_type]["scatter"][axis]["min"] = np.nan
                self.limit_dict[px_type]["scatter"][axis]["max"] = np.nan
                self.valid_values_dict[px_type]["scatter"] = False
        
        self.valid_values_any = any(bool_arr)
        if self.valid_values_any:
            return True, z_vals
        else:
            return False, z_vals
          
                                                      
@dataclass
class DataContainerManager:
    axis_transform_engine: "MetricEngine" 
    price_types: InitVar[list]
    data_container: InitVar[DataContainer] = None
    
    containers: dict = field(init=False, default_factory=dict)
    displayed_price_types: List[str] = field(init=False, default_factory=list)  
    
    x_min: float = field(init=False, default=np.nan)
    x_max: float = field(init=False, default=np.nan)
    y_min: float = field(init=False, default=np.nan)
    y_max: float = field(init=False, default=np.nan)
    z_min: float = field(init=False, default=np.nan)
    z_max: float = field(init=False, default=np.nan)
    
    features: DataFeatureManager = None
    
    def __post_init__(self, price_types, data_container: DataContainer):
        self.features = DataFeatureManager(price_types)
        if not data_container is None:
            self.add_displayed_price_type(data_container)

    def add_displayed_price_type(self, px_type):
        self.displayed_price_types.append(px_type)
        self.calculate_data_limits()
    
    def add_data_container(self, data_container):
        self.containers[data_container.px_type] = data_container
        self.displayed_price_types = [data_container.px_type]
        self.calculate_data_limits()
        
    def remove_displayed_price_type(self, px_type):
        self.displayed_price_types.remove(px_type)
        self.features.remove_data(px_type)
        self.calculate_data_limits()

    def update_data_containers_instrument_object(self, instrument_object):
        for px_type, data_container in self.containers.items():
            data_container.raw.update_all_metrics_name(instrument_object.ticker,
                                                       *instrument_object.get_all_metrics_price_type(px_type))
    
    def update_data_containers(self):
        for px_type, data_container in self.containers.items():
            data_container.update_dataclasss_transform(self.axis_transform_engine)
            data_container.data_container_cleanup()
    
    def update_cleanup(self):
        for px_type, data_container in self.containers.items():
            data_container.update_dataclasss_transform(self.axis_transform_engine)
    
    def update_price_cleanup(self):
        self.calculate_data_limits()

    def process_update(self):
        if len(self.containers) > 0:
            self.calculate_data_limits()
            
    def calculate_data_limits(self):
        if len(self.displayed_price_types) > 0:
            self.x_min = np.min([data_container.x_min for data_container in self.containers.values() if data_container.px_type in self.displayed_price_types])
            self.x_max = np.max([data_container.x_max for data_container in self.containers.values() if data_container.px_type in self.displayed_price_types])
            self.y_min = np.min([data_container.y_min for data_container in self.containers.values() if data_container.px_type in self.displayed_price_types])
            self.y_max = np.max([data_container.y_max for data_container in self.containers.values() if data_container.px_type in self.displayed_price_types])
            valid_values_any, z_vals = self.features.find_any_valid_values(self.containers)
            if valid_values_any:
                self.z_min, self.z_max = np.amin(z_vals), np.amax(z_vals)
            else:
                self.z_min, self.z_max = np.nan, np.nan
        else:
            self.x_min, self.x_max, self.y_min, self.y_max, self.z_min, self.z_max = [np.nan] * 6
            self.valid_values_any=False
            
    def get_limits(self):
        return self.x_min, self.x_max, self.y_min, self.y_max, self.z_min, self.z_max
    
    def generate_mask_from_domain_lims(self, x, y):
        return (self.x_min < x) & (x < self.x_max) & (self.y_min < y) & (y < self.y_max)
