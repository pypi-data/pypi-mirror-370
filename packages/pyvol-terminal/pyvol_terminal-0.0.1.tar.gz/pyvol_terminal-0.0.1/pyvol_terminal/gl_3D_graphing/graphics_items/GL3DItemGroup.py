from pyqtgraph.Qt import QtCore
from pyqtgraph.opengl.GLGraphicsItem import GLGraphicsItem
from pyqtgraph.Qt import QtCore, QtGui
from PySide6 import QtWidgets
from pyqtgraph.Qt import QT_LIB
import weakref
from pyqtgraph import opengl
import numpy as np
import warnings
#from .AbstractGLGraphicsItem import AbstractGLGraphicsItem, ABCGraphicsItemMeta

from .GL3DGraphicsItemMixin import GL3DGraphicsItemMixin

def get_item_data(item):
    if isinstance(item, opengl.GLScatterPlotItem):
        return item.pos
    elif isinstance(item, opengl.GLMeshItem):
        return item.opts['meshdata'].vertexes()
    elif isinstance(item, opengl.GLLinePlotItem):
        return item.pos
    elif isinstance(item, opengl.GLBarGraphItem):
        return item.points()
    return None



def compute_scene_bbox(items):
    min_vals, max_vals = None, None
    
    for item in items:
        data = get_item_data(item)
        if data is None or len(data) == 0:
            continue
            
        if not isinstance(data, np.ndarray):
            data = np.array(data)
            
        if data.ndim == 1:
            data = data[np.newaxis, :]
        if data.shape[1] == 2:
            data = np.hstack([data, np.zeros((len(data), 1))])
            
        item_min = np.nanmin(data, axis=0)
        item_max = np.nanmax(data, axis=0)
        
        if min_vals is None:
            min_vals, max_vals = item_min, item_max
        else:
            min_vals = np.minimum(min_vals, item_min)
            max_vals = np.maximum(max_vals, item_max)
    
    if min_vals is None:
        return np.array([0, 0, 0]), np.array([1, 1, 1])
    
    return min_vals, max_vals

class WeakList(object):

    def __init__(self):
        self._items = []

    def append(self, obj):
        #Add backwards to iterate backwards (to make iterating more efficient on removal).
        self._items.insert(0, weakref.ref(obj))

    def __iter__(self):
        i = len(self._items)-1
        while i >= 0:
            ref = self._items[i]
            d = ref()
            if d is None:
                del self._items[i]
            else:
                yield d
            i -= 1

#class GLItemGroup(AbstractGLGraphicsItem, QtWidgets.QGraphicsObject):

class GL3DItemGroup(GL3DGraphicsItemMixin):
    def __init__(self, parentItem=None):
        super().__init__(parentItem=parentItem)
        self.viewRange = [[0, 1] for _ in range(3)]
        self.itemsChangedListeners = WeakList()
        
        self.setFlag(GL3DGraphicsItemMixin.GLGraphicsItemFlag.ItemHasNoContents)
        self.setFlag(GL3DGraphicsItemMixin.GLGraphicsItemFlag.ItemSendsGeometryChanges)

    def itemChange(self, change, value):
        ret = super().itemChange(change, value)
        if change in [
            self.GLGraphicsItemChange.ItemChildAddedChange,
            self.GLGraphicsItemChange.ItemChildRemovedChange,
        ]:
            try:
                itemsChangedListeners = self.itemsChangedListeners
            except AttributeError:
                # It's possible that the attribute was already collected when the itemChange happened
                # (if it was triggered during the gc of the object).
                pass
            else:
                for listener in itemsChangedListeners:
                    listener.itemsChanged()

            try:
                inform_view_on_change = self.__inform_view_on_changes
            except AttributeError:
                # It's possible that the attribute was already collected when the itemChange happened
                # (if it was triggered during the gc of the object).
                pass
            else:
                if inform_view_on_change and change in [self.GLGraphicsItemChange.ItemPositionHasChanged, self.GLGraphicsItemChange.ItemTransformHasChanged]:
                    self.informViewBoundsChanged()
        return ret
        
    #def childItems(self):
    #    return list(self._GLGraphicsItem__children)

    def boundingRect(self):
        return QtCore.QRectF()
            
    def addItem(self, item):
        item.setParentItem(self)
        
    def _childPaint(self):...
    
    def _paintHelper(self):... 