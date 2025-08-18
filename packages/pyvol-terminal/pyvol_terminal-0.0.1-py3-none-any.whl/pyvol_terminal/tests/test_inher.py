#%%%
from functools import wraps

class GrandMother:
    wrapped_methods = "paint"
    def __init__(self, *args,):
        super().__init__()
        self._old_paint=None

    def __init_subclass__(cls, **kwargs):        
        super().__init_subclass__(**kwargs)


        for method_name in cls.__dict__:
            if method_name in cls.wrapped_methods:
                method = cls.__dict__[method_name].__name__
                print(f"method: {method}")
                @wraps(method)
                def wrapped(self, *args, **kwargs):
                    helper_method = getattr(GrandMother, f"_{method}Helper")
                    return helper_method(self, *args, **kwargs)
                
                setattr(cls, method_name, wrapped)
        
        
    def paint(self):
        print("grandmother")
        
    def _paintHelper(self):
        print(f"__paintHelper")
        print(self.__class__.paint())
        

class Parent3(GrandMother):
    def __init__(self):
        super().__init__()
    def paint(self):
        print("parent")

class Child(Parent3):
    def __init__(self):
        super().__init__()

    def paint(self):
        print("child")

a = Child()
a.paint()

#%%%

class grandParent:
    def __init__(self):
        print("gp before")
        super().__init__()


class Parent1(grandParent):
    def __init__(self):
        print("p1 before")
        super().__init__()
        #print("p1 after")
        
    def func(self):
        print("Parent1")



class Parent2:
    def __init__(self):
        print("p2 before")
        super().__init__()
        #print("p2 after")
    
    def func(self):
        print("Parent2")
        
        
class Child1(Parent1, Parent2): 
    def __init__(self):
        super().__init__()
        
Child1()
    
#%%
"""
class D:
    def __init__(self):
        print("D")
        super().__init__()

class B(D):
    def __init__(self):
        print("B")
        super().__init__()

class C:
    def __init__(self):
        print("C")
        super().__init__()

class A(B, C):  
    def __init__(self):
        print("A")
        super().__init__()

A()
#%%

from PySide6 import QtCore, QtWidgets, QtGui
import warnings
import abc
from PySide6.QtCore import QObject
from pyqtgraph import Transform3D
from pyvol_terminal.gl_3D_graphing.graphics_items import CustomGLGraphicsItem
from pyvol_terminal.gl_3D_graphing.graphics_items import GLGraphicsObject

class GLGroupItem(CustomGLGraphicsItem.CustomGLGraphicsItem):
    def __init__(self, parentItem=None):
        super().__init__(parentItem=parentItem)


a=GLGraphicsObject.GLGraphicsObject()
#a.rect()
print(a)
import sys
sys.exit()
"""

