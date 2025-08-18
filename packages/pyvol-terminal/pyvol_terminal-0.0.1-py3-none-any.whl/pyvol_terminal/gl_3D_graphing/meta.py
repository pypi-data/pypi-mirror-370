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


#%%


from PySide6 import QtCore, QtWidgets
from PySide6.QtWidgets import QApplication
from abc import abstractclassmethod, abstractmethod

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



class ABCInterface(QtWidgets.QWidget, metaclass=QABCMeta):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.on_view=False
        self.main_view: _MainViewMeta=None
        self.hide()
        

