#%%
from __future__ import annotations 
from typing import List, Optional, Tuple, Union, Dict, TYPE_CHECKING, Callable, ClassVar

from pyvol_terminal.gl_3D_graphing.widgets import GL3DViewWidget
if TYPE_CHECKING:
    from pyvol_terminal.gl_3D_graphing.graphics_items.GLViewBox import GLViewBox
from pyqtgraph import opengl
from PySide6 import QtWidgets, QtCore, QtGui
import numpy as np
from OpenGL import GL
from pyqtgraph.Qt import QT_LIB
import importlib
import pyqtgraph as pg
from pyvol_terminal.gl_3D_graphing.graphics_items.GL3DAxisItem import GL3DViewBox
from pyvol_terminal.gl_3D_graphing.graphics_items import GL3DViewBox, GLSurfacePlotItem, AbstractGLPlotItem, AbstractGLGraphicsItem, GLScatterPlotItem
from pyqtgraph import opengl
import sys
import cProfile
import sys
import pstats
from pyqtgraph import ButtonItem, icons
from dataclasses import dataclass, InitVar, field
from abc import ABC, abstractmethod
from PySide6 import QtGui, QtCore, QtWidgets
from PySide6.QtWidgets import QGraphicsItem
from enum import Enum, EnumType, Flag, IntFlag
from pyqtgraph import Transform3D
from pyqtgraph import functions as fn
from pyqtgraph.opengl.GLGraphicsItem import GLGraphicsItem
import warnings
import weakref


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

GLOptions = {
    'opaque': {
        GL.GL_DEPTH_TEST: True,
        GL.GL_BLEND: False,
        GL.GL_CULL_FACE: False,
    },
    'translucent': {
        GL.GL_DEPTH_TEST: True,
        GL.GL_BLEND: True,
        GL.GL_CULL_FACE: False,
        'glBlendFuncSeparate': (GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA,
                                GL.GL_ONE, GL.GL_ONE_MINUS_SRC_ALPHA),
    },
    'additive': {
        GL.GL_DEPTH_TEST: False,
        GL.GL_BLEND: True,
        GL.GL_CULL_FACE: False,
        'glBlendFunc': (GL.GL_SRC_ALPHA, GL.GL_ONE),
    },
}    




qt_enums = [QGraphicsItem.GraphicsItemChange.ItemPositionChange,
            QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged, 
            QGraphicsItem.GraphicsItemChange.ItemVisibleChange, 
            QGraphicsItem.GraphicsItemChange.ItemVisibleHasChanged, 
            QGraphicsItem.GraphicsItemChange.ItemSceneChange, 
            QGraphicsItem.GraphicsItemChange.ItemTransformChange,
            QGraphicsItem.GraphicsItemChange.ItemTransformHasChanged,
            QGraphicsItem.GraphicsItemChange.ItemSceneHasChanged, 
            QGraphicsItem.GraphicsItemChange.ItemParentChange,
            QGraphicsItem.GraphicsItemChange.ItemParentHasChanged,
            QGraphicsItem.GraphicsItemChange.ItemChildAddedChange,
            QGraphicsItem.GraphicsItemChange.ItemChildRemovedChange,
            QGraphicsItem.GraphicsItemChange.ItemFlagsChange,
            QGraphicsItem.GraphicsItemChange.ItemFlagsHaveChanged
            ]
    

class GLGraphicsEnumMetaclass(EnumType):
    def __new__(metacls, clsname, bases, clsdict):
        base_enums = clsdict.get('_base_enums', [])
        custom_members = clsdict.get('_custom_members', [])

        ignore_list = list(clsdict.get('_ignore_', []))
        ignore_list.extend(['_base_enums', '_custom_members'])
        clsdict['_ignore_'] = ignore_list

        values = [member.value for member in base_enums]
        max_value = max(values) if values else 0

        for member in base_enums:
            clsdict[member.name] = member.value

        shifts = [1, 2]
        for idx, (name, _) in enumerate(custom_members):
            shift = shifts[idx] if idx < len(shifts) else (idx + 1)
            value = max_value << shift
            clsdict[name] = value

        return super().__new__(metacls, clsname, bases, clsdict)
    
    def __call__(cls, value):
        return super().__call__(value)


qt_flags = [QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations,
            QGraphicsItem.GraphicsItemFlag.ItemHasNoContents,
            QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges,
            ]


class MetaFlag(type(IntFlag)):
    def __call__(cls, value=0):
        return super().__call__(value)




