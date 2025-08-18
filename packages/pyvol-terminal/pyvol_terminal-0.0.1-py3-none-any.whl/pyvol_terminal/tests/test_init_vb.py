#from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
from PySide6 import QtCore, QtGui, QtWidgets
from pyqtgraph import opengl
from OpenGL import GL
from pyqtgraph import Transform3D
import weakref
import numpy as np
from pyqtgraph.Qt import QtCore
from pyvol_terminal.gl_3D_graphing.graphics_items.GLGraphicsObject import GLGraphicsObject
from pyvol_terminal.gl_3D_graphing.graphics_items.GL3DViewBox import GLChildGroup
from pyvol_terminal.gl_3D_graphing.graphics_items.GL3DItemGroup import GL3DItemGroup
import weakref
from pyqtgraph.opengl import GLGraphicsItem
import weakref
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
import operator
from functools import reduce
from abc import ABCMeta, abstractmethod
import numpy as np
import warnings
from pyqtgraph.Qt import QT_LIB
from pyqtgraph import Transform3D


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


class AbstractGLGraphicsItem(GLGraphicsItem.GLGraphicsItem):
    
    def __init__(self, parentItem=None, **kwargs):
        self._blockUpdate=None
        self._viewBox=None
        print("AbstractGLGraphicsItem")
        print(f"parentItem: {parentItem}")
        
        super().__init__(parentItem=parentItem)

    @property
    def _parent(self):
        """Access to __parent"""
        return self._GLGraphicsItem__parent
    
    @_parent.setter
    def _parent(self, value):
        """Set __parent"""
        self._GLGraphicsItem__parent = value
    
    @property
    def _view(self):
        """Access to __view"""
        return self._GLGraphicsItem__view
    
    @_view.setter
    def _view(self, value):
        """Set __view"""
        self._GLGraphicsItem__view = value
    
    @property
    def _children(self):
        """Access to __children"""
        return self._GLGraphicsItem__children
    
    @property
    def _transform(self):
        """Access to __transform"""
        return self._GLGraphicsItem__transform
    
    @_transform.setter
    def _transform(self, value):
        """Set __transform"""
        self._GLGraphicsItem__transform = value
    
    @property
    def _visible(self):
        """Access to __visible"""
        return self._GLGraphicsItem__visible
    
    @_visible.setter
    def _visible(self, value):
        """Set __visible"""
        self._GLGraphicsItem__visible = value
    
    @property
    def _initialized(self):
        """Access to __initialized"""
        return self._GLGraphicsItem__initialized
    
    @_initialized.setter
    def _initialized(self, value):
        """Set __initialized"""
        self._GLGraphicsItem__initialized = value
    
    @property
    def _glOpts(self):
        """Access to __glOpts"""
        return self._GLGraphicsItem__glOpts
    
    @_glOpts.setter
    def _glOpts(self, value):
        """Set __glOpts"""
        self._GLGraphicsItem__glOpts = value
    
    @property
    def _depthValue(self):
        """Access to __depthValue"""
        return self._GLGraphicsItem__depthValue
    
    @_depthValue.setter
    def _depthValue(self, value):
        """Set __depthValue"""
        self._GLGraphicsItem__depthValue = value
    
class GLGraphicsObject(AbstractGLGraphicsItem, QtWidgets.QGraphicsObject): 
    _qtBaseClass = QtWidgets.QGraphicsObject
    def __init__(self, parentItem=None):
        self.__inform_view_on_changes = True
        QtWidgets.QGraphicsObject.__init__(self)
        
        self.setFlag(self.GraphicsItemFlag.ItemSendsGeometryChanges)

        
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
                print("itemchange")
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

    def parentItem(self):
        return self.__parent
    
class GL3DItemGroup(GLGraphicsObject):
    """
    Replacement for QGraphicsItemGroup
    """
    
    def __init__(self, *args):
        GLGraphicsObject.__init__(self, *args)
        self.setFlag(self.GraphicsItemFlag.ItemHasNoContents)
    
    def boundingRect(self):
        return QtCore.QRectF()
        
    def paint(self, *args):
        pass
    
    def addItem(self, item):
        item.setParentItem(self)


class GLChildGroup(GL3DItemGroup):

    def __init__(self, parentItem):
        GL3DItemGroup.__init__(self, parentItem)

        # Used as callback to inform ViewBox when items are added/removed from
        # the group.
        # Note 1: We would prefer to override itemChange directly on the
        #         ViewBox, but this causes crashes on PySide.
        # Note 2: We might also like to use a signal rather than this callback
        #         mechanism, but this causes a different PySide crash.
        self.itemsChangedListeners = WeakList()

        # exempt from telling view when transform changes
        self._GraphicsObject__inform_view_on_change = False

    def itemChange(self, change, value):
        ret = GL3DItemGroup.itemChange(self, change, value)
        if change in [
            self.GraphicsItemChange.ItemChildAddedChange,
            self.GraphicsItemChange.ItemChildRemovedChange,
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
        return ret
    
    def linkViewBox(self, vb):
        print
        self._viewBox=vb
        if self.parentItem() != vb:
            self.setParentItem(vb)
        self.update()


class CustomItem(AbstractGLGraphicsItem, QtWidgets.QGraphicsItem):
    def __init__(self):
        QtWidgets.QGraphicsItem.__init__(self, None)
        
def main():
    
    app = QtWidgets.QApplication()
    win = QtWidgets.QMainWindow()
    item1 = CustomItem()
    item2 = CustomItem()
    item1.setParentItem
    #child_group = GLChildGroup(parentItem=item)
    #child_group.setParentItem()
 #   print(gitem.parentItem())
    win.show()
    app.exec()

if __name__ == "__main__":
    main()
