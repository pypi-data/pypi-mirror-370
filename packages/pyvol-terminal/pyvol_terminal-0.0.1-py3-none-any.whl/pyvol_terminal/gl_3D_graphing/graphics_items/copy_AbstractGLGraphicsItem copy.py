from __future__ import annotations 
from typing import List, Optional, Tuple, Union, Dict, TYPE_CHECKING, Callable
if TYPE_CHECKING:
    from .GL3DViewBox import GL3DViewBox
    from enum import Flag 

import weakref
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets, isQObjectAlive
import operator
from functools import reduce
from abc import ABCMeta, abstractmethod
import numpy as np
from ..import meta
from pyqtgraph import Transform3D
from pyqtgraph import functions as fn
import abc
import traceback
import inspect
import warnings
from pyqtgraph.Qt import QT_LIB
from PySide6.QtWidgets import QGraphicsItem
from PySide6 import QtCore
from OpenGL import GL
from functools import wraps

from enum import Enum, EnumType, Flag, IntFlag

from pyqtgraph.Qt import QtCore, QtGui

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


class AbstractGLGraphicsItem(QtCore.QObject, metaclass=meta.QABCMeta):
    
    _nextId = 0
    
        
    class GLGraphicsItemChange(Enum, metaclass=GLGraphicsEnumMetaclass):
        _ignore_ = ['_base_enums', '_custom_members'] 
        _base_enums = qt_enums
        _custom_members = [('ItemViewChange', None), ('ItemViewHasChanged', None)]

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
    
    



    def __init__(self, parentItem: 'AbstractGLGraphicsItem' = None, **kwargs):
        super().__init__()
        self._id = AbstractGLGraphicsItem._nextId
        AbstractGLGraphicsItem._nextId += 1
        self.__blockUpdates: bool=False
        self.blockUpdates(False)
        self.__cachedView=None

        self.__parent: AbstractGLGraphicsItem | None = None
        self.__view = None
        self.__children: list[AbstractGLGraphicsItem] = list()
        self.__transform = Transform3D()
        self.__visible = True
        self.__flags = self.GLGraphicsItemFlag()
        
        self.setFlag(self.GLGraphicsItemFlag.ItemSendsGeometryChanges)
        (f"\nAbstract__init__: {parentItem}")
        self.__initialized = False
        self.setParentItem(parentItem)
        self.setDepthValue(0)
        self.__glOpts = {}

                
    def blockUpdates(self, flag):
        print(f"\nblockUpdates: {flag}")
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

    
    

    def setParentItem(self, item: 'AbstractGLGraphicsItem'):
        changed_enums=[]
        
        if not self.__parent is None:
            if item == self.__parent:
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
    
    
    def __addChild(self, childItem: 'AbstractGLGraphicsItem'):
        """Do NOT call this method or override it with setParentItem to the childItem. 
        Doing so will cause infinite recursion."""
        self.__children.append(childItem)

        
    def __removeChild(self, childItem: 'AbstractGLGraphicsItem'):
        if childItem in self.__children:
            self.__children.remove(childItem)

    def __paintHelper(self, *args, **kwargs):
        if QGraphicsItem.GraphicsItemFlag.ItemHasNoContents & self.flags():
            return 
        
        
    def visible(self):
        return self.__visible
        
    def itemChange(self, change, value):...

    
    
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

        self.setVisible(False)
        
    def show(self):
        self.setVisible(True)
    
    
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
    
    def paint(self):
        self.setupGLState()
        
    def update(self):
        print("\nupdate\n")
        print(f"self.updateBlocked(): {self.updateBlocked()}")
        if self.updateBlocked():
            return

        v = self.view()
        print(f"v: {v}")
        if v is None:
            return
        v.update()
    
    def updateBlocked(self):
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
    
    def childItems(self) -> List['AbstractGLGraphicsItem']:
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
            if isinstance(child, 'AbstractGLGraphicsItem'):
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
        print(f"view: {view}")
        print(f)
        print(f"\ninformViewBoundsChanged: {view is not None and hasattr(view, 'implements') and view.implements('ViewBox')}")
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