class GLGraphicsItemMixin:
    
    _nextId = 0
    
        
    class GLGraphicsItemChange(Enum, metaclass=GLGraphicsEnumMetaclass):
        _ignore_ = ['_base_enums', '_custom_members'] 
        _base_enums = qt_enums
        _custom_members = [('ItemViewChange', None), ('ItemViewHasChanged', None),
                           ('ItemParentWidgetChange', None), ("ItemParentWidgetHasChanged", None),
          #                 ('ItemDataChange', None), ("ItemParentWidgetHasChanged", None),
                           ]

    class GLGraphicsItemFlag(IntFlag, metaclass=MetaFlag):
        NoFlag = 0
        ItemIgnoresTransformations = QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations.value
        ItemHasNoContents = QGraphicsItem.GraphicsItemFlag.ItemHasNoContents.value
        ItemSendsGeometryChanges = QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges.value


        def __repr__(self):
            if self.value == 0:
                return f"{self.__class__.__name__}({self.value})"
            return super().__repr__()

    
    wrapped_methods = ["setData", "paint"]
    

    def __init__(self, parentItem: 'GLGraphicsItemMixin'=None, **kwargs):
        
        
        self.__parent = None
        self.__view = None
        self.__children = list()
        self.__transform = Transform3D()
        self.__visible = True
        self.__initialized = False
        self.__glOpts = {}
        self.__flags = self.GLGraphicsItemFlag()

        print("\n")
        print("abcGraphicsItem")
        print(f"cls: {self.__class__.__name__}")
        print(f"bases: {self.__class__.__bases__}")
        print(f"isinstance(self, GLGraphicsItem): {isinstance(self, GLGraphicsItem)}")

            
            
        self._connectedView = None
        self._id = GLGraphicsItemMixin._nextId
        GLGraphicsItemMixin._nextId += 1
        self.__blockUpdates: bool=False
        self.__cachedView=None
        self.__parentWidget=None
        self.blockUpdates(False)
        super().__init__(parentItem=parentItem)
        
        print("last")



        self.__parent: GLGraphicsItemMixin | None = None
        self.__view = None
        self.__children: list[GLGraphicsItemMixin] = []#list()
        self.__transform = Transform3D()
        self.__visible = True
        self.__flags = self.GLGraphicsItemFlag()
        
        self.setFlag(self.GLGraphicsItemFlag.ItemSendsGeometryChanges)

        self.__initialized = False
        self.setParentItem(parentItem)
        self.setDepthValue(0)
        self.__glOpts = {}

                
    def blockUpdates(self, flag):
        self.__blockUpdates=flag

    def setFlag(self, flag, enabled=True):
        if isinstance(flag, Flag):
            _ = self.itemChange(self.GLGraphicsItemChange.ItemFlagsChange, enabled)
            
            if enabled:
                new_flags = self.flags() | flag
            else:
                new_flags = self.flags() & ~flag
            
            if self.flags() != new_flags:
                self.__flags = new_flags
            _ = self.itemChange(self.GLGraphicsItemChange.ItemFlagsHaveChanged, enabled)
    
    def flags(self):    
        return self.__flags

    def setParentItem(self, item: 'GLGraphicsItemMixin'):
        changed_enums=[]
        
        if not self.__parent is None:
            if item == self.__parent:
                print(f"self: {self}")
                print(f"item: {item}")
                warnings.warn(f"{item.__class__.__name__} is already a parentItem to {self.__class__.__name__}, ignoring...", UserWarning)
                return
            else:
                self.itemChange(self.GLGraphicsItemChange.ItemParentChange, item)
                self.itemChange(self.GLGraphicsItemChange.ItemChildRemovedChange, item)
                changed_enums.append((self.GLGraphicsItemChange.ItemParentHasChanged, item))
                self.__parent.__removeChild(self)
            
        if not item is None:    
            if len(changed_enums) == 0:
                self.itemChange(self.GLGraphicsItemChange.ItemParentChange, item)
                changed_enums.append((self.GLGraphicsItemChange.ItemParentHasChanged, item))
            changed_enums.append((self.GLGraphicsItemChange.ItemChildAddedChange, self))
            item.__addChild(self)
            
        if not self.__view is None:
            self.itemChange(self.GLGraphicsItemChange.ItemViewChange, item)
            changed_enums.append((self.GLGraphicsItemChange.ItemViewHasChanged, item))
            self.__view.removeItem(self)
        self.__parent = item
        self.__view = None
        
        for change, value in changed_enums:
            self.itemChange(change, value)
    
    
    def __addChild(self, childItem: 'GLGraphicsItemMixin'):
        """Do NOT call this method or override it with setParentItem to the childItem. 
        Doing so will cause infinite recursion."""
        self.__children.append(childItem)

        
    def __removeChild(self, childItem: 'GLGraphicsItemMixin'):
        if childItem in self.__children:
            self.__children.remove(childItem)

    def __paintHelper(self, *args, **kwargs):
        if QGraphicsItem.GraphicsItemFlag.ItemHasNoContents & self.flags():
            return 
        
    def visible(self):
        return self.__visible
        
    def itemChange(self, change, value):
        if change in [self.GLGraphicsItemChange.ItemParentHasChanged, self.GLGraphicsItemChange.ItemSceneHasChanged]:
            if self.__class__.__dict__.get('parentChanged') is not None:
                # user's GraphicsObject subclass has a parentChanged() method
                warnings.warn(
                    "parentChanged() is deprecated and will be removed in the future. "
                    "Use changeParent() instead.",
                    DeprecationWarning, stacklevel=2
                )
                if QT_LIB == 'PySide6' and QtCore.__version_info__ == (6, 2, 2):
                    # workaround PySide6 6.2.2 issue https://bugreports.qt.io/browse/PYSIDE-1730
                    # note that the bug exists also in PySide6 6.2.2.1 / Qt 6.2.2
                    getattr(self.__class__, 'parentChanged')(self)
                else:
                    self.parentChanged()
            else:
                self.changeParent()

    
    
    def setGLOptions(self, opts):

        if isinstance(opts, str):
            opts = GLOptions[opts]
        self.__glOpts = opts.copy()
        self.update()
        
    def updateGLOptions(self, opts):
        """
        Modify the OpenGL state options to use immediately before drawing this item.
        *opts* must be a dictionary as specified by setGLOptions.
        Values may also be None, in which case the key will be ignored.
        """
        self.__glOpts.update(opts)
        
    
    def parentItem(self):
        """Return a this item's parent in the scenegraph hierarchy."""
        return self.__parent
        
        
    def _setView(self, v):
        self.__view = v
        
    def view(self):
        if self.__parent is None:
            # top level object
            return self.__view
        else:
            # recurse
            return self.__parent.view()
        
    def setDepthValue(self, value):

        self.__depthValue = value
        
    def depthValue(self):
        return self.__depthValue
    
    def __setTransformHelper(self, tr):
        self.itemChange(self.GLGraphicsItemChange.ItemTransformChange, tr)
        self.__transform = tr
        self.itemChange(self.GLGraphicsItemChange.ItemTransformHasChanged, tr)
        self.update()

        
    def setTransform(self, tr):
        if not isinstance(tr, Transform3D):
            tr = Transform3D(tr)
        if tr != self.transform():
            self.__setTransformHelper(tr)
        
    def resetTransform(self):
        if self.transform().isIdentity():
            return 
        self.__setTransformHelper(Transform3D())

        
    def applyTransform(self, tr, local):
        
        if local:
            newTransform = self.transform() * tr
        else:
            newTransform = tr * self.transform()
        if newTransform != self.transform():
            self.__setTransformHelper(newTransform)

            
    def transform(self) -> Transform3D:
        """Return this item's transform object."""
        return self.__transform
        
    def viewTransform(self):
        tr = self.__transform
        p = self
        while True:
            p = p.parentItem()
            if p is None:
                break
            tr = p.transform() * tr
        return Transform3D(tr)
        
    def translate(self, dx, dy, dz, local=False):
        tr = Transform3D()
        tr.translate(dx, dy, dz)
        self.applyTransform(tr, local=local)
        
    def rotate(self, angle, x, y, z, local=False):
        """
        Rotate the object around the axis specified by (x,y,z).
        *angle* is in degrees.
        
        """
        tr = Transform3D()
        tr.rotate(angle, x, y, z)
        self.applyTransform(tr, local=local)
    
    def scale(self, x, y, z, local=True):
        """
        Scale the object by (*dx*, *dy*, *dz*) in its local coordinate system.
        If *local* is False, then scale takes place in the parent's coordinates.
        """
        tr = Transform3D()
        tr.scale(x, y, z)
        self.applyTransform(tr, local=local)
    
    
    def hide(self):
        self.setVisible(False, True)
        
    def show(self):
        self.setVisible(True, True)
    
    
    def initialize(self):
        self.initializeGL()
        self.__initialized = True

    def isInitialized(self):
        return self.__initialized
    
    def initializeGL(self):

        pass
    
    def setupGLState(self):
        for k,v in self.__glOpts.items():
            if v is None:
                continue
            if isinstance(k, str):
                func = getattr(GL, k)
                func(*v)
            else:
                if v is True:
                    GL.glEnable(k)
                else:
                    GL.glDisable(k)
    """
    def paint(self):
        self.setupGLState()
        
    def update(self):
        if self.updatesBlocked():
            return

        v = self.view()
        if v is None:
            return
        v.update()
    """
    
    def updatesBlocked(self):
        return self.__blockUpdates

    def setVisible(self, value, explicitly):
        self.__setVisibleHelper(value, True, explicitly)

    def __setVisibleHelper(self, visible, update, explicitly):
        if explicitly:
            self.__explicitlyHidden = visible 
            
        if not self.parentItem() is None and visible and not self.parentItem().visible():
            return 

        if visible == self.visible():
            return 
            
        newVisible = self.itemChange(self.GLGraphicsItemChange.ItemVisibleChange, visible)
        if self.visible() == newVisible:
            return
        
        self.__visible = newVisible
        
        for child in self.childItems():
            if not visible or not child.__explicitlyHidden:
                child.__setVisibleHelper(visible, False, False)
        
        self.update()
        self.itemChange(self.GLGraphicsItemChange.ItemVisibleHasChanged, self.visible())
    
    def childItems(self) -> List['GLGraphicsItemMixin']:
        return list(self.__children)
    
   
    def mapToParent(self, point):
        tr = self.transform()
        if tr is None:
            return point
        return tr.map(point)
        
    def mapFromParent(self, point):
        tr = self.transform()
        if tr is None:
            return point
        return tr.inverted()[0].map(point)
        
    def mapToView(self, point):
        tr = self.viewTransform()
        if tr is None:
            return point
        return tr.map(point)
        
    def mapFromView(self, point):
        tr = self.viewTransform()
        if tr is None:
            return point
        return tr.inverted()[0].map(point)

    def modelViewMatrix(self) -> QtGui.QMatrix4x4:
        if (view := self.view()) is None:
            return QtGui.QMatrix4x4()
        return view.currentModelView()

    def projectionMatrix(self) -> QtGui.QMatrix4x4:
        if (view := self.view()) is None:
            return QtGui.QMatrix4x4()
        return view.currentProjection()

    def mvpMatrix(self) -> QtGui.QMatrix4x4:
        if (view := self.view()) is None:
            return QtGui.QMatrix4x4()
        return view.currentProjection() * view.currentModelView()


    def _updateView(self):
        ## called to see whether this item has a new view to connect to
        ## NOTE: This is called from GraphicsObject.itemChange or GraphicsWidget.itemChange.

        if not hasattr(self, '_connectedView'):
            # Happens when Python is shutting down.
            return
        self.forgetViewBox()
        
        ## check for this item's current viewbox
        view = self.getViewBox()
        
        oldView = None
        if not self._connectedView is None:
            oldView = self._connectedView()
        
        if view is oldView:
            # "  already have view", view
            return

        ## disconnect from previous view
        if not oldView is None:
            for signal, slot in [('sigRangeChanged', self.viewRangeChanged),
                                 ('sigTransformChanged', self.viewTransformChanged)]:
                try:
                    getattr(oldView, signal).disconnect(slot)
                except (TypeError, AttributeError, RuntimeError):
                    # TypeError and RuntimeError are from pyqt and pyside, respectively
                    pass
            
            self._connectedView = None
            
        if not view is None:
            view.sigRangeChanged.connect(self.viewRangeChanged)
            view.sigTransformChanged.connect(self.viewTransformChanged)
            self._connectedView = weakref.ref(view)
            self.viewRangeChanged()
            self.viewTransformChanged()
        self._replaceView(oldView)        
        self.viewChanged(view, oldView)        

    def setParentWidget(self, parent=None):
        
        if self.parentWidget() != parent:
            self.itemChange(self.GLGraphicsItemChange.ItemParentWidgetChange, parent) 
            self.__parentWidget = parent
            self.itemChange(self.GLGraphicsItemChange.ItemParentWidgetHasChanged, parent) 
    
    def parentWidget(self) -> GL3DViewWidget:
        return self.__parentWidget

    def viewChanged(self, view, oldView):
        """Called when this item's view has changed
        (ie, the item has been added to or removed from a ViewBox)"""
        
    def viewRect(self):
        """Return the visible bounds of this item's ViewBox or GraphicsWidget,
        in the local coordinate system of the item."""
        if self.__cachedView is not None:
            return self.__cachedView

        # Note that in cases of early returns here, the view cache stays empty (None).
        view = self.getViewBox()
        if view is None:
            return None
        bounds = self.mapRectFromView(view.viewRect())
        if bounds is None:
            return None

        bounds = bounds.normalized()
        
        self.__cachedView = bounds
        
        ## nah.
        #for p in self.getBoundingParents():
            #bounds &= self.mapRectFromScene(p.sceneBoundingRect())

        return bounds
        
    def _replaceView(self, oldView, item=None):
        if item is None:
            item = self
        for child in item.childItems():
            if isinstance(child, '"GLGraphicsItemMixin"'):
                if child.getViewBox() is oldView:
                    child._updateView()
                        #self._replaceView(oldView, child)
            else:
                self._replaceView(oldView, child)
        

    def parentChanged(self):
        self.changeParent(self)
        
    def changeParent(self):
        self._updateView()

    
    @QtCore.Slot()
    def viewTransformChanged(self):
        self.__cachedView = None
        
    
        
    def informViewBoundsChanged(self):
        view = self.getViewBox()
        if view is not None and hasattr(view, 'implements') and view.implements('ViewBox'):
            view.itemBoundsChanged(self)
    

    def allChildItems(self, root=None):
        """Return list of the entire item tree descending from this item."""
        if root is None:
            root = self
        tree = []
        for ch in root.childItems():
            tree.append(ch)
            tree.extend(self.allChildItems(ch))
        return tree
    
    @QtCore.Slot(object, object)
    @QtCore.Slot(object, object, object)
    def viewRangeChanged(self, vb=None, ranges=None, changed=None):...


    def mapRectFromView(self, obj):
        vt = self.viewTransform()
        if vt is None:
            return None
        vt = fn.invertQTransform(vt)
        return vt.mapRect(obj)

    def getViewBox2(self):
        

        if self._viewBox is None:
            while True:
                parent = self.parentItem()
                if isinstance(parent, GL3DViewBox):
                    self._viewBox = parent
                    break
            return self._viewBox if self._viewBox else None

    def getViewBox(self) -> GL3DViewBox:
        if self._viewBox is None:
            p = self
            while True:
                try:
                    p = p.parentItem()
                except RuntimeError:  ## sometimes happens as items are being removed from a scene and collected.
                    return None
                if p is None:
                    return None
                if hasattr(type(p), 'implements'):
                    if p.implements('ViewBox'):
                        self._viewBox = weakref.ref(p)
                        break
        
        return self._viewBox() if self._viewBox else None
    
    
    def forgetViewBox(self):
        self._viewBox = None
