from __future__ import annotations 
from typing import List, Optional, Tuple, Union, Dict, TYPE_CHECKING, Callable, ClassVar
if TYPE_CHECKING:
    from .GL3DViewBox import GL3DViewBox 

import weakref
from pyqtgraph.Qt import isQObjectAlive
from pyvol_terminal.gl_3D_graphing.meta import QABCMeta, abc
from pyqtgraph.opengl import GLGraphicsItem
from .AbstractGLGraphicsItem import AbstractGLGraphicsItem
from .AbstractGLGraphicsItem import ABCGraphicsItemMeta
from PySide6 import QtCore, QtWidgets
import numpy as np
from dataclasses import dataclass, field, InitVar
from abc import ABC, abstractmethod
import warnings
from pyqtgraph.Qt import QT_LIB
from functools import wraps 
import traceback
from pprint import pprint

@dataclass(slots=True)
class AbstractPlotDataset(ABC):
    initData: InitVar[np.ndarray|Tuple[np.ndarray, ...]] = None
    allFinite: List[Optional[bool]] = field(default_factory=list)
    _dataBounds: List[List[float]] | None = field(init=False, default=None)
    
    def __post_init__(self, initData):
        self._initialize_attributes()
        
        
    def _initialize_attributes(self):
        if len(self.allFinite) == 0:
            self.allFinite = [None] * self.num_components
            self._updateDataBounds()
        
    def dataBounds(self) -> QtCore.QRectF | None:
        if self._dataBounds is None: 
            self._updateDataBounds()
        return self._dataBounds
    
    @abstractmethod
    def data(self) -> np.ndarray | Tuple[np.ndarray,...]:
        ...
        
    @abstractmethod
    def dataKwargs(self) -> Dict[str, np.ndarray]:
        ...


        
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
class PlotDatasetFlatMesh(AbstractPlotDataset):    
    _pos: np.ndarray = field(init=False, default=None)
    
    def __post_init__(self, initData):
        self._pos = initData
        super(PlotDatasetFlatMesh, self).__post_init__(initData)
        
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

    def data(self) -> np.ndarray:
        return self.pos
    
    def dataKwargs(self):
        return {"pos" : self.pos}


            
@dataclass(slots=True)
class PlotDatasetMesh(AbstractPlotDataset):
    initData: InitVar[Tuple[np.ndarray, ...]] = None
    
    _x: np.ndarray = field(init=False, default=None)
    _y: np.ndarray = field(init=False, default=None)
    _z: np.ndarray = field(init=False, default=None)
    
    def __post_init__(self, initData):
        self.x, self.y, self.z = initData
        super(PlotDatasetMesh, self).__post_init__(initData)
            
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

    def dataKwargs(self):
        return {"x" : self.x, "y" : self.y, "z" : self.z}