"""
from pyvol_terminal.gl_3D_graphing.graphics_items import GLGraphicsObject

class MyClass(GLGraphicsObject.GLGraphicsObject):
    def __init__(self, *args,):
        super().__init__()

MyClass()
from pyvol_terminal.gl_3D_graphing.graphics_items import AbstractGLPlotItem
from abc import ABCMeta
import abc
from PySide6 import QtCore, QtWidgets, QtGui

from pyqtgraph.opengl import GLGraphicsItem

class QABCMeta(ABCMeta, type(QtCore.QObject)):
    
    def __new__(mcls, name, bases, ns, **kw):
        cls = super().__new__(mcls, name, bases, ns, **kw)
        abc._abc_init(cls)
        return cls
    def __call__(cls, *args, **kw):
        if cls.__abstractmethods__:
            raise TypeError(f"Can't instantiate abstract class {cls.__name__} without an implementation for abstract methods {set(cls.__abstractmethods__)}")
        return super().__call__(*args, **kw)




class GraphicsItemMeta(ABCMeta, type(QtCore.QObject)):
    pass

class AbstractGLGraphicsItem(QtWidgets.QGraphicsItem, GLGraphicsItem.GLGraphicsItem, metaclass=QABCMeta):
    @abc.abstractmethod
    def func(self):
        pass

class MetaGLGraphics(type(QtCore.QObject), ABCMeta):
    pass

class GLGraphicsObject(QtWidgets.QGraphicsObject, AbstractGLGraphicsItem, metaclass=QABCMeta): 
    _qtBaseClass = QtWidgets.QGraphicsObject

GLGraphicsObject



import pyqtgraph 

unique_attr = set(dir(pyqtgraph.ViewBox)) - set(dir(pyqtgraph.GraphicsWidget))
class CustomViewBox(pyqtgraph.ViewBox):
    
    unique_attr = unique_attr
    
    def __getattr__(self, name):
        
        if not name in CustomViewBox.unique_attr:
            raise AttributeError(
                f"'{type(self).__name__}' object blocks access to inherited "
                f"GraphicsWidget attribute '{name}'"
            )
        
        # Fallback to normal attribute resolution
        return super().__getattr__(name)

from PySide6 import QtWidgets 
app = QtWidgets.QApplication()

vb = CustomViewBox()
vb.setSizePolicy  # Raises AttributeError if only in GraphicsWidget
import sys 
sys.exit()


#%%%

import abc
from PySide6.QtCore import QObject
from pyqtgraph.Qt import QT_LIB, QtCore, QtWidgets
from pyqtgraph.opengl import GLGraphicsItem


class QABCMeta(abc.ABCMeta, type(QObject)):
    

    def __new__(mcls, name, bases, ns, **kw):
        print(f"name: {name}")
        print(f"bases: {bases}")
        print(f'ns: {ns}')
        res = super.__new__.__qualname__
        print(f"res: {res}")


        cls = super().__new__(mcls, name, bases, ns, **kw)
        abc._abc_init(cls)
        return cls
    def __call__(cls, *args, **kw):
        if cls.__abstractmethods__:
            raise TypeError(f"Can't instantiate abstract class {cls.__name__} without an implementation for abstract methods {set(cls.__abstractmethods__)}")
        return super().__call__(*args, **kw)

class AbstractGLGraphicsItem(QtWidgets.QGraphicsItem, GLGraphicsItem.GLGraphicsItem, metaclass=QABCMeta):
    pass
class GLGraphicsObject(QtWidgets.QGraphicsObject, AbstractGLGraphicsItem):
    pass



#%%


class GrandParent1:
    def __init__(self, kwarg1=None):
        self.kwarg1 = kwarg1
        print(kwarg1)
        print("GrandParent1")
        super().__init__(kwarg1=kwarg1)
     

class GrandParent2:
    def __init__(self, kwarg1=None):
        self.kwarg1 = kwarg1
        print(kwarg1)
        print("GrandParent2")
        super().__init__()


class Parent1(GrandParent1, GrandParent2):
    def __init__(self, kwarg1=None):
        self.kwarg1 = kwarg1
        print("Parent1")
        #super().__init__()
        super().__init__(kwarg1=kwarg1)

class Parent2(GrandParent1):
    def __init__(self, kwarg1=None):
        self.kwarg1 = kwarg1
        print("Parent2")
        #super().__init__()
        super().__init__(kwarg1=kwarg1)

class Child1(Parent1, GrandParent1):
    def __init__(self, kwarg1=None):
        self.kwarg1 = kwarg1
        print("Child1")
        super().__init__(kwarg1=kwarg1)
        #super().__init__(kwarg1=kwarg1)
        


child = Child1(kwarg1=10)



#%%
from PySide6 import QtCore, QtGui, QtWidgets

from pyvol_terminal.gl_3D_graphing import meta
from pyqtgraph.opengl import GLGraphicsItem


class AbstractGLGraphicsItem(QtWidgets.QGraphicsItem, GLGraphicsItem.GLGraphicsItem, metaclass=meta.QABCMeta):
    
    def __init__(self, parent=None, **kwargs):
        print("\nGraphicsItem")
        print(f"\n{self}\n")
        QtWidgets.QGraphicsItem.__init__(self)

        self._viewBox=None
        self._blockUpdate=None
        
class GLGraphicsObject(QtWidgets.QGraphicsObject, AbstractGLGraphicsItem): 
    _qtBaseClass = QtWidgets.QGraphicsObject
    def __init__(self, parent=None):
        print(f"\nGraphicsObject")
        self.__inform_view_on_changes = True
        QtWidgets.QGraphicsObject.__init__(self, parent=parent)

class AbstractGLPlotItem(GLGraphicsObject, metaclass=meta.QABCMeta):
    sigPlotChanged = QtCore.Signal()
    
    def __init__(self, *args, view_box=None, **kwargs):
        self._viewBox=view_box        
        print("PlotItem")
        GLGraphicsObject.__init__(self, **kwargs)
        self.extra_opts={
                   "clipToView" : False
                   }
        self._boundsCache=[None]*3
        
        self.setProperty('xViewRangeWasChanged', False)
        self.setProperty('yViewRangeWasChanged', False)
        self.setProperty('zViewRangeWasChanged', False)
        self.setProperty('styleWasChanged', True)  # force initial update

plot_item = AbstractGLPlotItem()
"""

#%%%