"""
class _Temp2("GLGraphicsItemMixin"):
    pass

class AbstractMeta(meta.QABCMeta):
    def __call__(cls, *args, **kwargs):
        self = cls.__new__(cls, *args, **kwargs)
        
        self._original_class = cls
        self.__class__ = _Temp
        parentItem = kwargs.pop("parentItem", None)
        "GLGraphicsItemMixin".__init__(self, parentItem=parentItem)
        
        self.__class__ = self._original_class
        del self._original_class
        
        if hasattr(self, '__init__') and self.__init__ is not None:
            self.__init__(*args, **kwargs)
        
        
        return self

"""

from dataclasses import dataclass
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




class AbstractGLPlotItem(GLGraphicsItemMixin):
    sigPlotChanged = QtCore.Signal(object) 
    
    def __init__(self, topology_type="", view_box=None, parentItem=None, **kwargs):
        print("init AbstractGLPlotItem")
        print(f"isinstance(self, GLGraphicsItem): {isinstance(self, GLGraphicsItem)}")
        
        super().__init__(parentItem=parentItem, **kwargs)
        
        
        self._dataset=None
        self._datasetDisplay=None
        self._cacheData = CacheData()
        self.plotdataset_cls=None
        self._viewBox: GL3DViewBox=view_box
        if topology_type=="Mesh":
            self.plotdataset_cls=PlotDatasetMesh
        elif topology_type=="FlatMesh":
            self.plotdataset_cls=PlotDatasetFlatMesh
            
        self.extra_opts={"clipToView" : False,
                         
                         }
        print(f"hasattr(self, ): {hasattr(self, "setProperty")}")
        """
        self.setProperty('xViewRangeWasChanged', False)
        
        self.setProperty('yViewRangeWasChanged', False)
        self.setProperty('zViewRangeWasChanged', False)
        self.setProperty('styleWasChanged', True)  # force initial update
        """
       # self.setParentItem(parentItem)


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

    
    #@abc.abstractmethod
    #def _setDataHelper(self, *args, **kwargs):...
    
    #@abc.abstractmethod
    #def setData(self, *args, **kwargs): ...
        
    
    def dataRect(self): 
        return None if self._dataset is None else self._dataset.dataBounds()
    """
    @abc.abstractmethod
    def dataBounds2(self,
                   ax: int,
                   frac=(1,1),
                   orthoRange=None
                   ) -> Tuple[float, float]:...
    """
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
            raise
            self.hide()
            return
        else:
            self.updateData(**dataset.dataKwargs())
    
    #@classmethod
    #@abstractmethod
    def clipDataFromVRange(cls, dataset, viewrange):
        return dataset
    
    def updateData(self, **kwargs):
        self.invalidateBounds()
        #self.prepareGeometryChange()
        self.informViewBoundsChanged()
      #  self.setData(**kwargs)
        
     #   self.update()
        self.sigPlotChanged.emit(self)
    
    def getData(self):
        dataset = self._getDisplayDataset()
        return (None, None, None) if dataset is None else dataset.data()

        
    def updateData222(self, *args, **kwargs):
        self.invalidateBounds()
        #self.prepareGeometryChange()
        self.informViewBoundsChanged()
        self.update()
        self.sigPlotChanged.emit(self)
    
    def getOriginalDataset(self) -> tuple[None, None] | tuple[np.ndarray, np.ndarray]:
        return self._dataset.data()
    
    def _getDisplayDataset(self):


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
    
    
class CustomGLSurfacePlotItem(AbstractGLPlotItem, opengl.GLSurfacePlotItem):
    """
    **Bases:** :class:`GLMeshItem <pyqtgraph.opengl.GLMeshItem>`
    
    Displays a surface plot on a regular x,y grid
    """
    def __init__(self, x=None, y=None, z=None, colors=None, parentItem=None, **kwds):
        print("CustomGLSurfacePlotItem")
        super().__init__(parentItem=parentItem, x=x, y=y, z=z, colors=colors, **kwds)
        
        
