from __future__ import annotations 
from typing import List, Optional, Tuple, Union, Dict, TYPE_CHECKING, Callable, ClassVar
if TYPE_CHECKING:
    from .GL3DViewBox import GL3DViewBox
    from ..widgets.GL3DViewWidget import GL3DViewWidget



    
from PySide6 import QtWidgets, QtCore, QtGui
from abc import ABC, abstractmethod, ABCMeta
import abc
from pyqtgraph import Transform3D, functions as fn
from pyqtgraph.opengl.GLGraphicsItem import GLGraphicsItem
from PySide6.QtWidgets import QGraphicsItem
from enum import Enum, EnumType, Flag
import warnings
from pyqtgraph.Qt import QT_LIB
import weakref
from .GL3DGraphicsItemMixin import GL3DGraphicsItemMixin
from dataclasses import dataclass, field, InitVar
import numpy as np
import traceback
import inspect

from pprint import pprint
import traceback
import io


def stackprinter_print_stack(limit, phrase):
    buf = io.StringIO()
    
    # Print stack to buffer (returns None, but writes to buf)
    traceback.print_stack(limit=limit, file=buf)
    
    # Get the value from buffer and split lines
    stack_trace = buf.getvalue()
    lines = stack_trace.split('\n')
    
    # Process each line to remove the phrase
    processed_lines = []
    for line in lines:
        processed_lines.append(line.split(str(phrase))[-1])
    
    # Join the processed lines
    return "\n".join(processed_lines)


    
@dataclass(slots=True)
class _ABCBasePlotDataset(ABC):
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
class PlotDatasetFlatMesh(_ABCBasePlotDataset):    
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
class PlotDatasetMesh(_ABCBasePlotDataset):
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


class BaseGL3DPlotDataItemMixin(GL3DGraphicsItemMixin):
    sigPlotChanged = QtCore.Signal(object) 
    
    def __init__(self, PlotDatasetClass, parentItem=None, **kwargs):
        self.last=None
        self._dataset: _ABCBasePlotDataset=None
        self._datasetDisplay: _ABCBasePlotDataset=None
        self._cacheData = CacheData()
        self._cacheValid=False
        self._viewBox: GL3DViewBox=None
        _connected_points = self._determineShading()
        
        if _connected_points:
            zFilterMode = "clip"
        else:
            zFilterMode = "filter"
        
        self.data_opts = {"zFilterMode" : zFilterMode,
                          "connectedPoints" : _connected_points,
                          "PlotDatasetClass" : PlotDatasetClass,
                          }
        super().__init__(parentItem=parentItem, **kwargs)
        

        self.setProperty('xViewRangeWasChanged', False)
        self.setProperty('yViewRangeWasChanged', False)
        self.setProperty('zViewRangeWasChanged', False)
        self.setProperty('styleWasChanged', True)
   #     self.setParentItem(parentItem)
    

    def _determineShading(self):
        if hasattr(self, 'smooth') and self.smooth:
            return True
        if hasattr(self, 'computeNormals') and self.computeNormals:
            return True
        if hasattr(self, 'mode'):
            return self.mode in ['triangles', 'triangle_strip']
        return False

    def viewTransform2(self):
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
    
    def viewTransformChanged(self):
        self.invalidateBounds()
        #self.prepareGeometryChange()

    def invalidateBounds(self):
        self._cacheData.reset()
        
    @QtCore.Slot(object, object)
    @QtCore.Slot(object, object, object)
    def viewRangeChanged(self, vb=None, ranges=None, changed=None):
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
            self.hide()
        else:
            self.updateData()
    
    def updateData(self, **kwargs):
        self.invalidateBounds()
        #self.prepareGeometryChange()
        self.informViewBoundsChanged()
        self.sigPlotChanged.emit(self)
    
    def getData(self):
        dataset = self._dataset
        view = self.view()
        if dataset is None or view is None:
            return (None, None, None)
        
 
        autoRange = view.vb.state['autoRange']
        if all(autoRange):
            return dataset.data()
        else:
            datasetDisplayed = self._getDisplayDataset()
            if not datasetDisplayed is None:
                return datasetDisplayed.data()
            return (None, None, None)
    


            
    def getOriginalDataset(self) -> tuple[None, None] | tuple[np.ndarray, np.ndarray, np.ndarray]:
        dataset = self._dataset
        return (None, None, None) if dataset is None else dataset.data()
    
    def _getDisplayDataset(self) -> _ABCBasePlotDataset | None:
        if self._dataset is None:
            self.last=1
            self._cacheValid=False
            return None
        # Return cached processed dataset if available and still valid:
        if all((not self._datasetDisplay is None,
                not self.property('xViewRangeWasChanged'),
                not self.property('yViewRangeWasChanged'),
                not self.property('zViewRangeWasChanged')
                )):
            self._cacheValid=True
            self.last=2
                
            return self._datasetDisplay
        self._cacheValid=False
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
            self.last=3
            
        if not view_range is None and all(allFinite):
            if not any(view.autoRangeEnabled()):
                data = self.clipFromView(data, view_range)        
                self.last=4
                    
        self._datasetDisplay = self.data_opts["PlotDatasetClass"](data, allFinite)
        
        self.setProperty('xViewRangeWasChanged', False)
        self.setProperty('yViewRangeWasChanged', False)
        self.setProperty('zViewRangeWasChanged', False)
        return self._datasetDisplay

    def dataBounds(self,
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
                                                             )
                                                            ):
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
        
        
    def setData(self, *args, **kwargs):
        sig = inspect.signature(self._setDataChild)

        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()  

        call_args = []
        call_kwargs = {}

        for name, param in sig.parameters.items():
            if param.kind in (
                inspect.Parameter.POSITIONAL_ONLY,
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
            ):
                call_args.append(bound.arguments[name])
            elif param.kind == inspect.Parameter.VAR_POSITIONAL:
                call_args.extend(bound.arguments.get(name, ()))
            elif param.kind == inspect.Parameter.KEYWORD_ONLY:
                call_kwargs[name] = bound.arguments[name]
            elif param.kind == inspect.Parameter.VAR_KEYWORD:
                call_kwargs.update(bound.arguments.get(name, {}))

        self.blockUpdates(True)
        self._setDataChild(*call_args, **call_kwargs)
        if isinstance(self.dataAttr, (list, tuple)):
            if all([not attr is None for attr in self.dataAttr]):
                self._dataset = self.data_opts["PlotDatasetClass"](self.dataAttr)
        else:
            if not self.dataAttr is None:    
                self._dataset = self.data_opts["PlotDatasetClass"](self.dataAttr)
        self._datasetDisplay = None
        self.updateItems(styleUpdate=self.property('styleWasChanged'))
        self.blockUpdates(False)
        self.update()
        
    @abstractmethod
    def clipFromView(self, dataset, viewrange):...
    
    @abstractmethod
    def _setDataChild(self, *args, **kwargs):...

    @property
    @abstractmethod
    def dataAttr(self):...