@dataclass(slots=True)
class CacheData:
    _null3: ClassVar[List[None]] = [None, None, None]
    _false3: ClassVar[List[None]] = [False, False, False]
    _null32: ClassVar[List[List[None]]] = [[None, None],[None, None], [None, None]]
    
    _mask: List[None]|List[np.ndarray] = field(init=False, default_factory=lambda : CacheData._null3.copy())
    _bounds: List[List[None]]|List[List[float]] = field(init=False, default_factory=lambda : [row.copy() for row in CacheData._null32])
    _mask: List[None]|List[np.ndarray] = field(init=False, default_factory=lambda : CacheData._null3.copy())
    _orthoRange: List[None]|List[float] = field(init=False, default_factory=lambda : CacheData._null3.copy())
    _frac: List[None]|List[float] = field(init=False, default_factory=lambda : CacheData._null3.copy())
    _cacheFlag: List[bool] = field(init=False, default_factory=lambda : CacheData._false3.copy())

    def __repr__(self):
        out = {}
        for name in self.__slots__:
            if name.startswith('_'):
                public_name = name[1:]
                method = getattr(self, public_name, None)
                if callable(method):
                    try:
                        out[public_name] = method()
                    except Exception:
                        out[public_name] = "<error>"
        return f"{self.__class__.__name__}({out})"   
     
    def cacheFlag(self, ax=None):
        if ax is None:
            return self._cacheFlag
        else:
            return self._cacheFlag[ax]
        
    
    def setCacheFlag(self, flag, ax=None):
        if ax is None:
            self._cacheFlag=flag
        else:
            self._cacheFlag[flag] = ax

    def setBounds(self, bounds, ax=None):
        if ax is None:
            self._bounds = bounds
            self.setCacheFlag([not None in lim for lim in bounds])
        else:
            self._bounds[ax] = bounds
            self.setCacheFlag(bounds, ax)

    
    def bounds(self, ax=None):
        if ax is None:
            return self._bounds
        else:
            return self._bounds[ax]

    
    def setMask(self, mask, ax=None):
        if ax is None:
            self._mask=mask     
        else:
            self._mask[ax] = mask
    
        
    def mask(self, ax=None):
        if ax is None:
            self._mask
        else:
            return self._mask[ax]


    def setOrthoRange(self, orthoRange, ax=None):
        if ax is None:
            self._orthoRange=orthoRange
        else:
            self._orthoRange[ax] = orthoRange

    def orthoRange(self, ax=None):
        if ax is None:
            return self._orthoRange
        else:
            return self._orthoRange[ax] 


    def setFrac(self, frac, ax=None):
        if ax is None:
            self._frac=frac
        else:
            self._frac[ax] = frac
        
    def frac(self, ax=None):
        if ax is None:
            return self._frac
        else:
            return self._frac[ax] 

    def reset(self):
        self.setBounds([row.copy() for row in self._null32])
        self.setCacheFlag(self._false3.copy())
        self.setMask(self._null3.copy())
        self.setOrthoRange(self._null3.copy())
        self.setFrac(self._null3.copy())



class MeshPlotitemProperties:
    def __init__(self, *args, **kwargs):
        self._x: np.ndarray
        self._y: np.ndarray 
        self._z: np.ndarray
        super().__init__(*args, **kwargs)
    
    @property
    def x(self):
        return self._x
      
    @x.setter
    def _x(self, value):
        self._x = value
        
    @property
    def y(self):
        return self._y
      
    @y.setter
    def _y(self, value):
        self._y = value

    @property
    def z(self):
        return self._z
      
    @z.setter
    def _z(self, value):
        self._z = value

class VectorPlotitemProperties:
    def __init__(self, *args, **kwargs):
        self._pos: np.ndarray
        super().__init__(*args, **kwargs)
    
    @property
    def pos(self):
        
        return self._pos
      
    @pos.setter
    def _pos(self, value):
        if (self.pos != value).any():
            
            self._pos = value