def filter_data_mask22222(x, y, z, limits):
    x_min, x_max = limits[0]
    y_min, y_max = limits[1]
    z_min, z_max = limits[2]
    
    # Create masks for x and y
    x_mask = (x >= x_min) & (x <= x_max)
    y_mask = (y >= y_min) & (y <= y_max)
    
    # Apply masks to x and y
    x_filtered = x[x_mask]
    y_filtered = y[y_mask]
    
    # Apply masks to z (rows correspond to x, columns to y)
    z_filtered = z[x_mask, :][:, y_mask]
    z_filtered = np.clip(z_filtered, z_min, z_max)
    
    return x_filtered, y_filtered, z_filtered

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

    
def _setDataHelper(self, **kwds):
    colors = kwds.get("colors", None)
    x, y, z = kwds.get("x", None), kwds.get("y", None), kwds.get("z", None)
    if all([ax is None for ax in (x, y, z)]):
        if colors is None:
            kwds["colors"]=colors
            return kwds
    else:
        pos = [ax if not ax is None else getattr(self, f"_{ax_str}") for ax_str, ax in zip("xyz", (x, y, z))]
        self._dataset = self.plotdataset_cls(tuple(pos))
        xyz = self.getData()
        self._datasetDisplay = None

        self._datasetDisplay = None
        kwds.update({ax_str : ax for ax_str, ax in zip("xyz", xyz) if not ax is None})
    if not colors is None:
        kwds["colors"]=colors
    return kwds


