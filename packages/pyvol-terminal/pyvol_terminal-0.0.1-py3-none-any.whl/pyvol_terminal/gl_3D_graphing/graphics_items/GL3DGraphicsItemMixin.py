from __future__ import annotations 
from typing import List, Optional, Tuple, Union, Dict, TYPE_CHECKING, Callable
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
from pyqtgraph.Transform3D import Transform3D


class QABCMeta(ABCMeta, type(QtCore.QObject)):
    """Meta class for OpenGL mixin objects, combining ABC and QObject."""
    def __new__(mcls, name, bases, ns, **kw):
        cls = super().__new__(mcls, name, bases, ns, **kw)
        abc._abc_init(cls)
        return cls
    def __call__(cls, *args, **kw):
        if cls.__abstractmethods__:
            raise TypeError(f"Can't instantiate abstract class {cls.__name__} without an implementation for abstract methods {set(cls.__abstractmethods__)}")
        return super().__call__(*args, **kw)



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


class MetaFlag(type(Flag)):
    def __call__(cls, value=0):
        return super().__call__(value)


class GL3DGraphicsItemMixin(GLGraphicsItem, metaclass=QABCMeta):
    
    class GLGraphicsItemChange(Enum, metaclass=GLGraphicsEnumMetaclass):
        _ignore_ = ['_base_enums', '_custom_members'] 
        _base_enums = qt_enums
        _custom_members = [('ItemViewChange', None), ('ItemViewHasChanged', None),
                           ('ItemParentWidgetChange', None), ("ItemParentWidgetHasChanged", None),
                           ('ItemDataChange', None), ("ItemDataHasChanged", None),
                           ]

    class GLGraphicsItemFlag(Flag, metaclass=MetaFlag):
        NoFlag = 0
        ItemIgnoresTransformations = QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations.value
        ItemHasNoContents = QGraphicsItem.GraphicsItemFlag.ItemHasNoContents.value
        ItemSendsGeometryChanges = QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges.value
        ItemSendsDataChanges = 0x100
        

        def __repr__(self):
            if self.value == 0:
                return f"{self.__class__.__name__}({self.value})"
            return super().__repr__()

    def __init__(self, parentItem:'GL3DGraphicsItemMixin'=None, **kwargs):
        self._flags = self.GLGraphicsItemFlag()
        self._blockUpdates: bool=False
        self._cachedView=None
        self._parentWidget=None
        self._connectedView=None
        self._explicitlyHidden=False
        super().__init__(parentItem=parentItem, **kwargs)
    
    def blockUpdates(self, flag):
        self._blockUpdates=flag
        
    def updatesBlocked(self):
        return self._blockUpdates

    @property
    def _parent(self):
        return self._GLGraphicsItem__parent

    @_parent.setter
    def _parent(self, parentItem):
        self._GLGraphicsItem__parent = parentItem

    @property
    def _children(self):
        return self._GLGraphicsItem__children

    @_children.setter
    def _children(self, childItem):
        self._GLGraphicsItem__children = childItem

    @property
    def _view(self):
        return self._GLGraphicsItem__view

    @_view.setter
    def _view(self, view):
        self._GLGraphicsItem__view = view
        
    @property
    def _visible(self):
        return self._GLGraphicsItem__visible

    @_visible.setter
    def _visible(self, flag):
        self._GLGraphicsItem__visible = flag

    @property
    def _transform(self):
        return self._GLGraphicsItem__transform

    @_transform.setter
    def _transform(self, tr):
        self._GLGraphicsItem__transform = tr

    @property
    def _initialized(self):
        return self._GLGraphicsItem__initialized

    @_initialized.setter
    def _initialized(self, flag):
        self._GLGraphicsItem__initialized=flag

    @property
    def _glOpts(self):
        return self._GLGraphicsItem__glOpts

    @_glOpts.setter
    def _glOpts(self, opts):
        self._GLGraphicsItem__glOpts = opts
        
    #@property
 #   def __flags(self):
   #     return self._GLGraphicsItem__flags
    
  #  @__flags.setter
 #   def __flags(self, flags):
      #  self._GLGraphicsItem__flags = flags

        

    def setFlag(self, flag, enabled=True, ):
        if isinstance(flag, Flag):
            _ = self.itemChange(self.GLGraphicsItemChange.ItemFlagsChange, enabled)
        
            if enabled:
                new_flags = self.flags() | flag
            else:
                new_flags = self.flags() & ~flag
            
            if self.flags() != new_flags:
                self._flags = new_flags
            _ = self.itemChange(self.GLGraphicsItemChange.ItemFlagsHaveChanged, enabled)
        
    def flags(self):    
        return self._flags
    
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
            
            
        return value

    def setParentItem(self, item: 'GL3DGraphicsItemMixin'):
        changed_enums=[]
        if not self._parent is None:
            if item == self._parent:
                warnings.warn(f"{item.__class__.__name__} is already a parentItem to {self.__class__.__name__}, ignoring...", UserWarning)
                return
            else:
                self.itemChange(self.GLGraphicsItemChange.ItemParentChange, item)
                self.itemChange(self.GLGraphicsItemChange.ItemChildRemovedChange, item)
                changed_enums.append((self.GLGraphicsItemChange.ItemParentHasChanged, item))
                self._GLGraphicsItem__parent.childItems().remove(self)
            
        if not item is None:    
            if len(changed_enums) == 0:
                self.itemChange(self.GLGraphicsItemChange.ItemParentChange, item)
                changed_enums.append((self.GLGraphicsItemChange.ItemParentHasChanged, item))
            changed_enums.append((self.GLGraphicsItemChange.ItemChildAddedChange, self))
            item._GLGraphicsItem__children.append(self)
            
        if not self._view is None:
            self.itemChange(self.GLGraphicsItemChange.ItemViewChange, item)
            changed_enums.append((self.GLGraphicsItemChange.ItemViewHasChanged, item))
            self._view.removeItem(self)
        
        self._parent = item
        self._view = None
        for change, value in changed_enums:
            self.itemChange(change, value)
            
    def visible(self):
        return self._visible

    def setVisible(self, value, explicitly=None):
        self._setVisibleHelper(value, True, explicitly)

    def _setVisibleHelper(self, visible, update, explicitly):
        if explicitly:
            self._explicitlyHidden = visible 
            
        if not self.parentItem() is None and visible and not self.parentItem().visible():
            return 

        if visible == self.visible():
            return 
        newVisible = self.itemChange(self.GLGraphicsItemChange.ItemVisibleChange, visible)
        if self.visible() == newVisible:
            return
        self._visible = newVisible
        
        for child in self.childItems():
            if not visible or not child._explicitlyHidden:
                child._setVisibleHelper(visible, False, False)
        
        self.update()
        self.itemChange(self.GLGraphicsItemChange.ItemVisibleHasChanged, self.visible())

    def _setTransformHelper(self, tr):
        self.itemChange(self.GLGraphicsItemChange.ItemTransformChange, tr)
        tr = Transform3D(tr)
        if tr != self.transform():
            self._transform = tr
      #      self.itemChange(self.GLGraphicsItemChange.ItemTransformHasChanged, tr)
            self.update()

    def setTransform(self, tr):
        self._setTransformHelper(tr)
        
    def resetTransform(self):
        if self.transform().isIdentity():
            return 
        self._setTransformHelper(Transform3D())

        
    def applyTransform(self, tr, local):
        if local:
            newTransform = self.transform() * tr
        else:
            newTransform = tr * self.transform()
        self._setTransformHelper(newTransform)

    
    @abstractmethod
    def _childPaint(self):...
    
    @abstractmethod
    def _paintHelper(self):... 
    
    def paint(self):
        if not (GL3DGraphicsItemMixin.GLGraphicsItemFlag.ItemHasNoContents & GL3DGraphicsItemMixin.flags(self)): 
            self._paintHelper()
            self._childPaint()

    def update(self):
        if self.updatesBlocked():
            return
        super().update()
        
        
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
            self._parentWidget = parent
            self.itemChange(self.GLGraphicsItemChange.ItemParentWidgetHasChanged, parent) 
    
    def parentWidget(self) -> GL3DViewWidget:
        return self._parentWidget

    def viewChanged(self, view, oldView):
        """Called when this item's view has changed
        (ie, the item has been added to or removed from a ViewBox)"""
        
    def viewRect(self):
        """Return the visible bounds of this item's ViewBox or GraphicsWidget,
        in the local coordinate system of the item."""
        if self._cachedView is not None:
            return self._cachedView

        # Note that in cases of early returns here, the view cache stays empty (None).
        view = self.getViewBox()
        if view is None:
            return None
        bounds = self.mapRectFromView(view.viewRect())
        if bounds is None:
            return None

        bounds = bounds.normalized()
        
        self._cachedView = bounds
        
        ## nah.
        #for p in self.getBoundingParents():
            #bounds &= self.mapRectFromScene(p.sceneBoundingRect())

        return bounds
        
    def _replaceView(self, oldView, item=None):
        if item is None:
            item = self
        for child in item.childItems():
            if hasattr(child, "getViewBox"):
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
        self._cachedView = None
        
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

    def getViewBox(self) -> 'GL3DViewBox':
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

    def itemTransform(self, other: 'GL3DGraphicsItemMixin', ok=None):
        if other is None:
            print("Warning: itemTransform called with null pointer")
            if not ok is None:
                ok = False
            return Transform3D()

        # Case 2: Same item
        if other == self:
            if not ok is None:
                ok = True
            return Transform3D()

        parent = self.parentItem()
        other_parent = other.parentItem()

        if parent == other:
            x = Transform3D()
            self._combine_transform_to_parent(x)
            if not ok is None:
                ok = True
            return x

        if other_parent == self:
            x = Transform3D()
            other._combine_transform_to_parent(x)
            invertible, inverted = x.inverted()
            if not ok is None:
                ok = invertible
            return inverted if invertible else Transform3D()

        # Case 5: Siblings (same parent)
        if not parent is None and parent == other_parent:
            # Fast path for simple translation
            if not self.transform().isIdentity() and not other.transform().isIdentity():
                x1 = Transform3D()
                self._combine_transform_to_parent(x1)
                
                x2 = Transform3D()
                other._combine_transform_to_parent(x2)
                
                invertible, inverted = x2.inverted()
                if not ok is None:
                    ok = invertible
                return x1 * inverted if invertible else Transform3D()
            else:
                delta = self.pos() - other.pos()
                if not ok is None:
                    ok = True
                return Transform3D.fromTranslate(delta.x(), delta.y())

        # Find closest common ancestor
        common_ancestor = self._find_common_ancestor(other)
        
        # Case 6: No common ancestor
        if common_ancestor is None:
            self.ensureSceneTransform()
            other.ensureSceneTransform()
            invertible, inverted = other.sceneTransform().inverted()
            if not ok is None:
                ok = invertible
            return self.sceneTransform() * inverted if invertible else Transform3D()

        # Case 7: Cousins (common ancestor but not direct)
        if other != common_ancestor and self != common_ancestor:
            # Transform both to common ancestor
            good = False
            this_to_common = self.itemTransform(common_ancestor, good)
            other_to_common = Transform3D()
            if good:
                other_to_common = other.itemTransform(common_ancestor, good)
            
            if not good:
                if ok is not None:
                    ok = False
                return Transform3D()
                
            invertible, inverted = other_to_common.inverted()
            if not invertible:
                if ok is not None:
                    ok = False
                return Transform3D()
                
            if ok is not None:
                ok = True
            return this_to_common * inverted

        # Case 8: Ancestor relationship
        parent_of_other = self.isAncestorOf(other)
        child = other if parent_of_other else self
        root = self if parent_of_other else other

        x = Transform3D()
        p = child
        while p is not None and p != root:
            p._combine_transform_to_parent(x)
            p = p.parentItem()

        if parent_of_other:
            invertible, inverted = x.inverted()
            if ok is not None:
                ok = invertible
            return inverted if invertible else Transform3D()
        
        if ok is not None:
            ok = True
        return x

    def _combine_transform_to_parent(self, x):
        """Helper to combine item's transform with parent transform"""
        # Apply item's transform
        t = self.transform()
        if not t.isIdentity():
            # Pre-multiply: x = t * x
            # Create a new transform since Transform3D doesn't support in-place multiplication
            x = t * x
            # Copy matrix elements to original x

        # Apply position translation
        #pos = self.pos
        #x.translate(pos.x(), pos.y())
      #  pos = 
     #   x.translate(self.pos[:,0], )

    def _find_common_ancestor(self, other):
        """Find closest common ancestor item"""
        # Collect all ancestors of this item
        ancestors = set()
        p = self
        while p is not None:
            ancestors.add(p)
            p = p.parentItem()
        
        # Find first common ancestor in other's hierarchy
        p = other
        while p is not None:
            if p in ancestors:
                return p
            p = p.parentItem()
        
        return None

    def ensureSceneTransform(self):
        """Ensure scene transform is up-to-date (dummy implementation)"""
        # In a real implementation, this would ensure the scene transform is cached
        pass

    # Required QGraphicsItem methods (simplified for example)
    def boundingRect(self):
        return self.childrenBoundingRect()

