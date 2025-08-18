from __future__ import annotations 
from typing import List, Optional, Tuple, Union, Dict, TYPE_CHECKING, Callable, Any
if TYPE_CHECKING:
    from instruments.instruments import Option
 #   from 
    from instruments.utils import InstrumentManager

from PySide6 import QtWidgets, QtCore      
from abc import ABC, abstractmethod, ABCMeta
from ..gl_3D_graphing import meta
from pprint import pprint



class _ABCQWidgetMeta(type(QtCore.QObject), ABCMeta):...
class ABCQWidget(QtWidgets.QWidget, ABC, metaclass=_ABCQWidgetMeta):...

QSplitterMeta = type(QtWidgets.QSplitter)




class ABCInterface(QtWidgets.QMainWindow, metaclass=meta.QABCMeta):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.on_view=False

    
    @abstractmethod
    def get_calibration_slot(self) -> QtCore.Slot:...
    
    @QtCore.Slot()
    def update_view(self, calibrated_engines):
        if self.isVisible():
            self._internal_update_view(calibrated_engines)

    @abstractmethod
    def _internal_update_view(self):...


    
    ### RESUIRES_ABOUTTOCLOSE_TOO
        
    
#class ABCQWidget(QtWidgets.QWidget, ABC, metaclass=QObjectMeta):

QSplitterMeta = type(QtWidgets.QSplitter)



class ABCMainViewMeta222(_ABCQWidgetMeta, QSplitterMeta):
    
    def __init__(self, *args, **kwargs):
        self._intense_interaction=False
        self._interact_end_callbacks: List[Callable]=[]
        self._intenseInteractionContainer: Dict[str, bool]={}
        super().__init__(*args, **kwargs)
        
    @QtCore.Slot()
    def update_view(self, calibrated_engines):
        if self.isVisible():
            self._internal_update_view(calibrated_engines)

    def add_interact_end_callback(self, callback):
        self._interact_end_callbacks.append(callback)
        
    def remove_interact_end_callback(self, callback): 
        self._interact_end_callbacks.remove(callback)
 
    def processInteractionState(self, id, state: bool):
        self._intenseInteractionContainer[id] = state
        current_state = any(self._intenseInteractionContainer.values())
        if current_state != self._intense_interaction:
            self._intense_interaction = current_state
            for callback in self._interact_end_callbacks:
                callback(current_state)
                
    def addIntenseInteraction(self, id):
        self._intenseInteractionContainer[id] = False
    
    def removeIntenseInteraction(self, id):
        del self._intenseInteractionContainer[id]

    @abstractmethod
    def _internal_update_view(self):...


class ABCMainViewQSplitter(QtWidgets.QSplitter, metaclass=meta.QABCMeta):
    
    def __init__(self, *args, **kwargs):
        self._intense_interaction=False
        self._interact_end_callbacks: List[Callable]=[]
        self._intenseInteractionContainer: Dict[str, bool]={}
        super().__init__(*args, **kwargs)
        
    @QtCore.Slot()
    def update_view(self, calibrated_engines):
        if self.isVisible():
            self._internal_update_view(calibrated_engines)

    def add_interact_end_callback(self, callback):
        self._interact_end_callbacks.append(callback)
        
    def remove_interact_end_callback(self, callback): 
        self._interact_end_callbacks.remove(callback)
 
    def processInteractionState(self, id, state: bool):
        self._intenseInteractionContainer[id] = state
        current_state = any(self._intenseInteractionContainer.values())
        if current_state != self._intense_interaction:
            self._intense_interaction = current_state
            for callback in self._interact_end_callbacks:
                callback(current_state)
                
    def addIntenseInteraction(self, id):
        self._intenseInteractionContainer[id] = False
    
    def removeIntenseInteraction(self, id):
        del self._intenseInteractionContainer[id]
        
    @abstractmethod
    def _internal_update_view(self):...


class ABCMainViewQTableWidget(QtWidgets.QTableWidget, metaclass=meta.QABCMeta):
    
    def __init__(self, *args,**kwargs):
        self._intense_interaction=False
        self._interact_end_callbacks: List[Callable]=[]
        self._intenseInteractionContainer: Dict[str, bool]={}
        super().__init__(*args, **kwargs)
        
    @QtCore.Slot()
    def update_view(self, calibrated_engines):
        if self.isVisible():
            self._internal_update_view(calibrated_engines)

    def add_interact_end_callback(self, callback):
        self._interact_end_callbacks.append(callback)
        
    def remove_interact_end_callback(self, callback): 
        self._interact_end_callbacks.remove(callback)
 
    def processInteractionState(self, id, state: bool):
        self._intenseInteractionContainer[id] = state
        current_state = any(self._intenseInteractionContainer.values())
        if current_state != self._intense_interaction:
            self._intense_interaction = current_state
            for callback in self._interact_end_callbacks:
                callback(current_state)
                
    def addIntenseInteraction(self, id):
        self._intenseInteractionContainer[id] = False
    
    def removeIntenseInteraction(self, id):
        del self._intenseInteractionContainer[id]


    @abstractmethod
    def _internal_update_view(self):...



class ABCSettings(QtWidgets.QWidget, metaclass=meta.QABCMeta):
    def __init__(self, *args,**kwargs):
        self._parametersUpdatedCallbacks=[]
        super().__init__(*args, **kwargs)

    def addParametersUpdatedCallback(self, callback):
        self._parametersUpdatedCallbacks.append(callback)
    
    def removeParametersUpdatedCallback(self, callback):
        self._parametersUpdatedCallbacks.remove(callback)
    
    def parametersUpdated(self, new, previous=None):
        for callback in self._parametersUpdatedCallbacks:
            callback(new, previous)