def clipDataFromVRange222(cls, data, view_range):
    clipped_dataset=[]
    new_display_z=None
    x, y, z = data
    for ax, arr in enumerate((x,y,z)):
        if ax < 2:
            mask_ax = ([ax] >= view_range[ax][0]) & (arr <= view_range[ax][1])
            clipped_dataset.append(arr[mask_ax])
            if ax == 0:
                new_display_z = arr[mask_ax,:]
            else:
                new_display_z = arr[:,mask_ax]
        else:
            new_display_z = np.clip(new_display_z, view_range[ax][0], view_range[ax][1])
            clipped_dataset.append(new_display_z)

    return tuple(clipped_dataset)


@classmethod
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


def paint(self):        
    
    # WARNING: can return (None, None, None) if self._getDisplayDataset() returns None
    x, y, z = self.getData()

    
    if not x is None and not np.array_equal(self._x, x):

        if self._x is None or len(x) != len(self._x):
            self._vertexes = None
        self._x = x
    
    if not y is None and not np.array_equal(self._y, y):
        if self._y is None or len(y) != len(self._y):
            self._vertexes = None
        self._y = y


    if not z is None and not np.array_equal(self._z, z):

        if not self._x is None and z.shape[0] != len(self._x):
            raise Exception('Z values must have shape (len(x), len(y))')
        if not self._y is None and z.shape[1] != len(self._y):
            raise Exception('Z values must have shape (len(x), len(y))')
        self._z = z
        if not self._vertexes is None and self._z.shape != self._vertexes.shape[:2]:
            self._vertexes = None
    
    
    if self._z is None:
        return
    
    updateMesh = False
    newVertexes = False
    
    ## Generate vertex and face array
    if self._vertexes is None:
        newVertexes = True
        self._vertexes = np.empty((self._z.shape[0], self._z.shape[1], 3), dtype=np.float32)
        self.generateFaces()
        self._meshdata.setFaces(self._faces)
        updateMesh = True
    
    if newVertexes or (not x is None and not np.array_equal(self._x, x)):
        if x is None:
            if self._x is None:
                x = np.arange(self._z.shape[0])
            else:
                x = self._x
        self._vertexes[:, :, 0] = x.reshape(len(x), 1)
        updateMesh = True
    
    if newVertexes or (not y is None and not np.array_equal(self._y, y)):
        if y is None:
            if self._y is None:
                y = np.arange(self._z.shape[1])
            else:
                y = self._y
        self._vertexes[:, :, 1] = y.reshape(1, len(y))
        updateMesh = True
    
    if newVertexes or (not z is None and not np.array_equal(self._z, z)):
        self._vertexes[...,2] = self._z
        updateMesh = True
            
    self.blockUpdates(True)
    if updateMesh:
        self._meshdata.setVertexes(self._vertexes.reshape(self._vertexes.shape[0]*self._vertexes.shape[1], 3))
        self.meshDataChanged()
    self.blockUpdates(False)
    super().paint()