from PySide6 import QtCore, QtGui, QtWidgets
from pyqtgraph.opengl.GLGraphicsItem import GLGraphicsItem
from PySide6.QtWidgets import QGraphicsItem
import warnings
from pyqtgraph.Qt import QT_LIB
from pyvol_terminal.gl_3D_graphing.graphics_items.AbstractGLGraphicsItem import AbstractGLGraphicsItem

from pyqtgraph.opengl import GLGraphicsItem
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets, isQObjectAlive
from pyvol_terminal.gl_3D_graphing import meta

class AbstractGLGraphicsItem(GLGraphicsItem.GLGraphicsItem, QtWidgets.QGraphicsItem, metaclass=meta.QABCMeta):

    def __init__(self, parentItem=None, **kwargs):
        self._blockUpdate: bool
        self._viewBox = None
        self._viewWidget = None
        super().__init__()

        self._GLGraphicsItem__parent = None 
        self._GLGraphicsItem__children = list() 
        self._GLGraphicsItem__view = None 
        self._cachedView = None
        self.setParentItem(parentItem)


    @property
    def parent(self):
        """Getter for parent property"""
        return self._GLGraphicsItem__parent

    @parent.setter
    def parent(self, item):
        """Setter for parent property with all the logic"""
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


class CustomAbstractGLGraphicsItem(AbstractGLGraphicsItem):
    def __init__(self, parent=None):
        self.__inform_view_on_changes=True
        
        super().__init__()

    def boundingRect(self, *args, **kwargs):
        return

    def itemChange(self, change, value):
        ret = QtWidgets.QGraphicsItem.itemChange(self, change, value)
        print(f"\nPlotItem itemChange")
        print(f"change: {change}")
        print(f"value: {value}")
        if change in [self.GraphicsItemChange.ItemParentHasChanged, self.GraphicsItemChange.ItemSceneHasChanged]:
            print(True)
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

    
    def _internal_update(self, *args, **kwargs):...

graphics_itepaint = CustomAbstractGLGraphicsItem()
graphics_item2 = CustomAbstractGLGraphicsItem()

graphics_itepaint.setParentItem(graphics_item2)
import sys
sys.exit()


#%%


from abc import ABCMeta, ABC, abstractmethod

class GrandParent1(ABC):
    def __init__(self):
        super().__init__()

    def __init_subclass__(cls):
        print(cls)
    
    def paint(self):
        print("g")
        
    @abstractmethod
    def paintChild(self):...


class Parent1(GrandParent1):
    def __init__(self):
        super().__init__()
        
    def paint(self):
        super().paint()
        print("p")
        
class Parent2:
    def __init__(self):
        super().__init__()
        
    def paint(self):
        
        print("p")
        
    def abs(self):
        print("p abs")


class Child(Parent1, Parent2):
    pass
    def paintChild(self):
        print("c")


class ChildChild(Child):
    pass

    def paintChild(self):
        print("c")


c = Child()
c.paintChild()

#%%

class GrandParent1:
    def __init__(self, **kwargs):
        print("init GP1")
        #self.__x=None
        super().__init__(**kwargs)
        
    def paint(self):
        print(f"GBase1 paint")
        result = self.paintGL()
        return result

class GrandParent2:
    def __init__(self):
        print("init GP2")
        super().__init__()

class Parent1(GrandParent1):
    def __init__(self, **kwargs):
        print("init p1")
        self.__x=None
        super().__init__(**kwargs)

class Parent2(GrandParent2):
    def __init__(self, x):
        print("init p2")
        super().__init__()
        self.setData(x)
        
    def setData(self, x):
        print(f"Parent2 setData")
        self.__x=x



class Child(Parent1, Parent2):
    def __init__(self, x=None, **kwargs):
        print("Child")
        super().__init__(x=x, **kwargs)

    def paintGL2(self):
        print("Extend paintGL")
        Parent2.paint(self)


# use it like this:
e = Child(x=10)
#e.paint()



#%%

_x=2*np.arange(3)
import numpy as np
def func1(x=None):
    if not x is None:
        print("True func1")
        _x=x
    else:
        print("False func1")
        
        
def func2(x):
    if not x is None and not np.array_equal(x, _x):
        print("True func2")
    else:
        print("False func2")

#func2(None)
func2(2*np.arange(3))

_x=2*np.arange(3)

def func11(x=None):
    if not x is None:
        print("True func11")
        _x=x
    else:
        print("False func11")
        
        
def func22(x):
    if np.array_equal(x, _x):
        x=None
    func11(x=x)
#func22(None)
func22(2*np.arange(3))