class BaseAbstractPlotDataItem(AbstractGLGraphicsItem, metaclass=ABCGraphicsItemMeta):
    sigPlotChanged = QtCore.Signal(object) 
    def __init__(self, topology_type="", view_box=None, parentItem=None, **kwargs):
        self._dataset: AbstractPlotDataset=None
        self._datasetDisplay: AbstractPlotDataset=None
        self._cacheData = CacheData()
        self.plotdataset_cls=None
        self._viewBox: GL3DViewBox=view_box
        if topology_type=="Mesh":
            self.plotdataset_cls=PlotDatasetMesh
        elif topology_type=="FlatMesh":
            self.plotdataset_cls=PlotDatasetFlatMesh
        else:
            traceback.print_stack()
            raise
        self.extra_opts={"clipToView" : False,
                         }

        self.setProperty('xViewRangeWasChanged', False)
        self.setProperty('yViewRangeWasChanged', False)
        self.setProperty('zViewRangeWasChanged', False)
        self.setProperty('styleWasChanged', True)  # force initial update
        
        self.setParentItem(parentItem)

    def viewTransform(self):
        view = self.getViewBox()
        if view is None:
            return None
        if hasattr(view, 'implements') and view.implements('ViewBox'):
            return self.itemTransform(view.innerSceneItem())[0]
        else:
            return self.sceneTransform()

    def setViewBox(self, vb):
        self._viewBox=vb

    def dataRect(self): 
        return None if self._dataset is None else self._dataset.dataBounds()

    def setClipToView(self, state: bool):
        pass
    
    def viewTransformChanged(self):
        self.invalidateBounds()
        #self.prepareGeometryChange()

    def invalidateBounds(self):
        self._cacheData.reset()
        
    @QtCore.Slot(object, object)
    @QtCore.Slot(object, object, object)
    def viewRangeChanged(self, vb=None, ranges=None, changed=None):

        # view range has changed; re-plot if needed 
        update_needed = False
        if changed is None or changed[0]: 
            self.setProperty('xViewRangeWasChanged', True)
            self._datasetDisplay = None
            update_needed = True
        if changed is None or changed[1]:
            self.setProperty('yViewRangeWasChanged', True)
            self._datasetDisplay = None
            update_needed = True
        if changed is None or changed[2]:
            self.setProperty('zViewRangeWasChanged', True)
            self._datasetDisplay = None
            update_needed = True

        if update_needed:
            self.updateItems(styleUpdate=False)
            
    def updateItems(self, styleUpdate: bool = True):
        dataset = self._getDisplayDataset()
        
        if dataset is None:
            print(f"\n\nDataSet is None!!!\n\n")
            raise
            self.hide()
            return
        else:
            self.updateData(**dataset.dataKwargs())
    
    @classmethod
    @abstractmethod
    def clipDataFromVRange(cls, dataset, viewrange):...
    
    def updateData(self, **kwargs):
        self.invalidateBounds()
        #self.prepareGeometryChange()
        self.informViewBoundsChanged()
        self.sigPlotChanged.emit(self)
    
    def getData(self):
        dataset = self._getDisplayDataset()
        return (None, None, None) if dataset is None else dataset.data()

            
    def getOriginalDataset(self) -> tuple[None, None] | tuple[np.ndarray, np.ndarray]:
        return self._dataset.data()
    
    def _getDisplayDataset(self) -> AbstractPlotDataset | None:
        if self._dataset is None:
            return None
        # Return cached processed dataset if available and still valid:
        if all((not self._datasetDisplay is None,
                not self.property('xViewRangeWasChanged'),
                not self.property('yViewRangeWasChanged'),
                not self.property('zViewRangeWasChanged')
                )):
            return self._datasetDisplay

        allFinite = self._dataset.allFinite
        data = self._dataset.data()
        
        view = self.getViewBox()
        
        if view is None:
            view_range = None
        else:
            view_range = view.viewRange()  # this is always up-to-date
        if view_range is None:
            view_range = self.viewRect()
 
        if view is None or view.autoRangeEnabled()[0]:
            pass  # no ViewBox to clip to, or view will autoscale to data range.
                
        if not all(allFinite):
            data = self._dataset.data()
        if not view_range is None and all(allFinite):
            data = self.clipDataFromVRange(data, view_range)        

        self._datasetDisplay = self.plotdataset_cls(data, allFinite)
        return self._datasetDisplay


    def dataBoundsVectorized(self,
                             frac=(1., 1. ,1),
                             orthoRange=(None, None, None)
                             ) -> Tuple[float, float, float]:

        if not self.visible() or self._dataset is None:
            return [[None, None], [None, None], [None, None]]
        else:
            data = self._dataset.data()
            mask = np.ones(len(data), dtype=bool)

            cache_bounds = {}
            mask_container={}

            for ax in range(2):
                if self._cacheData.cacheFlag(ax) is None and all((self._cacheData.frac(ax) == frac[ax],
                                                                  self._cacheData.orthoRange(ax) == orthoRange[ax])):
                    cache_bounds[ax] = self._cacheData.bounds(ax)
                    mask_container[ax] = self._cacheData.mask(ax)

                if not orthoRange[ax] is None:
                    mask = (data[:, ax] >= orthoRange[ax][0]) & (data[:, ax] <= orthoRange[ax][1])
                    self._cacheData.setMask(mask, ax)
                    mask_container[ax] = mask
                else:
                    self._cacheData.setMask(None, ax)
            
            x_filtered = data[0][mask_container[0]] if 0 in mask_container else data[0]
            y_filtered = data[1][mask_container[1]] if 1 in mask_container else data[1]
        
            if self._cacheData.cacheFlag(2) is None and all((self._cacheData.frac(2) == frac[2],
                                                             self._cacheData.orthoRange(2) == orthoRange[2]
                                                             )):
                cache_bounds[2] = self._cacheData.bounds(2)
                
                
            z_filtered = data[2]
            if 0 in mask_container:
                z_filtered = z_filtered[mask_container[0], :]
            
            if 1 in mask_container:
                z_filtered = z_filtered[:, mask_container[1]]

            if not orthoRange[2] is None:
                z_filtered = np.clip(z_filtered, orthoRange[2][0], orthoRange[2][1])

            
            limits = [[bound.min(), bound.max()] if i not in cache_bounds else cache_bounds[i] for i, bound in enumerate((x_filtered, y_filtered, z_filtered))]
            self._cacheData.setBounds(limits)
            return self._cacheData.bounds()

    @abstractmethod
    def _setDataChild(self, *args, **kwargs):...
        
        
    def setData(self, *args, **kwargs):
        self.blockUpdates(True)
        self._setDataChild(*args, **kwargs)
        self.updateItems(styleUpdate=self.property('styleWasChanged'))
        self.blockUpdates(False)
        self.update()

        
    def setData(self, *args, **kwargs):
        self.blockUpdates(True)
        self._setDataChild()
        self.blockUpdates(False)
        
        
    @abstractmethod
    def paint(self):
        self._paintHelper()
    
    
    
    