class GL3DMeshPlotDataItemMixin(BaseGL3DPlotDataItemMixin):
    topology_type="mesh"
    def __init__(self, parentItem=None, **kwargs):
        super().__init__(PlotDatasetClass=PlotDatasetMesh,
                        parentItem=parentItem,
                        **kwargs
                        )
        
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
        
    def clipFromView(self, dataset, view_range):
        x, y, z = dataset
        
        x_min, x_max = view_range[0]
        y_min, y_max = view_range[1]
        z_min, z_max = view_range[2]
        
        x_mask = (x >= x_min) & (x <= x_max)
        y_mask = (y >= y_min) & (y <= y_max)
        
        x_filtered = x[x_mask]
        y_filtered = y[y_mask]
                
        z_filtered = z[x_mask, :][:, y_mask]
        z_filtered = np.clip(z_filtered, z_min, z_max)
        return x_filtered, y_filtered, z_filtered

class GL3DFlatMeshPlotDataItemMixin(BaseGL3DPlotDataItemMixin):
    topology_type="FlatMesh"
    
    def __init__(self, parentItem=None, **kwargs):
        super().__init__(PlotDatasetClass=PlotDatasetFlatMesh,
                         parentItem=parentItem,
                         **kwargs
                         )
        
    def _paintHelper(self):
        pos = self.getData()
        
        if np.array_equal(self.pos, pos):
           pos=pos 

        self.blockUpdates(True)
        self._setDataChild(pos=pos)
        self.blockUpdates(False)

    def clipFromView(self, dataset, view_range):
        if self.data_opts["zFilterMode"]=="clip":
            mask = ((dataset[:, 0] >= view_range[0][0]) & (dataset[:, 0] <= view_range[0][1])
                   &(dataset[:, 1] >= view_range[1][0]) & (dataset[:, 1] <= view_range[1][1]) 
                   )
            z_filtered = dataset[mask]
            z_filtered = np.clip(z_filtered, view_range[2][0], view_range[2][1])
        else:
            mask = ((dataset[:, 0] >= view_range[0][0]) & (dataset[:, 0] <= view_range[0][1])
                   &(dataset[:, 1] >= view_range[1][0]) & (dataset[:, 1] <= view_range[1][1]) 
                   &(dataset[:, 2] >= view_range[2][0]) & (dataset[:, 2] <= view_range[2][1])
                   )
            z_filtered = dataset[mask]
        return z_filtered

    def dataBounds(self,
                    frac=(1., 1. ,1),
                    orthoRange=(None, None, None)
                    ) -> Tuple[float, float, float]:
        
        if not self.visible() or self._dataset is None:
            return [[None, None], [None, None], [None, None]]
        else:
            data = self._dataset.data()
            data_t = data[:, 0], data[:, 1], data[:, 2]
            mask = np.ones(len(data), dtype=bool)
            cache_bounds = {}
            mask_container={}

            for ax in range(3):
                if self._cacheData.cacheFlag(ax) is None and all((self._cacheData.frac(ax) == frac[ax],
                                                                  self._cacheData.orthoRange(ax) == orthoRange[ax])):
                    cache_bounds[ax] = self._cacheData.bounds(ax)
                    mask_container[ax] = self._cacheData.mask(ax)
            
                if not orthoRange[ax] is None:
                    mask = (data_t[ax] >= orthoRange[ax][0]) & (data_t[ax] <= orthoRange[ax][1])
                    self._cacheData.setMask(mask, ax)
                    mask_container[ax] = mask
                else:
                    self._cacheData.setMask(None, ax)
            
            x_filtered = data_t[0][mask_container[0]] if 0 in mask_container else data_t[0]
            y_filtered = data_t[1][mask_container[1]] if 1 in mask_container else data_t[1]
            z_filtered = data_t[2][mask_container[2]] if 2 in mask_container else data_t[2]
            limits = [[bound.min(), bound.max()] if i not in cache_bounds else cache_bounds[i] for i, bound in enumerate((x_filtered, y_filtered, z_filtered))]
            self._cacheData.setBounds(limits)
            return self._cacheData.bounds()
        
