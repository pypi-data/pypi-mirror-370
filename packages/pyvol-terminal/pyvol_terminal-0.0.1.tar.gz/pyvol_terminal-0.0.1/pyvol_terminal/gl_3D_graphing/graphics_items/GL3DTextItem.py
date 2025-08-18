from __future__ import annotations
from typing import List, Optional, Tuple, Union, Dict, TYPE_CHECKING
if TYPE_CHECKING:
    from pyvol_terminal.interfaces.volatility_surface.pyvol_GL3DViewWidget import SurfaceViewWidget
    from .GL3DAxisItem import GL3DViewBox
    from ..widgets.GL3DViewWidget import GL3DViewWidget
    

from pyqtgraph import opengl, Vector
from PySide6 import QtCore, QtGui, QtWidgets
import numpy as np
import math
from ..meta import QABCMeta, abc
from pyqtgraph.opengl import GLGraphicsItem
from OpenGL import GL  
from pprint import pprint   
from .GL3DGraphicsItems import MixedGL3DTextItem
from pyqtgraph import Transform3D

class GL3DTextItem(MixedGL3DTextItem):
    eye_mat = np.eye(4)
    def __init__(self,
                 anchor=(0, 0),
                 resizeToWorld=False,
                 resizeTolerance=0,
                 parentItem=None, 
                 **kwargs
                 ):    
        
        self.lastRect=None
        self.posF=None
        self.resizeTolerance=resizeTolerance
        glopts = kwargs.pop('glOptions', 'additive',)
        self._initDistance, self._initPointSize, self._lastSetDistance=None, None, None
        self._resizeToWorld=resizeToWorld
        self._anchor=anchor
        self.width=None
        self.p=None
        
        super().__init__(parentItem=parentItem, **kwargs)
        self.setGLOptions(glopts)

        
    def compute_projection(self):
        rect = QtCore.QRectF(self.view().rect())
        ndc_to_viewport = QtGui.QMatrix4x4()
        ndc_to_viewport.viewport(rect.left(), rect.bottom(), rect.width(), -rect.height())
        return ndc_to_viewport * self.mvpMatrix()
    
    def linkWidget(self, parent: SurfaceViewWidget):
        super().setParent(parent)
        
    def itemChange(self, change, value):
        ret = super().itemChange(change, value)
        if change == self.GLGraphicsItemChange.ItemViewHasChanged:
            self._initDistance, self._initPointSize=None, None
        return ret

    def _updateSize(self):
        if self._initDistance is None:
            view = self.view()
            if not view is None and hasattr(view, "cameraPosition"):
                distance = GL3DTextItem.distance_between_point_perpendicular_plane(self.pos, self.view().centerPositionNumpy(), self.view().cameraPositionNumpy())
                self._initDistance = distance
                self._initPointSize = self.font.pointSize()
                self._lastSetDistance = distance
                
        else:
                current_distance = GL3DTextItem.distance_between_point_perpendicular_plane(self.pos, self.view().centerPositionNumpy(), self.view().cameraPositionNumpy())
            #if abs(current_distance / self._lastSetDistance - 1) > self.resizeTolerance:
                self._lastSetDistance = current_distance
                r = self._initDistance / current_distance
                newPointSize = r * self._initPointSize
                self.font.setPointSizeF(newPointSize)
            
    def setData(self, **kwargs):
        if "resizeToWorld" in kwargs:
            self.setResizeToWorld(kwargs.pop("resizeToWorld"))
        if "anchor" in kwargs:
            self.setAnchor(kwargs.pop("anchor"))
        super().setData(**kwargs)

    @classmethod
    def distance_between_point_perpendicular_plane(cls, point, p2, p3):
        diff_OC = p2 - p3
        if np.linalg.norm(diff_OC) == 0:
            raise ValueError("Camera is already at the origin. No unique line of sight.")
        
        u_hat = diff_OC / np.linalg.norm(diff_OC)
        return np.dot(point - p3, u_hat)

    def _updatePositionFromAnchor(self, pos: QtGui.QVector3D):
        x, y = pos.x(), pos.y()
        font_metrics = QtGui.QFontMetrics(self.font)
        self.lastRect = font_metrics.tightBoundingRect(self.text)

        height = self.lastRect.height()
        self.width = self.lastRect.width()
        x = x - self._anchor[0] * self.width if self._anchor[0] == 1 else x
        y = y + self._anchor[1] * height if self._anchor[1] == 1 else y
        pos.setX(x)
        pos.setY(y)
        
        
    def setAnchor(self, anchor: Tuple[float, float]) -> None:
        self._anchor = anchor
        
    def setResizeToWorld(self, flag):
        self._resizeToWorld=flag    
        
    def anchor(self): return self._anchor
    def resizeToWorld(self): return self._resizeToWorld


    def _paintHelper(self):...

    def paint(self):
        if len(self.text) < 1:
            return
        self.setupGLState()
        
        if self.resizeToWorld():
            self._updateSize()
            
        project = self.compute_projection()
        vec3 = QtGui.QVector3D(*self.pos)
        self.posF = project.map(vec3).toPointF()        
        
        self._updatePositionFromAnchor(self.posF)
        
        painter = QtGui.QPainter(self.view())
        painter.setPen(self.color)
        painter.setFont(self.font)
        painter.setRenderHints(QtGui.QPainter.RenderHint.Antialiasing | QtGui.QPainter.RenderHint.TextAntialiasing)
        painter.drawText(self.posF, self.text)
        painter.end()