@classmethod
def insert_axis_and_interpolate(cls, arr, axis_values, data, axis=0):
    """Insert missing axis_values into arr, interpolate in data accordingly."""
    arr = np.asarray(arr)
    data = np.asarray(data)
    sort_idx = np.argsort(arr)
    arr = arr[sort_idx]
    data = np.take(data, sort_idx, axis=axis)

    for val in axis_values:
        if val < arr[0] or val > arr[-1] or np.any(np.isclose(arr, val)):
            continue
        idx = np.searchsorted(arr, val)
        a0, a1 = arr[idx - 1], arr[idx]
        t = (val - a0) / (a1 - a0)

        if axis == 0:
            d0, d1 = data[idx - 1], data[idx]
            d_new = (1 - t) * d0 + t * d1
        else:
            d0, d1 = data[:, idx - 1], data[:, idx]
            d_new = (1 - t) * d0 + t * d1

        arr = np.insert(arr, idx, val)
        data = np.insert(data, idx, d_new[np.newaxis, :] if axis == 0 else d_new[:, np.newaxis], axis=axis)

    return arr, data       


def setData(self, x=None, y=None, z=None, colors=None):
    print("setData")
    if not x is None:
        if self._x is None or len(x) != len(self._x):
            self._vertexes = None
        self._x = x
    
    if not y is None:
        if self._y is None or len(y) != len(self._y):
            self._vertexes = None
        self._y = y
    
    if not z is None:
        if not self._x is None and z.shape[0] != len(self._x):
            raise Exception('Z values must have shape (len(x), len(y))')
        if not self._y is None and z.shape[1] != len(self._y):
            raise Exception('Z values must have shape (len(x), len(y))')
        self._z = z
        if not self._vertexes is None and self._z.shape != self._vertexes.shape[:2]:
            self._vertexes = None
    
    if colors is not None:
        self._colors = colors
        self._meshdata.setVertexColors(colors)
    
    if self._z is None:
        return
    
    updateMesh = False
    newVertexes = False
    
    ## Generate vertex and face array
    if self._vertexes is None:
        newVertexes = True
        self._vertexes = np.empty((self._z.shape[0], self._z.shape[1], 3), dtype=np.float32)
        self.generateFaces()
        self._meshdata.setFaces(self._faces)
        updateMesh = True
    
    if newVertexes or x is not None:
        if x is None:
            if self._x is None:
                x = np.arange(self._z.shape[0])
            else:
                x = self._x
        self._vertexes[:, :, 0] = x.reshape(len(x), 1)
        updateMesh = True
    
    if newVertexes or y is not None:
        if y is None:
            if self._y is None:
                y = np.arange(self._z.shape[1])
            else:
                y = self._y
        self._vertexes[:, :, 1] = y.reshape(1, len(y))
        updateMesh = True
    
    if newVertexes or z is not None:
        self._vertexes[...,2] = self._z
        updateMesh = True
    
    if all((not self._x is None, not self._y is None, not self._z is None)):
        pos = [getattr(self, f"_{ax_str}") for ax_str, ax in zip("xyz", (x, y, z))]
        self._dataset = self.plotdataset_cls(tuple(pos))
    self._datasetDisplay=None
    self.blockUpdates(True)
    self.updateItems(styleUpdate=self.property('styleWasChanged'))
    self.blockUpdates(False)

    if updateMesh:
        self._meshdata.setVertexes(self._vertexes.reshape(self._vertexes.shape[0]*self._vertexes.shape[1], 3))
        self.meshDataChanged()
        
    
    #self.updateItems(styleUpdate=self.property('styleWasChanged'))
    #self.blockUpdates(False)
    #self.informViewBoundsChanged()

    #   self.sigPlotChanged.emit(self)
    
    
