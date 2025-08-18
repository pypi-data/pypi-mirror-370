from pyqtgraph.Qt import QtCore
from pyqtgraph.opengl.GLGraphicsItem import GLGraphicsItem
from pyqtgraph.Qt import QtCore, QtGui
from PySide6 import QtWidgets
from pyqtgraph.Qt import QT_LIB
import weakref
from pyqtgraph import opengl
import numpy as np
import warnings
from pyqtgraph.Qt import isQObjectAlive
from pyvol_terminal.gl_3D_graphing import meta
import abc

        

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

class AbstractGLGraphicsItem(GLGraphicsItem, metaclass=meta.QABCMeta):
    
    def __init__(self, parentItem=None, **kwargs):
        self._blockUpdate: bool
        self.blockUpdate(False)
        self._viewBox=None
        self._viewWidget=None
        super().__init__()

        self._GLGraphicsItem__parent = None 
        self._GLGraphicsItem__children = list() 
        self._GLGraphicsItem__view = None 
        self._cachedView = None
        self.setParentItem(parentItem)

    def blockUpdate(self, flag):
        self._blockUpdate=flag
            
        
    @abc.abstractmethod
    def _internal_update(self):...

    def update(self):
        if not self._blockUpdate:
            self._internal_update()
        
    
    def setParentItem(self, item):
        if self._GLGraphicsItem__parent is not None:
            self._GLGraphicsItem__parent._GLGraphicsItem__children.remove(self)
        if item is not None:
            item._GLGraphicsItem__children.append(self)
            item.itemChange(item.GraphicsItemChange.ItemChildAddedChange, self)

        if self._GLGraphicsItem__view is not None:
            self._GLGraphicsItem__view.removeItem(self)

        self._GLGraphicsItem__parent = item
        self._GLGraphicsItem__view = None
        

    def childItems(self):
        return list(self._GLGraphicsItem__children)


class GLItemGroup(AbstractGLGraphicsItem, QtWidgets.QGraphicsObject):
    def __init__(self, parentItem=None):
        self.__inform_view_on_changes = True
        super().__init__(parentItem=parentItem)
        
        self.viewRange = [[0, 1] for _ in range(3)]
        self._GLGraphicsItem__parent = None 
        self._GLGraphicsItem__children = list() 
        self._GLGraphicsItem__view = None 
        self.itemsChangedListeners = WeakList()
        
        
        self.setFlag(self.GraphicsItemFlag.ItemHasNoContents)
        self.setFlag(self.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setParentItem(parentItem)

    def itemChangeInner(self, change, value):
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
        ret = self.itemChangeInner(change, value)
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
        
    def childItems(self):
        return list(self._GLGraphicsItem__children)

    def boundingRect(self):
        return QtCore.QRectF()
        
    def paint(self, *args):
        pass
    
    def addItem(self, item):
        item.setParentItem(self)
    
    def resetTransform(self):
        return super().resetTransform()

    

    def _internal_update(self):
        return QtWidgets.QGraphicsObject.update()

class AnotherItem(QtWidgets.QGraphicsItem):
    def __init__(self, parentItem=None):
        super().__init__(parent=parentItem)
        
    def _internal_update(self, **kwargs):...    
    
    

"""


class CustomItem(AbstractGLGraphicsItem, QtWidgets.QGraphicsObject):
    def __init__(self, parentItem=None):
        super().__init__(parentItem=parentItem)
        self._GLGraphicsItem__parent = None 
        self._GLGraphicsItem__children = list() 
        self._GLGraphicsItem__view = None 
        self._cachedView = None
        self.item_group = GLItemGroup(parentItem=self)
        self.setParentItem(parent)
    

"""

class CustomItem(QtWidgets.QGraphicsObject):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        
    def _internal_update(self, **kwargs):...    
    

    def boundingRect(self):
        return QtCore.QRectF(-10, -10, 20, 20)  # Or some non-zero rect
    
    def paint(self, *args, **kwargs):...


class QGraphicsWrapper(QtWidgets.QGraphicsItem):
    def __init__(self, parent=None):
        super().__init__(parent=parent)     
        self._GLGraphicsItem__parent = None 
        self._GLGraphicsItem__children = list() 
        self._GLGraphicsItem__view = None 
        self.__depthValue=0

        self.custom_item = GLItemGroup()
        self.custom_item.setParentItem(self) 

    def _setView(self, view):
        self.__view=view
    
    def boundingRect(self):
        return QtCore.QRectF(-10, -10, 20, 20)  # Or some non-zero rect
    
    def paint(self, *args, **kwargs):...
    
    def isInitialized(self):
        return True
    
    def depthValue(self):
        """Return the depth value of this item. See setDepthValue for more information."""
        return self.__depthValue
    
    def visible(self):
        return self.isVisible()

#from pyvol_terminal.gl_3D_graphing.graphics_items.GLViewBox import GLViewBox

class GLViewBox(AbstractGLGraphicsItem, QtWidgets.QGraphicsItem):
    def __init__(self, parentItem=None):
        super().__init__()     
    
    def create_child(self):
        self.childGroup = GLItemGroup(parentItem=self)
        print(f"self.childGroup: {self.childGroup}")
        print(f'isQObjectAlive(self.childGroup): {isQObjectAlive(self.childGroup)}')
        if hasattr(type(self.childGroup), "implements"):
            print(True)
        else:
            print(False)
        
    def _internal_update(self, **kwargs):...    
    

    def boundingRect(self):
        return QtCore.QRectF(-10, -10, 20, 20)  # Or some non-zero rect
    
    def paint(self, *args, **kwargs):...


        


class CustomGLViewWidget(opengl.GLViewWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)     
#        wrapper = QGraphicsWrapper()
        self.vb=GLViewBox()
        self.addItem(self.vb)
        print("after addItem")
        self.vb.create_child()
        print(self.items)
        

class Window(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)     
        
        #self.graphics_item_wrapper = QGraphicsWrapper()
        self.central_widget = CustomGLViewWidget()
        self.setCentralWidget(self.central_widget)
        self.central_layout = QtWidgets.QHBoxLayout(self.centralWidget())
        self.setLayout(self.central_layout)
        
        
        
        
        #self.central_widget.addItem(self.graphics_item_wrapper)



def main():
    app = QtWidgets.QApplication()
    win = Window()
    print(f"win.central_widget.items: {win.central_widget.items}")
    
    items = win.central_widget.items
    for item in items:
        
        print(f"item.childGroup: {item.childGroup}")
        
        parent_item = item.childGroup.parentItem()
        print(f"parent_item: {parent_item}")

        
        if hasattr(parent_item, "implements"):
            print(True)
        else:
            print(False)
        


            

    win.show()



    app.exec()

if __name__ == "__main__":
    main()