class AbstractGLGraphicsItem22(AbstractGLGraphicsItem, metaclass=meta.QABCMeta):
    def __init__(self, parentItem=None, **kwargs):
        self._blockUpdate: bool
        self.__inform_view_on_changes=True
        self.blockUpdates(False)
        self._viewBox: GL3DViewBox=None
        self._viewWidget=None
        self._connectedView=None
        super().__init__()
        self._connectedView=None

        self._GLGraphicsItem__parent = None 
        self._GLGraphicsItem__children = list() 
        self._GLGraphicsItem__view = None 
        self.__cachedView = None
        self.setParentItem(parentItem)


    def blockUpdates(self, flag):
        self._blockUpdate=flag
        
    @property
    def __parent(self):
        return self._GLGraphicsItem__parent
    
    @__parent.setter
    def __parent(self, parentItem):
        self._GLGraphicsItem__parent=parentItem
    
    @property
    def __view(self):
        return self._GLGraphicsItem__view
    
    @__view.setter
    def __view(self, view):
        self._GLGraphicsItem__view=view

    @property
    def __parent(self):
        return self._GLGraphicsItem__parent
    
    @__parent.setter
    def __parent(self, parentItem):
        self._GLGraphicsItem__parent=parentItem

    @property
    def __parent(self):
        return self._GLGraphicsItem__parent
    
    @__parent.setter
    def __parent(self, parentItem):
        self._GLGraphicsItem__parent=parentItem

    @property
    def __parent(self):
        return self._GLGraphicsItem__parent
    
    @__parent.setter
    def __parent(self, parentItem):
        self._GLGraphicsItem__parent=parentItem


    @property
    def __parent(self):
        return self._GLGraphicsItem__parent
    
    @__parent.setter
    def __parent(self, parentItem):
        self._GLGraphicsItem__parent=parentItem

    



    @property
    def __parent(self):
        return self._GLGraphicsItem__parent
    
    @__parent.setter
    def __parent(self, parentItem):
        
        self._GLGraphicsItem__parent=parentItem
        self.itemChange(self.GraphicsItemChange.ItemChildAddedChange, self)

    @abc.abstractmethod
    def _internal_update(self):...

    def update(self):
        ("update")
        if not self._blockUpdate:
            self._internal_update()
            
    def updatesBlocked(self):
        return self._blockUpdate

    @property
    def parent(self):
        """Getter for parent property"""
        return self._GLGraphicsItem__parent

    @parent.setter
    def parent(self, item: AbstractGLGraphicsItem):
        if self._GLGraphicsItem__parent is not None:
            self._GLGraphicsItem__parent._GLGraphicsItem__children.remove(self)
        if item is not None:
            item._GLGraphicsItem__children.append(self)
            item.itemChange(item.GraphicsItemChange.ItemChildAddedChange, self)
            

        if self._GLGraphicsItem__view is not None:
            self._GLGraphicsItem__view.removeItem(self)

        self._GLGraphicsItem__parent = item
        self.itemChange(self.GraphicsItemChange.ItemParentHasChanged, item)
        self._GLGraphicsItem__view = None

    def setParentItem(self, item):
        self.parent = item

    def boundingRect(self):
        return QtWidgets.QGraphicsItem.boundingRect(self)

    def childItems(self):
        return list(self._GLGraphicsItem__children)

    def getViewBox2(self) -> GL3DViewBox:
        return self._viewBox
    
    
    
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
    
    
        
    
    def parentChanged(self):
        self.changeParent(self)


    def changeParent(self):
        self._updateView()
        
    def forgetViewWidget(self):
        self._viewWidget = None
        
    def forgetViewBox(self):
        self._viewBox = None

    def _updateView2(self):
        ## called to see whether this item has a new view to connect to
        ## NOTE: This is called from GraphicsObject.itemChange or GraphicsWidget.itemChange.


        ## It is possible this item has moved to a different ViewBox or widget;
        ## clear out previously determined references to these.
        self.forgetViewBox()
        self.forgetViewWidget()
        
        ## check for this item's current viewbox or view widget
        view = self.getViewBox()
        #if view is None:
            ## "  no view"
            #return

        oldView = None
        if self._connectedView is not None:
            oldView = self._connectedView()
            
        if view is oldView:
            # "  already have view", view
            return

        if oldView is not None:
            Device = 'Device' if hasattr(oldView, 'sigDeviceRangeChanged') else ''
            for signal, slot in [(f'sig{Device}RangeChanged', self.viewRangeChanged),
                                 (f'sig{Device}TransformChanged', self.viewTransformChanged)]:
                try:
                    getattr(oldView, signal).disconnect(slot)
                except (TypeError, AttributeError, RuntimeError):
                    # TypeError and RuntimeError are from pyqt and pyside, respectively
                    pass
            
            self._connectedView = None

        if view is not None:
            # "connect:", self, view
            if hasattr(view, 'sigDeviceRangeChanged'):
                # connect signals from GraphicsView
                view.sigDeviceRangeChanged.connect(self.viewRangeChanged)
                view.sigDeviceTransformChanged.connect(self.viewTransformChanged)
            else:
                # connect signals from ViewBox
                view.sigRangeChanged.connect(self.viewRangeChanged)
                view.sigTransformChanged.connect(self.viewTransformChanged)
            self._connectedView = weakref.ref(view)
            self.viewRangeChanged()
            self.viewTransformChanged()
        
        ## inform children that their view might have changed
        self._replaceView(oldView)
        
        self.viewChanged(view, oldView)
        
            
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
            if isinstance(child, AbstractGLGraphicsItem):
                if child.getViewBox() is oldView:
                    child._updateView()
                        #self._replaceView(oldView, child)
            else:
                self._replaceView(oldView, child)
        


    
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



