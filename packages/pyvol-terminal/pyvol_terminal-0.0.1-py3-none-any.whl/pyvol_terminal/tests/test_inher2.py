from __future__ import annotations 
from typing import List, Optional, Tuple, Union, Dict, TYPE_CHECKING, Callable
if TYPE_CHECKING:
    from .GLViewBox import GLViewBox 

#from pyqtgraph.opengl import GLGraphicsItem
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
import warnings
from pyqtgraph.Qt import QT_LIB
from .GLGraphicsItem import GLGraphicsItem
from PySide6.QtWidgets import QGraphicsItem


class EnumContainer:
    NoCache = QGraphicsItem.CacheMode.NoCache
    ItemCoordinateCache = QGraphicsItem.CacheMode.ItemCoordinateCache
    DeviceCoordinateCache = QGraphicsItem.CacheMode.DeviceCoordinateCache
    
    ItemEnabledChange = QGraphicsItem.GraphicsItemChange.ItemEnabledChange
    ItemEnabledHasChanged = QGraphicsItem.GraphicsItemChange.ItemEnabledHasChanged
    ItemPositionChange = QGraphicsItem.GraphicsItemChange.ItemPositionChange
    ItemPositionHasChanged = QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged
    ItemTransformChange = QGraphicsItem.GraphicsItemChange.ItemTransformChange
    ItemTransformHasChanged = QGraphicsItem.GraphicsItemChange.ItemTransformHasChanged
    ItemRotationChange = QGraphicsItem.GraphicsItemChange.ItemRotationChange
    ItemRotationHasChanged = QGraphicsItem.GraphicsItemChange.ItemRotationHasChanged
    ItemScaleChange = QGraphicsItem.GraphicsItemChange.ItemScaleChange
    ItemScaleHasChanged = QGraphicsItem.GraphicsItemChange.ItemScaleHasChanged
    ItemTransformOriginPointChange = QGraphicsItem.GraphicsItemChange.ItemTransformOriginPointChange
    ItemTransformOriginPointHasChanged = QGraphicsItem.GraphicsItemChange.ItemTransformOriginPointHasChanged
    ItemSelectedChange = QGraphicsItem.GraphicsItemChange.ItemSelectedChange
    ItemSelectedHasChanged = QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged
    ItemVisibleChange = QGraphicsItem.GraphicsItemChange.ItemVisibleChange
    ItemVisibleHasChanged = QGraphicsItem.GraphicsItemChange.ItemVisibleHasChanged
    ItemParentChange = QGraphicsItem.GraphicsItemChange.ItemParentChange
    ItemParentHasChanged = QGraphicsItem.GraphicsItemChange.ItemParentHasChanged
    ItemChildAddedChange = QGraphicsItem.GraphicsItemChange.ItemChildAddedChange
    ItemChildRemovedChange = QGraphicsItem.GraphicsItemChange.ItemChildRemovedChange
    ItemSceneChange = QGraphicsItem.GraphicsItemChange.ItemSceneChange
    ItemSceneHasChanged = QGraphicsItem.GraphicsItemChange.ItemSceneHasChanged
    ItemCursorChange = QGraphicsItem.GraphicsItemChange.ItemCursorChange
    ItemCursorHasChanged = QGraphicsItem.GraphicsItemChange.ItemCursorHasChanged
    ItemToolTipChange = QGraphicsItem.GraphicsItemChange.ItemToolTipChange
    ItemToolTipHasChanged = QGraphicsItem.GraphicsItemChange.ItemToolTipHasChanged
    ItemFlagsChange = QGraphicsItem.GraphicsItemChange.ItemFlagsChange
    ItemFlagsHaveChanged = QGraphicsItem.GraphicsItemChange.ItemFlagsHaveChanged
    ItemZValueChange = QGraphicsItem.GraphicsItemChange.ItemZValueChange
    ItemZValueHasChanged = QGraphicsItem.GraphicsItemChange.ItemZValueHasChanged
    ItemOpacityChange = QGraphicsItem.GraphicsItemChange.ItemOpacityChange
    ItemOpacityHasChanged = QGraphicsItem.GraphicsItemChange.ItemOpacityHasChanged
    ItemScenePositionHasChanged = QGraphicsItem.GraphicsItemChange.ItemScenePositionHasChanged

    ItemIsMovable = QGraphicsItem.GraphicsItemFlag.ItemIsMovable.value
    ItemIsSelectable = QGraphicsItem.GraphicsItemFlag.ItemIsSelectable.value
    ItemIsFocusable = QGraphicsItem.GraphicsItemFlag.ItemIsFocusable.value
    ItemClipsToShape = QGraphicsItem.GraphicsItemFlag.ItemClipsToShape.value
    ItemClipsChildrenToShape = QGraphicsItem.GraphicsItemFlag.ItemClipsChildrenToShape.value
    ItemIgnoresTransformations = QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations.value
    ItemIgnoresParentOpacity = QGraphicsItem.GraphicsItemFlag.ItemIgnoresParentOpacity.value
    ItemDoesntPropagateOpacityToChildren = QGraphicsItem.GraphicsItemFlag.ItemDoesntPropagateOpacityToChildren.value
    ItemStacksBehindParent = QGraphicsItem.GraphicsItemFlag.ItemStacksBehindParent.value
    ItemUsesExtendedStyleOption = QGraphicsItem.GraphicsItemFlag.ItemUsesExtendedStyleOption.value
    ItemHasNoContents = QGraphicsItem.GraphicsItemFlag.ItemHasNoContents.value
    ItemSendsGeometryChanges = QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges.value
    ItemAcceptsInputMethod = QGraphicsItem.GraphicsItemFlag.ItemAcceptsInputMethod.value
    ItemNegativeZStacksBehindParent = QGraphicsItem.GraphicsItemFlag.ItemNegativeZStacksBehindParent.value
    ItemIsPanel = QGraphicsItem.GraphicsItemFlag.ItemIsPanel.value
    ItemSendsScenePositionChanges = QGraphicsItem.GraphicsItemFlag.ItemSendsScenePositionChanges.value
    ItemContainsChildrenInShape = QGraphicsItem.GraphicsItemFlag.ItemContainsChildrenInShape.value