def generateFaces(self):
    cols = self._z.shape[1]-1
    rows = self._z.shape[0]-1
    faces = np.empty((cols*rows*2, 3), dtype=np.uint32)
    rowtemplate1 = np.arange(cols).reshape(cols, 1) + np.array([[0, 1, cols+1]])
    rowtemplate2 = np.arange(cols).reshape(cols, 1) + np.array([[cols+1, 1, cols+2]])
    for row in range(rows):
        start = row * cols * 2 
        faces[start:start+cols] = rowtemplate1 + row * (cols+1)
        faces[start+cols:start+(cols*2)] = rowtemplate2 + row * (cols+1)
    self._faces = faces

def create_pos():
    X = np.arange(-5, 5, 0.5)
    Y = np.arange(-3, 3, 0.5)
    X_mat, Y_mat = np.meshgrid(X, Y, indexing="xy")
    R = np.sqrt(X_mat**2 + Y_mat**2)

    m1 = 1
    
    Z_mat = m1 * np.sin(R) 
    return X_mat, Y_mat, Z_mat, m1

class CustomColorMap(pg.ColorMap):
    def __init__(self, colourmap_style: str):
        pos = np.linspace(0, 1, 500)          
        try:
            colourmap = pg.colormap.get(colourmap_style)
        except:
            print(f"{colourmap_style} is not in pyqtgraph, using default inferno")
            colourmap = pg.colormap.get("inferno")

        colors = colourmap.map(pos, mode='byte')        
        super().__init__(pos=pos, color=colors, mode='byte')

