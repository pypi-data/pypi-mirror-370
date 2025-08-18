from __future__ import annotations 
from typing import List, Optional, Tuple, Union, Dict, TYPE_CHECKING, Callable, ClassVar
if TYPE_CHECKING:
    from .GL3DViewBox import GL3DViewBox 

import weakref
from pyqtgraph.Qt import isQObjectAlive
from pyvol_terminal.gl_3D_graphing.meta import QABCMeta, abc
from pyqtgraph.opengl import GLGraphicsItem
from .AbstractGLGraphicsItem import AbstractGLGraphicsItem
from .AbstractGLGraphicsItem import ABCGraphicsItemMeta
from PySide6 import QtCore, QtWidgets, QtGui
import numpy as np
from dataclasses import dataclass, field, InitVar
from abc import ABC, abstractmethod
import warnings
from pyqtgraph.Qt import QT_LIB
from functools import wraps 
import traceback
from pprint import pprint
from pyqtgraph import opengl

import importlib

if QT_LIB in ["PyQt5", "PySide2"]:
    QtOpenGL = QtGui
else:
    QtOpenGL = importlib.import_module(f"{QT_LIB}.QtOpenGL")

__all__ = ['GLLinePlotItem']




class BaseGLLinePlotItem(AbstractGLGraphicsItem, opengl.GLLinePlotItem, metaclass=ABCGraphicsItemMeta):
    def __init__(self, parentItem=None, **kwds):

        glopts = kwds.pop('glOptions', 'additive')
        self.setGLOptions(glopts)
        self.pos = None
        self.mode = 'line_strip'
        self.width = 1.
        self.color = (1.0,1.0,1.0,1.0)
        self.antialias = False

        self.m_vbo_position = QtOpenGL.QOpenGLBuffer(QtOpenGL.QOpenGLBuffer.Type.VertexBuffer)
        self.m_vbo_color = QtOpenGL.QOpenGLBuffer(QtOpenGL.QOpenGLBuffer.Type.VertexBuffer)
        self.vbos_uploaded = False
        
        self.setData(**kwds)

    def paintGL(self):
        return opengl.GLLinePlotItem.paint(self)