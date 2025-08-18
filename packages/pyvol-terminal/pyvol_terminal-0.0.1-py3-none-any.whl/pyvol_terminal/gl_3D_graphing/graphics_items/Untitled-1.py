#%%

from abc import ABC, abstractmethod
from dataclasses import dataclass, field, InitVar
from typing import List, Tuple, Optional
import numpy as np
@dataclass(slots=True)
class AbstractPlotDataSet(ABC):
    allFinite: List[Optional[bool]] = field(init=False, default_factory=list)
    _dataBounds: List[Tuple[Optional[float], Optional[float]]] = field(init=False, default_factory=list)
    
    def __post_init__(self):
        self._initialize_attributes()
        
    def _initialize_attributes(self):
        """Initialize attributes based on number of components"""
        n = self.num_components
        self.allFinite = [None] * n
        self._dataBounds = [(None, None)] * n
        
    @property
    @abstractmethod
    def num_components(self) -> int:
        """Number of data components (e.g., 3 for x/y/z)"""
        
    @abstractmethod
    def getComponents(self) -> List[np.ndarray]:
        """Get list of component arrays (flattened for bounds calculation)"""
        
    def _compute_bounds(self):
        """Update bounds and finite-status for all components"""
        components = self.getComponents()
        for i, comp in enumerate(components):
            if comp.size == 0:
                self.allFinite[i] = None
                self._dataBounds[i] = (None, None)
            else:
                flat_comp = comp.ravel()
                self.allFinite[i] = np.isfinite(flat_comp).all()
                self._dataBounds[i] = (np.min(flat_comp), np.max(flat_comp))

# Example implementations
@dataclass(slots=True)
class PlotDatasetVector(AbstractPlotDataSet):
    pos: InitVar[Optional[np.ndarray]] = None
    
    _pos: np.ndarray = field(init=False, default=None)
    
    def __post_init__(self, pos):
        super(PlotDatasetVector, self).__post_init__()
        self.pos = pos
            
            
    @property
    def num_components(self) -> int:
        return 3
        
    def getComponents(self) -> List[np.ndarray]:
        return [self._pos[:, i] for i in range(3)]
    
    @property
    def pos(self) -> np.ndarray:
        return self._pos
        
    @pos.setter
    def pos(self, value: np.ndarray):
        self._pos = value

@dataclass(slots=True)
class PlotDatasetMesh(AbstractPlotDataSet):
    x: InitVar[Optional[np.ndarray]] = None
    y: InitVar[Optional[np.ndarray]] = None
    z: InitVar[Optional[np.ndarray]] = None
    
    _x: np.ndarray = field(init=False, default=None)
    _y: np.ndarray = field(init=False, default=None)
    _z: np.ndarray = field(init=False, default=None)
    
    def __post_init__(self, x, y, z):
        super(PlotDatasetMesh, self).__post_init__()

        self.x = x
        self.y = y
        self.z = z
            
    @property
    def num_components(self) -> int:
        return 3
        
    def getComponents(self) -> List[np.ndarray]:
        return [c.ravel() for c in (self.x, self.y, self.z)]
    
    # Property setters with automatic bounds update
    @property
    def x(self) -> np.ndarray:
        return self._x
        
    @x.setter
    def x(self, value: np.ndarray):
        self._x = value
    
    @property
    def y(self) -> np.ndarray:
        return self._y
        
    @y.setter
    def y(self, value: np.ndarray):
        self._y = value
    
    @property
    def z(self) -> np.ndarray:
        return self._z
        
    @z.setter
    def z(self, value: np.ndarray):
        self._z = value

# Vector initialization
vector_data = PlotDatasetVector(pos=np.random.rand(100, 3))

# Mesh initialization
x, y, z = np.mgrid[:10, :10, :10]

mesh_data = PlotDatasetMesh(x, y, z)

# Update data
vector_data.pos = np.random.rand(50, 3)
mesh_data.x = np.linspace(0, 5, 10)

# Access computed properties
print(vector_data._dataBounds)  # Bounds for x,y,z
print(mesh_data.allFinite)     # Finite-status for each component

#%%%


from PySide6 import QtCore, QtGui, QtWidgets