class _BaseAbstractGraphicsItem(QtCore.QObject, EnumContainer, GLGraphicsItem):
    itemChanged = QtCore.Signal(QGraphicsItem.GraphicsItemChange, object)
    def __init__(self, parentItem=None):
        super().__init__(parentItem)
        self.__inform_view_on_changes=True
        self._cache_mode = self.NoCache
        self._flags = 0
        self._position = (0, 0)
        self._visible = True
        self._enabled = True
        self._selected = False
        self._transform = None
        self._rotation = 0.0
        self._scale = 1.0
        self._transform_origin = (0, 0)
        self._z_value = 0.0
        self._opacity = 1.0
        
        

    
    def itemChange(self, change, value):
        ret = super().itemChange(change, value)

        if change in [self.GraphicsItemChange.ItemParentHasChanged, self.GraphicsItemChange.ItemSceneHasChanged]:
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
        try:
            inform_view_on_change = self.__inform_view_on_changes
        except AttributeError:
            # It's possible that the attribute was already collected when the itemChange happened
            # (if it was triggered during the gc of the object).
            pass
        else:
            if inform_view_on_change and change in [self.GraphicsItemChange.ItemPositionHasChanged, self.GraphicsItemChange.ItemTransformHasChanged]:
                self.informViewBoundsChanged()
            
        return ret

        
    def itemChange(self, change, value):

        self.itemChanged.emit(change, value)
        return value
    
    # Cache mode property
    @property
    def cacheMode(self):
        return self._cache_mode
    
    @cacheMode.setter
    def cacheMode(self, value):
        if self._cache_mode != value:
            self._cache_mode = value
    
    @property
    def flags(self):
        return self._flags
    
    @flags.setter
    def flags(self, value):
        if self._flags != value:
            new_value = self.itemChange(self.ItemFlagsChange, value)
            self._flags = new_value
            self.itemChange(self.ItemFlagsHaveChanged, new_value)
    
    # Position property
    @property
    def position(self):
        return self._position
    
    @position.setter
    def position(self, value):
        if self._position != value:
            new_value = self.itemChange(self.ItemPositionChange, value)
            self._position = new_value
            self.itemChange(self.ItemPositionHasChanged, new_value)
    
    # Visibility property
    @property
    def visible(self):
        return self._visible
    
    @visible.setter
    def visible(self, value):
        if self._visible != value:
            new_value = self.itemChange(self.ItemVisibleChange, value)
            self._visible = new_value
            self.itemChange(self.ItemVisibleHasChanged, new_value)
    
    # Enabled property
    @property
    def enabled(self):
        return self._enabled
    
    @enabled.setter
    def enabled(self, value):
        if self._enabled != value:
            new_value = self.itemChange(self.ItemEnabledChange, value)
            self._enabled = new_value
            self.itemChange(self.ItemEnabledHasChanged, new_value)
    
    # Selected property
    @property
    def selected(self):
        return self._selected
    
    @selected.setter
    def selected(self, value):
        if self._selected != value:
            new_value = self.itemChange(self.ItemSelectedChange, value)
            self._selected = new_value
            self.itemChange(self.ItemSelectedHasChanged, new_value)
    
    # Transform property
    @property
    def transform(self):
        return self._transform
    
    @transform.setter
    def transform(self, value):
        if self._transform != value:
            new_value = self.itemChange(self.ItemTransformChange, value)
            self._transform = new_value
            self.itemChange(self.ItemTransformHasChanged, new_value)
    
    # Rotation property
    @property
    def rotation(self):
        return self._rotation
    
    @rotation.setter
    def rotation(self, value):
        if self._rotation != value:
            new_value = self.itemChange(self.ItemRotationChange, value)
            self._rotation = new_value
            self.itemChange(self.ItemRotationHasChanged, new_value)
    
    # Scale property
    @property
    def scale(self):
        return self._scale
    
    @scale.setter
    def scale(self, value):
        if self._scale != value:
            new_value = self.itemChange(self.ItemScaleChange, value)
            self._scale = new_value
            self.itemChange(self.ItemScaleHasChanged, new_value)
    
    # Transform origin point property
    @property
    def transformOriginPoint(self):
        return self._transform_origin
    
    @transformOriginPoint.setter
    def transformOriginPoint(self, value):
        if self._transform_origin != value:
            new_value = self.itemChange(self.ItemTransformOriginPointChange, value)
            self._transform_origin = new_value
            self.itemChange(self.ItemTransformOriginPointHasChanged, new_value)
    
    # Z-value property
    @property
    def zValue(self):
        return self._z_value
    
    @zValue.setter
    def zValue(self, value):
        if self._z_value != value:
            new_value = self.itemChange(self.ItemZValueChange, value)
            self._z_value = new_value
            self.itemChange(self.ItemZValueHasChanged, new_value)
    
    # Opacity property
    @property
    def opacity(self):
        return self._opacity
    
    @opacity.setter
    def opacity(self, value):
        if self._opacity != value:
            new_value = self.itemChange(self.ItemOpacityChange, value)
            self._opacity = new_value
            self.itemChange(self.ItemOpacityHasChanged, new_value)
    
    def setCacheMode(self, mode, logical_cache_size=None, device_cache_size=None):
        """
        Set the cache mode for this item.
        Optionally provide cache sizes for ItemCoordinateCache or DeviceCoordinateCache modes.
        """
        self._cache_mode = mode
        # Here you would typically store the cache sizes if needed
        self._logical_cache_size = logical_cache_size
        self._device_cache_size = device_cache_size
    
    def setFlag(self, flag, enabled=True):
        """Set or clear a flag for this item."""
        flag_int = flag.value if hasattr(flag, 'value') else flag
        if enabled:
            new_flags = self._flags | flag_int
        else:
            new_flags = self._flags & ~flag_int
        
        if self._flags != new_flags:
            self.flags = new_flags
    
    def setParent(self, parent):
        """
        Override setParent to handle parent change notifications
        """
        old_parent = self.parent()
        super().setParent(parent)
        if old_parent != parent:
            self.itemChange(self.ItemParentChange, parent)
            self.itemChange(self.ItemParentHasChanged, parent)
            
    def itemChange(self, change, value):
        """
        Handle item changes. Can be overridden in subclasses for custom behavior.
        Returns the new value after processing.
        """
        self.itemChanged.emit(change, value)
        return value