class _Temp(BaseAbstractPlotDataItem):
    pass



class _AbstractPlotDataItemMeta(ABCGraphicsItemMeta):
    def __call__(cls, *args, **kwargs):
        if cls.__abstractmethods__:
            raise TypeError(f"Can't instantiate abstract class {cls.__name__} without an implementation for abstract methods {set(cls.__abstractmethods__)}")
        self = cls.__new__(cls, *args, **kwargs)
        self._original_class = cls
        self.__class__ = _Temp
        
        topology_type = kwargs.pop("topology_type", None)
        view_box = kwargs.pop("view_box", None)
        parentItem = kwargs.pop("parentItem", None)

        BaseAbstractPlotDataItem.__init__(self, topology_type=topology_type, parentItem=parentItem, view_box=view_box, )
        
        self.__class__ = self._original_class
        del self._original_class
        
        if hasattr(self, '__init__') and self.__init__ is not None:
            self.__init__(*args, **kwargs)
            
        return self




class BaseMeshPlotDataItem(BaseAbstractPlotDataItem, metaclass=_AbstractPlotDataItemMeta):
    def __init__(self, view_box=None, parentItem=None, **kwargs):
        BaseAbstractPlotDataItem.__init__(self, topology_type="Mesh", view_box=view_box, parentItem=parentItem)
        
    
    def _paintHelper(self):
        
        x, y, z = self.getData()
        if np.array_equal(self._x, x):
           x=None 
        if np.array_equal(self._y, y):
           y=None 
        if np.array_equal(self._z, z):
           z=None 

        return super()._paintHelper()
    
    @classmethod
    @abstractmethod
    def clipDataFromVRange(cls, data, view_range):
        x_min, x_max = view_range[0]
        y_min, y_max = view_range[1]
        z_min, z_max = view_range[2]
        
        x, y, z = data

        x_mask = (x >= x_min) & (x <= x_max)
        y_mask = (y >= y_min) & (y <= y_max)
        

        x_filtered = x[x_mask]
        y_filtered = y[y_mask]
                
        z_filtered = z[x_mask, :][:, y_mask]
        z_filtered = np.clip(z_filtered, z_min, z_max)

        return x_filtered, y_filtered, z_filtered

    def _paintHelper(self):
        x, y, z = self.getData()
        if np.array_equal(self._x, x):
           x=None 
        if np.array_equal(self._y, y):
           y=None 
        if np.array_equal(self._z, z):
           z=None 

        self.blockUpdates(True)
        self._setDataChild(x=x, y=y, z=z)
        self.blockUpdates(False)
        self._childPaint()