@dataclass(slots=True)
class AbstractPlotDataSet(ABC):
    allFinite: List[Optional[bool]] = field(init=False, default_factory=list)
    _dataBounds: List[List[float]] | None = field(init=False, default=None)
    
    def __post_init__(self):
        self._initialize_attributes()
        
    def _initialize_attributes(self):
        self.allFinite = [None] * self.num_components
        
        
    def dataBounds(self) -> QtCore.QRectF | None:
        if self._dataBounds is None: 
            self._updateDataBounds()
        return self._dataBounds

        
    @property
    @abstractmethod
    def num_components(self) -> int:
        """Number of data components (e.g., 3 for x/y/z)"""
        
    @abstractmethod
    def getComponents(self) -> List[np.ndarray]:
        """Get list of component arrays (flattened for bounds calculation)"""
    
    def _updateDataBounds(self):
        components = self.getComponents()
        if any([values is None for values in components]):
            return None
         
        dataBounds=[]
        for idx, arr in enumerate(components):
            minRange, maxRange, finiteFlag = self._getArrayBounds(arr, self.allFinite[idx])
            dataBounds.append((minRange, maxRange))
            self.allFinite[idx]=finiteFlag
            
        self._dataBounds=dataBounds
                
    def _getArrayBounds(self,
                        arr: np.ndarray,
                        all_finite: bool | None
                        ) -> tuple[float, float, bool]:
        # here all_finite could be [None, False, True]
        if not all_finite:  # This may contain NaN or inf values.
            # We are looking for the bounds of the plottable data set. Infinite and Nan
            # are ignored.
            selection = np.isfinite(arr)
            # True if all values are finite, False if there are any non-finites
            all_finite = bool(selection.all())
            if not all_finite:
                arr = arr[selection]
        
        # here all_finite could be [False, True]
        try:
            amin = np.min( arr )  # find minimum of all finite values
            amax = np.max( arr )  # find maximum of all finite values
        except ValueError:  # is raised when there are no finite values
            amin = np.nan
            amax = np.nan
        print(f"amin, amax, all_finite: {(amin, amax, all_finite)}")
        return amin, amax, all_finite

@dataclass(slots=True)
class PlotDatasetVector(AbstractPlotDataSet):
    pos: InitVar[Optional[np.ndarray]] = None
    
    _pos: np.ndarray = field(init=False, default=None)
    
    def __post_init__(self, pos):
        super(PlotDatasetVector, self).__post_init__()
        self.pos = pos
            
            
    @property
    def num_components(self) -> int:
        return 3
        
    def getComponents(self) -> List[np.ndarray]:
        return [self._pos[:, i] for i in range(self.num_components)]
    
    @property
    def pos(self) -> np.ndarray:
        return self._pos
        
    @pos.setter
    def pos(self, value: np.ndarray):
        self._pos = value

    def data(self) -> np.array:
        return self.pos()


