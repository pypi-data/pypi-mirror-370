#%%
from pyqtgraph.opengl import GLGraphicsItem
from PySide6 import QtCore, QtGui, QtWidgets
from pyqtgraph.opengl import GLViewWidget

import abc
from abc import ABC, ABCMeta, abstractmethod
from PySide6.QtCore import QObject

    
import abc
from PySide6.QtCore import QObject

class QABCMeta(abc.ABCMeta, type(QObject)):
    
    """
    SOURCE:
    https://stackoverflow.com/questions/78778926/creating-a-metaclass-that-inherits-from-abcmeta-and-qobject
    
    """
    
    def __new__(mcls, name, bases, ns, **kw):
        cls = super().__new__(mcls, name, bases, ns, **kw)
        abc._abc_init(cls)
        return cls
    def __call__(cls, *args, **kw):
        if cls.__abstractmethods__:
            raise TypeError(f"Can't instantiate abstract class {cls.__name__} without an implementation for abstract methods {set(cls.__abstractmethods__)}")
        return super().__call__(*args, **kw)






class _ABCQWidgetMeta(type(QtCore.QObject), ABCMeta):...
class ABCQWidget(QtWidgets.QTableWidget, metaclass=_ABCQWidgetMeta):...


class CustomTableWidget(QtWidgets.QWidget, metaclass=ABCQWidget):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)


app = QtWidgets.QApplication()
a = CustomTableWidget()