def create_objects(X_mat, Y_mat, Z_mat, m1) -> AbstractGLPlotItem:

    
    X_vec, Y_vec, Z_vect = X_mat.flatten(), Y_mat.flatten(), Z_mat.flatten()
    
    pos_scatter = np.column_stack((X_vec, Y_vec, Z_vect))
    """
    scatter = GLScatterPlotItem.GLScatterPlotItem(pos=pos_scatter,
                                                  glOptions='opaque',
                                                  color=(1, 0, 1, 1)
                                                  )
    """
    scatter=None
    pos_surface = X_mat[0], Y_mat[:,1], Z_mat.T
    colormap = CustomColorMap("inferno")
    
    z_norm = (Z_mat - Z_mat.min()) / (Z_mat.max() - Z_mat.min())
    colors = colormap.map(np.linspace(0, 1, 500), mode='byte')
    # Map normalized Z to RGB colors


    
    surface = CustomGLSurfacePlotItem(x=pos_surface[0],
                                                  y=pos_surface[1],
                                                  z=pos_surface[2],
                                                  glOptions='opaque',
                                                  shader="shaded",
                                                  colors=colors
                                                  )
    
    print(f"surface._x: {surface._x}")
    return scatter, surface




class Window(QtWidgets.QMainWindow):
    def __init__(self, *args):
        super().__init__(*args)
        
        self.gl_view = opengl.GLViewWidget()
        """
        worldRange=[[0.,1.], [0.,1.],[0.,1.]]

        self.viewBox = GLViewBox.GLViewBox(worldRange=worldRange)
        
        self.gl_view = GLPlotWidget.GLPlotWidget(
                                            # worldRange=worldRange,
                                             #worldRange=np.array([[0.,1.]]*3)
                                             viewBox=self.viewBox
                                             )

        """
   #     self.central_layout = QtWidgets.QVBoxLayout(self)
    #    self.central_layout.addWidget(self.gl_view)
        self.setCentralWidget(self.gl_view)
        self.gl_view.opts["distance"]=5
        self.gl_view.update()
        self.setCentralWidget(self.gl_view)
        self.setGeometry(0, 0, 500, 300)
        self.show()
        self.X_mat, self.Y_mat, self.Z_mat, self.m1 = create_pos()
        self.scatter, self.surface = create_objects(self.X_mat, self.Y_mat, self.Z_mat, self.m1)    
        
        self.gl_view.addItem(self.surface)
        
        
def main():
    import sys
    app = QtWidgets.QApplication(sys.argv)
    win = Window()
   # win.timer.start(750)
    sys.exit(app.exec())

if __name__ == "__main__":
    main()