@dataclass(slots=True)
class PlotDatasetMesh(AbstractPlotDataSet):
    x: InitVar[Optional[np.ndarray]] = None
    y: InitVar[Optional[np.ndarray]] = None
    z: InitVar[Optional[np.ndarray]] = None
    
    _x: np.ndarray = field(init=False, default=None)
    _y: np.ndarray = field(init=False, default=None)
    _z: np.ndarray = field(init=False, default=None)
    
    def __post_init__(self, x, y, z):
        super(PlotDatasetMesh, self).__post_init__()

        self.x = x
        self.y = y
        self.z = z
            
    @property
    def num_components(self) -> int:
        return 3
        
    def getComponents(self) -> List[np.ndarray]:
        return [c.ravel() for c in (self.x, self.y, self.z)]
    
    # Property setters with automatic bounds update
    @property
    def x(self) -> np.ndarray:
        return self._x
        
    @x.setter
    def x(self, value: np.ndarray):
        self._x = value
    
    @property
    def y(self) -> np.ndarray:
        return self._y
        
    @y.setter
    def y(self, value: np.ndarray):
        self._y = value
    
    @property
    def z(self) -> np.ndarray:
        return self._z
        
    @z.setter
    def z(self, value: np.ndarray):
        self._z = value

    def data(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        return (self.x, self.y, self.z)

# Vector initialization
vector_data = PlotDatasetVector(pos=np.arange(90).reshape(30,3))

# Mesh initialization
x, y, z = np.mgrid[:10, :10, :10]

x = np.arange(30)
y = np.arange(3)
z = np.arange(90).reshape(30,3)

mesh_data = PlotDatasetMesh(x, y, z)

# Update data
#vector_data.pos = np.random.rand(50, 3)





# Access computed properties
print(vector_data.dataBounds())  # Bounds for x,y,z
print(mesh_data.dataBounds())     # Finite-status for each component



#%%



@dataclass(slots=True)
class AbstractPlotDataset(ABC):
    allFinite: List[Optional[bool]] = field(default_factory=list)
    _dataBounds: List[List[float]] | None = field(init=False, default=None)
    
    def __post_init__(self):
        self._initialize_attributes()
        
    def _initialize_attributes(self):
        self.allFinite = [None] * self.num_components
        
        
    def dataBounds(self) -> QtCore.QRectF | None:
        if self._dataBounds is None: 
            self._updateDataBounds()
        return self._dataBounds
    
    @abstractmethod
    def data(self):...

        
    @property
    @abstractmethod
    def num_components(self) -> int:
        """Number of data components (e.g., 3 for x/y/z)"""
        
    @abstractmethod
    def getComponents(self) -> List[np.ndarray]:
        """Get list of component arrays (flattened for bounds calculation)"""
    
    def _updateDataBounds(self):
        components = self.getComponents()
        if any([values is None for values in components]):
            return None
         
        dataBounds=[]
        for idx, arr in enumerate(components):
            minRange, maxRange, finiteFlag = self._getArrayBounds(arr, self.allFinite[idx])
            dataBounds.append((minRange, maxRange))
            self.allFinite[idx]=finiteFlag
            
        self._dataBounds=dataBounds
                
    def _getArrayBounds(self,
                        arr: np.ndarray,
                        all_finite: bool | None
                        ) -> tuple[float, float, bool]:
        # here all_finite could be [None, False, True]
        if not all_finite:  # This may contain NaN or inf values.
            # We are looking for the bounds of the plottable data set. Infinite and Nan
            # are ignored.
            selection = np.isfinite(arr)
            # True if all values are finite, False if there are any non-finites
            all_finite = bool(selection.all())
            if not all_finite:
                arr = arr[selection]
        
        # here all_finite could be [False, True]
        try:
            amin = np.min( arr )  # find minimum of all finite values
            amax = np.max( arr )  # find maximum of all finite values
        except ValueError:  # is raised when there are no finite values
            amin = np.nan
            amax = np.nan
        return amin, amax, all_finite

@dataclass(slots=True)
class PlotDatasetVector(AbstractPlotDataset):
    pos: InitVar[Optional[np.ndarray]] = None
    
    _pos: np.ndarray = field(init=False, default=None)
    
    def __post_init__(self, pos):
        super(PlotDatasetVector, self).__post_init__()
        self._pos = pos
            
            
    @property
    def num_components(self) -> int:
        return 3
        
    def getComponents(self) -> List[np.ndarray]:
        return [self._pos[:, i] for i in range(self.num_components)]
    
    @property
    def pos(self) -> np.ndarray:
        return self._pos
        
    @pos.setter
    def pos(self, value: np.ndarray):
        self._pos = value

    def data(self) -> np.array:
        return self.pos
# Vector initialization
vector_data = PlotDatasetVector(pos=np.arange(90).reshape(30,3))

# Mesh initialization
x, y, z = np.mgrid[:10, :10, :10]

x = np.arange(30)
y = np.arange(3)
z = np.arange(90).reshape(30,3)

mesh_data = PlotDatasetMesh(x, y, z)

# Update data
#vector_data.pos = np.random.rand(50, 3)





# Access computed properties
print(vector_data.dataBounds())  # Bounds for x,y,z
print(mesh_data.dataBounds())     # Finite-status for each component



@dataclass(slots=True)
class AbstractPlotDataSet2(ABC):
    x: InitVar[np.ndarray] 
    y: InitVar[np.ndarray] 
    z: InitVar[np.ndarray] 
    
    _x: np.ndarray = field(init=False, default=None)
    _y: np.ndarray = field(init=False, default=None)
    _z: np.ndarray = field(init=False, default=None)
    
    allFinite: List[bool] = field(default_factory=lambda: [None]*3)
    #_dataBounds: List[Tuple[float, float]] = field(init=False, default_factory=lambda: [[None, None] for _ in range(3)])
    _dataBounds: List[Tuple[float, float]] = field(init=False, default=None)


    def __post_init__(self, x=None, y=None, z=None):
        self.x=x
        self.y=y
        self.z=z
        
        if isinstance(self.x, np.ndarray) and self.x.dtype.kind in 'iu':
            self.allFinite[0]=True
        if isinstance(self.y, np.ndarray) and self.y.dtype.kind in 'iu':
            self.allFinite[1]=True
        if isinstance(self.z, np.ndarray) and self.z.dtype.kind in 'iu':
            self.allFinite[2]=True        
            
    def dataBounds(self) -> QtCore.QRectF | None:
        print(f'\ndataBounds')
        if self._dataBounds is None: 
            self._updateDataBounds()
        print(f"self._dataBounds: {self._dataBounds}")
        return self._dataBounds

    @abstractmethod
    def data(self):...

    #@abstractmethod
    #def update(self, *args, **kwargs):...

    @property
    def x(self):
        return self._x
    
    @x.setter
    def x(self, x):
        self._x=x
        
    @property
    def y(self):
        return self._y
    
    @y.setter
    def y(self, y):
        self._y=y

    @property
    def z(self):
        return self._z
    
    @z.setter
    def z(self, z):
        self._z=z

    def _updateDataBounds(self):
        if any((self.x is None, self.y is None, self.z is None)):
            return None

        dataBounds=[]
        for idx, arr in enumerate((self.x, self.y, self.z)):
            minRange, maxRange, finiteFlag = self._getArrayBounds(arr, self.allFinite[idx])
            dataBounds.append((minRange, maxRange))
            self.allFinite[idx]=finiteFlag
            
        self._dataBounds=dataBounds

    def _getArrayBounds(self,
                        arr: np.ndarray,
                        all_finite: bool | None
                        ) -> tuple[float, float, bool]:
        # here all_finite could be [None, False, True]
        if not all_finite:  # This may contain NaN or inf values.
            # We are looking for the bounds of the plottable data set. Infinite and Nan
            # are ignored.
            selection = np.isfinite(arr)
            # True if all values are finite, False if there are any non-finites
            all_finite = bool(selection.all())
            if not all_finite:
                arr = arr[selection]
        
        # here all_finite could be [False, True]
        try:
            amin = np.min( arr )  # find minimum of all finite values
            amax = np.max( arr )  # find maximum of all finite values
        except ValueError:  # is raised when there are no finite values
            amin = np.nan
            amax = np.nan
        return amin, amax, all_finite
    