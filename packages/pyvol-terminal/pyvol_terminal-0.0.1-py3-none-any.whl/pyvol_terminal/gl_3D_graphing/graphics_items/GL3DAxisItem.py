from __future__ import annotations 
from typing import List, Optional, Tuple, Union, Dict, TYPE_CHECKING, Callable, Any
if TYPE_CHECKING:
    from pyvol_terminal.gl_3D_graphing.graphics_items.GL3DViewBox import GL3DViewBox
    from pyvol_terminal.gl_3D_graphing.widgets.GL3DViewWidget import GL3DViewWidget

import pyqtgraph.opengl as gl

from pyqtgraph.opengl import GLGraphicsItem, GLViewWidget
from pyqtgraph import opengl
from PySide6 import QtWidgets, QtCore, QtGui
import numpy as np
import weakref
from pyqtgraph.Qt import isQObjectAlive
from pyvol_terminal.gl_3D_graphing.meta import QABCMeta, abc
import pyqtgraph as pg
from pyqtgraph import getConfigOption, functions as fn
from .GL3DTextItem import GL3DTextItem
from .GL3DGraphicsItems import GL3DLinePlotDataItem, MixedGL3DTextItem
from .GL3DGraphicsItemMixin import GL3DGraphicsItemMixin
from .GL3DPlotDataItemMixin import GL3DFlatMeshPlotDataItemMixin
from .GL3DGraphicsItems import MixedGLLinePlotItem
import math
import copy
from pprint import pprint
from ... import utils 
from OpenGL import GLU, GL


from pyqtgraph.Qt import QtGui, QT_LIB
import importlib


class TickItem(MixedGLLinePlotItem):
    def __init__(self, tickLength, axis=None, face=None, name=None, *args, **kwargs):
        self.tickLength=tickLength
        self.axis=axis
        self.face=face
        self.name=name
        super().__init__(*args, **kwargs)
        self.setFlag(self.GLGraphicsItemFlag.ItemHasNoContents)


    
class TickLineset(MixedGLLinePlotItem):
    def __init__(self,
                 *args,
                 **kwargs
                 ):
        
        mode = "lines"    # Keep mode lines for optimized painting for grouped line items 
        kwargs["mode"]=mode
        
        self._lineItems: List[TickItem]=[]
        self._linkedLinesets: List[TickItem]=[]
        
        self._contantArray: np.ndarray=None
        
        self._lineItemsContantMap: Dict[TickItem, int] = {}
        self._linkedLinesetsConstantMap: Dict[TickLineset, Dict[TickItem, Tuple[int, int]]] = {}
        
        super().__init__(*args, **kwargs)

        
    def addConstantLineItem(self, lineItem: TickItem):
        pos = np.array(lineItem.pos)
        
        if self._contantArray is None:
            self._contantArray = pos
            self._lineItemsContantMap[lineItem] = (0, pos.shape[0])
        else:
            self._lineItemsContantMap[lineItem] = (self._contantArray.shape[0], pos.shape[0])
            self._contantArray = np.vstack((self._contantArray, pos))            

    def tickLinesets(self):
        return list(self._linkedLinesetsConstantMap.keys())
    
    def linkTickLineset(self, tickLineset: TickLineset):
        
        #if len(self.tickLinesets()) == 0:
        #    self._linkedLinesetsConstantMap = {tickLineset : {}}
        
        for lineItem in tickLineset.constantLineItems():
            pos = np.array(lineItem.pos)
            if self._contantArray is None:
                self._contantArray = pos
                self._linkedLinesetsConstantMap[tickLineset] = {lineItem : (0, pos.shape[0])}
            else:
                self._linkedLinesetsConstantMap[tickLineset] = {lineItem : (self._contantArray.shape[0], pos.shape[0])}
                self._contantArray = np.vstack((self._contantArray, pos))      
                
        self._linkedLinesets.append(tickLineset)
    
    def linkedLinesets(self) -> List[TickLineset]:
        return self._linkedLinesets
            
    def constantLineItems(self):
        return list(self._lineItemsContantMap.keys())
    
    def lineItems(self):
        return self._lineItems

    def addLineItem(self, item: MixedGLLinePlotItem):        
        self._lineItems.append(item)
    
    def childrenBoundingRect(self):...
    
    def _getWorldPositions(self, item: TickItem):
        """Get item positions in world coordinates"""
        if not hasattr(item, 'pos') or item.pos is None:
            return None
      
        tr = item.transform()
        # Apply transform to get world positions
        pos = item.pos.copy()
        if not tr.isIdentity():
            points_h = np.hstack([pos, np.ones((pos.shape[0], 1))])
            tr_matrix = np.array(tr.data()).reshape(4, 4).T
            transformed_h = points_h @ tr_matrix.T
            pos = transformed_h[:, :3]
        return pos
    
    def stackLineset(self, newPositionAll, lineItems: List[TickItem]):
        for item in lineItems:
            if item.transform().isIdentity():
                newPos = item.pos
            else:
                tr = item.transform()
                tr_matrix = np.array(tr.data()).reshape(4, 4).T  
                points_h = np.hstack([item.pos, np.ones((item.pos.shape[0], 1))])
                transformed_h = points_h @ tr_matrix.T
                newPos = transformed_h[:, :3]
            
            if newPositionAll is None:
                newPositionAll=newPos
            else:
                newPositionAll = np.vstack((newPositionAll, newPos))
        return newPositionAll
    
    def _extractNestedLines(self, combined_pos):
        T = (self.parentItem().transform() * self.transform()).inverted()[0]
        for nestedLineItem in self.linkedLinesets():
            for lineItem in nestedLineItem.lineItems():
                pos = [T.map(QtGui.QVector3D(p[0], p[1], p[2])) for p in lineItem.pos]
                
                pos = [nestedLineItem.parentItem().transform().map(QtGui.QVector3D(p.x(), p.y(), p.z())) for p in pos]
                pos = [nestedLineItem.transform().map(QtGui.QVector3D(p.x(), p.y(), p.z())) for p in pos]
                pos = np.array([[p.x(), p.y(), p.z()] for p in pos])
                
                pos = self._mapLineItem(pos, lineItem.transform())
                combined_pos = pos if combined_pos is None else np.vstack((combined_pos, pos))
                
            self.last_child2pos = pos[-1]
        return combined_pos                    
            
            
    def _mapLineItem(self, pos, tr):        
        if not tr.isIdentity():
            points_h = np.hstack([pos, np.ones((pos.shape[0], 1))])
            tr_matrix = np.array(tr.data()).reshape(4, 4).T
            transformed_h = points_h @ tr_matrix.T
            #pos = transformed_h[:, :3]
            pos = transformed_h[:, :3] / transformed_h[:, 3:4]  
        return pos
    
    def _paintHelper(self):
        newPositionAll = self.stackLineset(self._contantArray, self.lineItems())
        #for lineItem in self.lineItems():
        #    pos = self._mapLineItem(lineItem.pos.copy(), lineItem.transform())
        #    newPositionAll = pos if newPositionAll is None else np.vstack((newPositionAll, pos))
                

        newPositionAll = self._extractNestedLines(newPositionAll)
       
        if not newPositionAll is None:
            self.blockUpdates(True)
            self.setData(pos=newPositionAll, color=self.color)
            self.blockUpdates(False)
            
        super()._paintHelper()
        
        
    
    def paint(self):
        if not (GL3DGraphicsItemMixin.GLGraphicsItemFlag.ItemHasNoContents & GL3DGraphicsItemMixin.flags(self)): 
            self._paintHelper()
            self._childPaint()
        
        

class GL3DAxisTextItem(GL3DTextItem):
    
    def __init__(self,
                 tickLevel: float=None,
                 ref: int=None,
                 **kwargs
                 ):        
        
        super().__init__(**kwargs)
        self._idRef=ref
        
        self.setTickLevel(tickLevel)
        
        
    def setTickLevel(self, tickLevel):self._tickLevel=tickLevel
    def setOffset(self, offset):self._offset=offset
    
    def tickLevel(self):return self._tickLevel
    def offset(self):return self._offset
    def idRef(self):return self._idRef
    
    def setPos(selfm, kwargs):
        return kwargs

    
    @QtCore.Slot(object)
    def updateTextVisibility(self, axis_item: GL3DViewBox):
        if self.idRef() is None:
            return
        if self.idRef() > axis_item._currentTicks[self._tickLevel]-1:
            self.hide()
        else:
            self.show()

class GL3DAxisLabelItem(GL3DAxisTextItem):
    def __init__(self, *args, **kwargs):
        self._linkedTextItems: List[GL3DAxisTextItem]=[]
        super().__init__(*args, **kwargs)
    
    def linkTextValueItems(self, items: List[GL3DAxisTextItem]):
        self._linkedTextItems=items
    
    def _updatePositionFromAnchor(self, pos: QtGui.QVector3D):
        x, y = pos.x(), pos.y()
        font_metrics = QtGui.QFontMetrics(self.font)
        self.lastRect = font_metrics.tightBoundingRect(self.text)

        height = self.lastRect.height()
        width = self.lastRect.width()
        x = x - self._anchor[0] * width if self._anchor[0] == 1 else x
        y = y + self._anchor[1] * height if self._anchor[1] == 1 else y
        
        
        self.lastRect.moveTo(x, y)
        
        # X-direction offset (adjust as needed)
        
        x_offset = 5  
        max_attempts = 20
        attempts = 0
        px_xpos_collect=[]
        px_xposEnd_collect=[]
        for tick in self._linkedTextItems:
            if tick.visible():
                px_xpos_collect.append(tick.posF.x())
                px_xposEnd_collect.append(tick.posF.x() + tick.width if self.anchor()[0]==0 else tick.posF.x() - tick.width)
        n_ticks = len(px_xpos_collect)
        mid_xpos =None
        mid_xposEnd = None
        if n_ticks > 0:
            if n_ticks % 2 == 0:
                mid_xpos = 0.5 * (px_xpos_collect[int(n_ticks/2)-1] + px_xpos_collect[int(n_ticks/2)])
                mid_xposEnd = 0.5 * (px_xposEnd_collect[int(n_ticks/2)-1] + px_xposEnd_collect[int(n_ticks/2)])
            else:
                mid_xpos = px_xpos_collect[int(n_ticks/2)]
                mid_xposEnd = px_xposEnd_collect[int(n_ticks/2)]
            
            
                
            if self._anchor[0] == 0:
                if mid_xposEnd > x:
                    x += mid_xposEnd - x + 5 
            else:
                if mid_xposEnd < x:
                    x += - (x - mid_xposEnd) -5
        pos.setX(x)
        pos.setY(y)
    
                

class GL3DAxisItem(GL3DGraphicsItemMixin):
    sigAxisChanged = QtCore.Signal(QtCore.QObject)
    
    
    """
    
    axis indexes are ordered x == 0, y == 1, z == 2
       
    """
    
    
    directionAxisStr = {0 : "x", 1 : "y", 2: "z"}
    
    
    def __init__(self,
                 axis: int,
                 axisFace: int,
                 worldOrigin: Tuple[int, int, int]=(0, 0, 0),
                 viewRange: List[List[int]]=None,
                 faceRectSize: Tuple[int, int, int]=None,                 
                 text: str="",
                 labelFont: QtGui.QFont | None=QtGui.QFont("Neue Haas Grotesk", 16),
                 labelColor: str=getConfigOption('foreground'),
                 labelOffset: float=0.3, 
                 labelResizeToWorld: bool=True,
                 labelAutoUpdateAnchor: bool=True,
                 labelAnchor: Tuple[float, float]=(0.5, 0.5),
                 showLabel: bool=True,
                 valuesFont: QtGui.QFont | None=QtGui.QFont("Neue Haas Grotesk", 10),
                 valuesColor: Tuple[float,...]=getConfigOption('foreground'),
                 tickLength: float=None,
                 tickColor: Tuple[float,...]=getConfigOption('foreground'),
                 linkView: GL3DViewBox=None,
                 parentItem=None,
                 showFaceBorder: bool=True,
                 showValues: bool=True,
                 faceTickOffset: float=-0.05,
                 tickTextOffset: float=0.03,
                 tickMarginOffset: float=0,
                 graphFaceOffset: float=-0.05,
                 invertedFromWorld: bool=False,
                 valuesAnchor: Tuple[float, float]=(0., 0.),
                 textResizeToWorld: bool=True,
                 textAutoUpdateAnchor: bool=True,
                 syncToView: bool=True,
                 showGrid: bool=True,
                 showTicks: bool=True,
                 showTickMargin: bool=True,
                 **kwargs
                 ):
        super().__init__(parentItem=parentItem)
        self.flipped=False

        self._initLayout(axis, axisFace, worldOrigin, viewRange)
        self._initPerformanceParameters()
        
        self.setParentItem(parentItem)
        
        self._nTicksMajor = 6
        
        self._linkedView = None
        self._name=None
        if tickLength is None:
            tickLength = abs([size for ax, size in enumerate(faceRectSize) if ax != axis and size != 0].pop(0)) / 14
        
        self.style = {
            #        'tickTextOffset': [5, 2],  ## (horizontal, vertical) spacing between text and axis
                    'tickTextWidth': 30,  ## space reserved for tick text
                    'tickTextHeight': 18,
                    'autoExpandTextSpace': True,  ## automatically expand text space if needed
                    'autoReduceTextSpace': True,
                #   'hideOverlappingLabels': hide_overlapping_labels,
                    'valuesFont': valuesFont,
                    "valuesColor" : valuesColor,
                    "tickColor" : tickColor,
                    'stopAxisAtTick': (False, False),  ## whether axis is drawn to edge of box or to last tick
                    'textFillLimits': [  ## how much of the axis to fill up with tick text, maximally.
                        (0, 0.8),    ## never fill more than 80% of the axis
                        (2, 0.6),    ## If we already have 2 ticks with text, fill no more than 60% of the axis
                        (4, 0.4),    ## If we already have 4 ticks with text, fill no more than 40% of the axis
                        (6, 0.2),    ## If we already have 6 ticks with text, fill no more than 20% of the axis
                                    ],
                    'showValues': showValues,
                    "showFaceBorder"  : showFaceBorder,
                    "tickLength" : tickLength,
                    "maxNticksperLevel" : 10,
                    "tickWidth" : [2.5, 1.5],
                    'maxTickLevel': 1,
                    'maxTextLevel': 1,
                    'tickAlpha': None,  ## If not none, use this alpha for all ticks.
                    "invertedFromWorld" : int(invertedFromWorld),
                    "valuesAnchor" : valuesAnchor,
                    "textAutoUpdateAnchor" : textAutoUpdateAnchor,
                    "textAnchorVar" : None,
                    "tickTextOffset" : tickTextOffset,
                    "labelOffset" : labelOffset,
                    "faceTickOffset" : faceTickOffset,
                    "graphFaceOffset" : graphFaceOffset,
                    "showGrid" : showGrid,
                    "showLabel" : showLabel,
                    "showTicks" : showTicks,
                    "showTickMargin" : showTickMargin,
                    "syncToView" : syncToView,
                    
                }
        self.textWidth = 30  ## Keeps track of maximum width / height of tick text
        self.textHeight = 18
        self._currentTicks=[0 for _ in range(self.style["maxTickLevel"] + 1)]
        
        self.transformCondtions = {}
        
        self.offsetStyle = {"graphFaceOffset" : graphFaceOffset,
                            "tickMargin" : tickMarginOffset,
                            "ticks" : faceTickOffset,
                           # "tickText" : ValuesOffset,
                            "labelOffsetFace" : labelOffset,
                            }
    
        self.fixedWidth = None
        self.fixedHeight = None

        self.logMode = False

        self._tickDensity = 1.0   # used to adjust scale the number of automatically generated ticks
        self._tickLevels  = None  # used to override the automatic ticking system with explicit ticks
        self._tickSpacing = None  # used to override default tickSpacing method
       # self.scale = 1.0
        self.scale_pyqtgraph=1
        self.autoSIPrefix = False
        self.autoSIPrefixScale = 1.0
        self._siPrefixEnableRanges = None    
        

        self.labelText = ""
        self.labelUnits = ""
        self.labelUnitPrefix = ""
        self._labelItem = None
        
        self.label = None
        self.tickText = None
        
        self._GLItems = {"values" : None,
                         "ticks" : None, 
                         "tickLineset" : None,
                         "label" : None,
                         "faceBorder" : None,
                         "tickMargin" : None,
                         }
        self._GLItems: Dict[str, MixedGL3DTextItem|GL3DLinePlotDataItem]
        
        self.tickStyle = {"textResizeToWorld" : textResizeToWorld,
                          "valuesAnchor" : valuesAnchor,
                          "textAutoUpdateAnchor" : textAutoUpdateAnchor or valuesAnchor != (0, 0),
                          "showValues" : showValues,
                          'valuesFont': valuesFont,
                          "tickLength" : tickLength,
                          }
        
        labelAutoUpdateAnchor = showLabel and (labelAutoUpdateAnchor or labelAnchor != (0, 0))
        self.labelStyle = {"labelText" : text,
                           "labelColor" : labelColor or getConfigOption('foreground'),
                           "labelFont" : labelFont,
                           "labelAnchor" : labelAnchor,
                           "labelAutoUpdateAnchor" : labelAutoUpdateAnchor,
                           "labelResizeToWorld" : labelResizeToWorld,
                           "labelOffsetFace" : labelOffset,
                           "showLabel" : showLabel,
                           }
        self._cameraPositionChanged=True
        self._baseTickWorldCoords = None
        
        self._initGLItems()
    
        self.setRange(*self.viewBoxRange("axis"))
        
        if self.style["showLabel"]:
            self.setLabel(**self.labelStyle)

        self._linkedView = None
        
        if linkView is not None:
            self._linkToView_internal(linkView)
            
        self.setTickStyle(valuesColor=valuesColor,
                          valuesFont=QtGui.QFont("Neue Haas Grotesk", 10),
                          valuesAnchor=self.style["valuesAnchor"],
                          )
        
        self._setItemData()    
    
    
    def _initGLItems(self):
        self._GLItems["tickLineset"] = self._initTickItems()
        
        if self.style["showValues"]:
            self.tickText = self._initValueTextItems()
        
        if self.style["showLabel"]:
            self.label = self._initLabelTextItem()        
            self.label.linkTextValueItems(self.tickText[0])    
        
        if self.style["showFaceBorder"]:
            self._GLItems["faceBorder"] = self._initFaceRectBorderItem()     
          
        if self.style["showTicks"] and self.style["showTickMargin"]:
            self._GLItems["tickMargin"] = self._initTickMarginItem()
        
                
    def _setDataHelper(self):...
    def clipDataFromVRange(self):...
    
    def enableAutoSIPrefix(self, enable=True):
        """
        Enable (or disable) automatic SI prefix scaling on this axis.

        When enabled, this feature automatically determines the best SI prefix
        to prepend to the label units, while ensuring that axis values are scaled
        accordingly.

        For example, if the axis spans values from -0.1 to 0.1 and has units set
        to 'V' then the axis would display values -100 to 100
        and the units would appear as 'mV'

        This feature is enabled by default, and is only available when a suffix
        (unit string) is provided to display on the label.

        Parameters
        ----------
        enable : bool, optional
            Enable Auto SI prefix, by default True.
        """

        self.autoSIPrefix = enable
        self.updateAutoSIPrefix()
    
    
    def updateAutoSIPrefix(self):
        scale = 1.0
        prefix = ''
        if self.label.visible():
            _range = 10**np.array(self.range) if self.logMode else self.range
            scaling_value = max(abs(_range[0]), abs(_range[1])) * self.scale_pyqtgraph
            if any(low <= scaling_value <= high for low, high in self.getSIPrefixEnableRanges()):
                (scale, prefix) = fn.siScale(scaling_value)

        self.autoSIPrefixScale = scale
        self.labelUnitPrefix = prefix
        
    def _updateLabel(self):
        if self.style["showLabel"]:
            self.label.setData(text=self.labelString())
        
    def getSIPrefixEnableRanges(self):
        """
        Get the ranges in which automatic SI prefix scaling is enabled.

        Returns
        -------
        tuple of tuple of float, float
            A tuple of ranges where SI prefix scaling is enabled. Each range is a tuple
            containing two floats representing the start and end of the range. If no
            custom ranges are set, then the default ranges are returned. The default
            ranges are ``((0., 1.), (1e9, inf))`` if units are empty, and 
            ``((0., inf))`` otherwise.
        """
        if self._siPrefixEnableRanges is not None:
            return self._siPrefixEnableRanges
        elif self.labelUnits == '':
            return (0., 1.), (1e9, float('inf'))
        else:
            return ((0., float('inf')),)
        
    def viewBoxRange(self, ax_or_ax_type):
        if isinstance(ax_or_ax_type, int):
            return self.geometry["viewRange"][ax_or_ax_type]
        elif isinstance(ax_or_ax_type, str):
            return self.geometry["viewRange"][self.geometry[ax_or_ax_type]]
    
    def _transformToView(self, viewRange):
        xmin, xmax = viewRange[0]
        ymin, ymax = viewRange[1]
        zmin, zmax = viewRange[2]
        self.blockUpdates(True)
        self.scale(xmax - xmin, ymax - ymin, zmax - zmin, False)
        self.blockUpdates(False)
        self.translate(xmin, ymin, zmin, False)

    
    def _linkToView_internal(self, view: GL3DViewBox):
        self.unlinkFromView()
        self._linkedView = weakref.ref(view)
        self._transformToView(view.worldRange())

        if self.geometry["axis"] == 0:
            view.sigXRangeChanged.connect(self.linkedViewChanged)
        elif self.geometry["axis"] == 1:
            view.sigYRangeChanged.connect(self.linkedViewChanged)
        else:
            view.sigZRangeChanged.connect(self.linkedViewChanged)
        view.sigResized.connect(self.linkedViewChanged)
        
        if isinstance(view.parentWidget(), GLViewWidget):
            plotitem_widget = view.parentWidget()
                        
            if self.style["syncToView"]:
                plotitem_widget.sigViewAngleChanged.connect(self.cameraPositionChanged)
                self.autoUpdatePosition(plotitem_widget)
        
            if self.tickStyle["textAutoUpdateAnchor"] or self.labelStyle["labelAutoUpdateAnchor"]:
                    plotitem_widget.sigViewAngleChanged.connect(self.cameraPositionChanged)
                    self.autoUpdateAnchor(plotitem_widget)
                
    def _initTransform(self, origin):
        tr = self.transform()
        for ax in range(3):
            
            translation = np.zeros(3)
            translation[ax] = -0.5 

            tr.translate(* (-1 *translation))

            scales = [1, 1, 1]
            scales[ax] *= (1 - 2 * origin[ax])
            
            tr.scale(*scales)
            tr.translate(*translation)
        self.setTransform(tr)


    def _initLayout(self, axis, axisFace, worldOrigin, viewRange):
        if viewRange is None:
            viewRange = np.repeat(np.array([[0. ,1.]]), 3, axis=0)
        else:
            viewRange = np.array(viewRange, dtype=float)
            
        self.geometry={"axis" : axis,
                       "axisFace" : axisFace,
                       "axisOrtho" : ({0, 1, 2} - {axis, axisFace}).pop(),
                       "localOrigin" : [0., 0., 0.],
                       "worldOrigin" : worldOrigin,
                       "viewRange" : np.repeat(np.array([[0. ,1.]]), 3, axis=0),  # set dummy viewRange before calling  _setViewRange
                       }
        
        self._initTransform(worldOrigin)
        self.geometry["viewRange"] = viewRange
    
    def _initPerformanceParameters(self):
        self.__geometryPerformance = {}
        
        
        z_1 = self.geometry["localOrigin"].copy()
        z_1[self.geometry["axisFace"]] = np.diff(self.viewBoxRange("axisFace")).item()
        
        self.__geometryPerformance["localRangeQVector"] = pg.Vector(*self.geometry["localOrigin"]), pg.Vector(*z_1)

        
    
    @classmethod
    def fromViewBoxRange(cls,
                         viewRange: list[list[float]] | Dict[str, list[float]],   # limits of the viewBox in world coordinates [[x_min, x_max], [y_min, y_max], [z_min, z_max]] or {"x" : [x_min, x_max], "y" : [y_min, y_max], "z" : [z_min, z_max]}
                         axis: str | int,
                         worldOrigin: Tuple[int, int, int]|Dict[str, int]=None, #    extremum values must be either 0 or 1, and orients the axis origin in world coordinates. {"x" : int, "y" : int ,..} or (int, int ,int)
                         faceDirection: str | int | None = None,         # faceDirection is the direction that shares the rectangular-face with the axis-direction along the viewRange. e.g. for the unit-cube with direction==x faceDirection==y for the xy face
                         **kwargs
                         ) -> 'GL3DViewBox':
        
        worldOrigin = list(worldOrigin)
        
        direction_size = [d - worldOrigin[axis] for d in viewRange[axis] if d != worldOrigin[axis]][0]
        faceDirection_size = [d - worldOrigin[faceDirection] for d in viewRange[faceDirection] if d != worldOrigin[faceDirection]][0]
        
        faceRectSize = [0, 0, 0]
        faceRectSize[axis] = direction_size
        faceRectSize[faceDirection] = faceDirection_size

        axisItem  = cls(axis,
                        axisFace=faceDirection,
                        worldOrigin=worldOrigin,
                        viewRange=viewRange,
                        faceRectSize=faceRectSize,
                        faceDirection=faceDirection,
                        **kwargs)    
        return axisItem
    
    def _initFaceRectBorderItem(self) -> opengl.GLLinePlotItem:
        
        p1 = [0.]*3
        p1[:] = self.geometry["localOrigin"]
        p2 = p1.copy()
        
        p2[self.geometry["axis"]] = 1. - self.geometry["localOrigin"][self.geometry["axis"]]
        
        p3 = p1.copy()
        p3[self.geometry["axis"]] = 1. - self.geometry["localOrigin"][self.geometry["axis"]]
        p3[self.geometry["axisFace"]] = 1. - self.geometry["localOrigin"][self.geometry["axisFace"]]
        
        p4 = p1.copy()
        p4[self.geometry["axisFace"]] = 1.- self.geometry["localOrigin"][self.geometry["axisFace"]]
        
        segments = [p1, p2, p2, p3, p3, p4, p4, p1]
        
        borderline = MixedGLLinePlotItem(pos=segments,
                                        color= self.style["tickColor"],
                                        glOptions="translucent",
                                        mode="lines",
                                        )
        borderline.name = "borderline"
        self._GLItems["tickLineset"].addConstantLineItem(borderline)
        
        borderline.setParentItem(self._GLItems["tickLineset"])
        
        return borderline
    
    
    def _initTickMarginItem(self):
        p1 = [0.]*3
        p1[:] = self.geometry["localOrigin"]
        
        p2 = p1.copy()
        p2[self.geometry["axis"]] = 1. - self.geometry["localOrigin"][self.geometry["axis"]]
        
        marginline = MixedGLLinePlotItem(pos=[p1, p2],
                                        color= self.style["tickColor"],
                                        glOptions="translucent",
                                        mode="lines",
                                        )
        marginline.setTransform(self.tickItems.transform())
        marginline.name="margin"
        self._GLItems["tickLineset"].addConstantLineItem(marginline)
        
        marginline.setParentItem(self._GLItems["tickLineset"])
        return marginline
    

    def _validate_kwargs(self, direction, orthoCoords, perpendicular_axis, viewBoxRange):
        c_viewBoxRange = viewBoxRange.copy() if isinstance(viewBoxRange, list) else viewBoxRange.tolist().copy()
        _ = c_viewBoxRange.pop(direction)
        orthoCoords = list(orthoCoords)
        if not all(orthoCoords[idx] in ax for idx, ax in enumerate(c_viewBoxRange)):
            raise ValueError("Orthogonal Coordinates do not match the viewBox range")

    def _childPaint(self):...
    
    def _setItemData(self):
        tickLevels, tickLevelsWorld = self.tickValues(*self.range, 1)
        self.updateLineItems(tickLevelsWorld)
        
        if self.style["showValues"]:
            self.updateTextItems(tickLevels, tickLevelsWorld)

    def _paintHelper(self):
        v = self.view()
        if not v is None:
            if self.style["syncToView"] and self._cameraPositionChanged:
                self.autoUpdatePosition(v, False)
            if self.style["showValues"] and self._cameraPositionChanged and (self.tickStyle["textAutoUpdateAnchor"] or self.labelStyle["labelAutoUpdateAnchor"]):
                self.autoUpdateAnchor(v, False)
            self._cameraPositionChanged=False
        self._setItemData()        
        
        self._updateLabel()
        
        self.sigAxisChanged.emit(self)

    def _initValueTextItems(self) -> List[List[GL3DAxisTextItem]]:
        gl_objects_level = []
        idx=0
        if self.style["showTicks"]:
            parent = self.tickItems
            parent_offset = parent.tickLength
        else:
            parent = self
            parent_offset = 0.
        
        for jdx in range(self.style["maxTextLevel"] + 1):
            gl_objects = []
            for idx in range(self.style["maxNticksperLevel"]):                
                gl_object = GL3DAxisTextItem(tickLevel=jdx,
                                             ref=idx,
                                             anchor=self.tickStyle["valuesAnchor"],
                                             font=self.tickStyle["valuesFont"], 
                                             resizeToWorld=True,
                                             resizeTolerance=0.1,
                                             )
                offset = [0., 0., 0.,]
                offset[self.geometry["axisFace"]] = parent_offset + self.style["tickTextOffset"]
                gl_object.translate(*offset)
                gl_object.setParentItem(parent)
                gl_object.hide()                
                self.sigAxisChanged.connect(gl_object.updateTextVisibility)
                gl_objects.append(gl_object)
                idx+=1
            gl_objects_level.append(gl_objects)
        return gl_objects_level
    
    
    
    def tickValues(self, minVal:float, maxVal:float, size: float):
        minVal, maxVal = sorted((minVal, maxVal))

        minVal *= self.scale_pyqtgraph
        maxVal *= self.scale_pyqtgraph

        ticks = []
        ticksWorld = []
        
        
        tickLevels = self.tickSpacing(minVal, maxVal, size)
        allValues = np.array([])
        
        for i in range(len(tickLevels)):
            spacing, offset = tickLevels[i]

            ## determine starting tick
            start = (math.ceil((minVal-offset) / spacing) * spacing) + offset

            ## determine number of ticks
            num = int((maxVal-start) / spacing) + 1
            values = (np.arange(num) * spacing + start) / self.scale_pyqtgraph
            ## remove any ticks that were present in higher levels
            ## we assume here that if the difference between a tick value and a previously seen tick value
            ## is less than spacing/100, then they are 'equal' and we can ignore the new tick.
            close = np.any(
                np.isclose(
                    allValues,
                    values[:, np.newaxis],
                    rtol=0,
                    atol=spacing/self.scale_pyqtgraph*0.01
                ),
                axis=-1
            )
            values = values[~close]                
            allValues = np.concatenate([allValues, values])
            ticks.append((spacing/self.scale_pyqtgraph, values.tolist()))
            ticksWorld.append((self.mapTextToWorld(spacing/self.scale_pyqtgraph), self.mapTextToWorld(values).tolist()))
            self._currentTicks[i] = len(values.tolist())
        return ticks, ticksWorld
    
    def tickStrings(self, values: list[float], scale: float, spacing: float):
        """
        Return the strings that should be displayed at each tick value.

        This method is used to generate tick strings, and is called automatically.

        Parameters
        ----------
        values : list of float
            List of tick values.
        scale : float
            The scaling factor for tick values.
        spacing : float
            The spacing between ticks.

        Returns
        -------
        list of str
            List of strings to display at each tick value.
        """
        
            
        disp_spacing = spacing * scale
        if disp_spacing > 0:
            places = max(0, math.ceil(-math.log10(disp_spacing)))
        else:
            places = 0

        strings = []
        for v in values:
            # Apply scale only once
            vs = v * scale
            if abs(vs) < .001 or abs(vs) >= 10000:
                vstr = "%g" % vs
            else:
                vstr = ("%%0.%df" % places) % vs
            strings.append(vstr)
        return strings


    def _invalidateTickCache(self):
        """Reset all cached calculations that depend on scale"""
        self._tickLevels = None
        self._autoRangeNeedsUpdate = True
        self._matrixNeedsUpdate = True
        self._initDistance = None
        self._initPointSize = None
        self._lastSetDistance = None

    def updateLineItems(self, tickLevelsWorld):
        def _append_update(base, lineLength, target_list):
            pos = base.copy()
            pos[self.geometry["axisFace"]] = lineLength
            target_list.append(base)
            target_list.append(pos)

        tickPositions = []
        gridPositions = []
        
        for idx, ticksWorld in enumerate(tickLevelsWorld, start=1):
            for tick in ticksWorld[1]:
                basePosition = [0., 0., 0., ]
                basePosition[self.geometry["axis"]] = tick
                if self.style["showTicks"]:
                    _append_update(basePosition, self.style["tickLength"] / idx, tickPositions)

                if self.style["showGrid"]:
                    _append_update(basePosition, np.diff(self.viewBoxRange("axisFace")).item(), gridPositions)

        if self.style["showTicks"]:
            self.tickItems.blockUpdates(True)
            self.tickItems.setData(pos=np.array(tickPositions))
            self.tickItems.blockUpdates(False)
            
        if self.style["showGrid"]:
            self._GLItems["Grids"].blockUpdates(True)
            self._GLItems["Grids"].setData(pos=np.array(gridPositions))
            self._GLItems["Grids"].blockUpdates(False)
            

    def updateTextItems(self, tickLevels, tickLevelsWorld):
        for jdx, (ticks, ticksWorld) in enumerate(zip(tickLevels, tickLevelsWorld)):
            spacing, values = ticks
            strings = self.tickStrings(values, self.scale_pyqtgraph, spacing)
            for idx, (value, string, tickWorld) in enumerate(zip(values, strings, ticksWorld[1])):
                
                if jdx > self.style["maxTextLevel"]:
                    break
                text_item=self.tickText[jdx][idx]
                basePosition=self.geometry["localOrigin"].copy()
                basePosition[self.geometry["axis"]] = tickWorld

                text_item.blockUpdates(True)
                text_item.setData(pos=basePosition, text=string)
                text_item.blockUpdates(False)
                
        
                
    def setRange(self, mn: float, mx: float):
        if not math.isfinite(mn) or not math.isfinite(mx):
            raise ValueError(f"Not setting range to [{mn}, {mx}]")
        
        self.range = [mn, mx]
        if self.autoSIPrefix:
            # XXX: Will already update once!
            self.updateAutoSIPrefix()
    #    self._setItemData()
        
        #self.sigAxisChanged.emit(self)        
        
        
    def setTextFont(self, font=None):
        if font is None:
            getConfigOption("foreground")

    def setScale(self, scale=1.0):
        """
        Set the value scaling for this axis.

        Setting this value causes the axis to draw ticks and tick labels as if the view
        coordinate system were scaled.

        Parameters
        ----------
        scale : float, optional
            Value to scale the drawing of ticks and tick labels as if the view
            coordinate system was scaled, by default 1.0.
        """
        
        if scale != self.scale_pyqtgraph:
            self.scale_pyqtgraph = scale
            self._updateLabel()
        self._invalidateTickCache()  
        self.update()
            
    def setLabel(self,
                labelText: str | None=None,
                labelColor: str | None=None,
                labelFont: str | None=None,
                labelAnchor: str=None,
                labelResizeToWorld: bool=None,
                labelAutoUpdateAnchor: bool=None,
                showLabel: bool=None,
                unitPrefix: str | None=None,
                **kwargs
                ):  
        if not labelText is None:
            self.labelText = labelText
        
        visible = bool(self.labelText)
        if visible:
            self.label.setData(text=self.labelText)
        else:
            self.label.setData(text="")
        if not showLabel is None:
            if showLabel and not visible:
                raise
            
        self.showLabel(visible)
        
        if "labelOffsetFace" in kwargs:
            del kwargs["labelOffsetFace"]

        if not labelColor is None:
            self.labelStyle["labelColor"] = labelColor
        if not labelFont is None:
            self.labelStyle["labelFont"] = labelFont
        if not labelAnchor is None:
            self.labelStyle["labelAnchor"] = labelAnchor
        if not labelResizeToWorld is None:
            self.labelStyle["labelResizeToWorld"] = labelResizeToWorld and visible
            self.labelText
        
        if not labelAutoUpdateAnchor is None:
            self.labelStyle["labelAutoUpdateAnchor"] = (labelAutoUpdateAnchor or labelAnchor != (0, 0)) and visible
        
        kwargs = {"resizeToWorld" : self.labelStyle["labelResizeToWorld"],
                  "text" : self.labelText,
                  "color" : self.labelStyle["labelColor"],
                  "font" : self.labelStyle["labelFont"],
             #     "anchor" : self.labelStyle["labelAnchor"],
                  }
        
        self.label.setData(**kwargs)
    
    def showLabel(self, show: bool=True):
        if show:
            self.label.show()
        else:
            self.label.hide()
    
    def setTickStyle(self,
                     tickColor: str | None=None,
                     tickAnchor: Tuple[float, float]=(0., 0.),
                     valuesFont: str | None=None,
                     textResizeToWorld: bool=True,
                     textAutoUpdateAnchor: bool=None,
                     showValues: bool=None,
                     *args,
                     **kwargs
                     ):
        
        if not tickColor is None:
            self.tickStyle["tickColor"] = tickColor            
        if not valuesFont is None:
            self.tickStyle["valuesFont"] = valuesFont            
        if not tickAnchor is None:
            self.tickStyle["tickAnchor"] = tickAnchor
        if not textResizeToWorld is None:
            self.tickStyle["textResizeToWorld"] = textResizeToWorld
        if not tickAnchor is None:
            self.tickStyle["tickAnchor"] = tickAnchor
        if not showValues is None:
            self.tickStyle["showValues"] = showValues
        
        if not textAutoUpdateAnchor is None:
            self.tickStyle["textAutoUpdateAnchor"] = (textAutoUpdateAnchor or tickAnchor != (0, 0)) and self.tickStyle["showValues"]

        if self.tickStyle["showValues"]:
        
            if "values" in self._GLItems and valuesFont:
                for tick_level in self.tickText:
                    for item in tick_level:
                        item.setData(font=self.tickStyle["valuesFont"])
    
    def _initLabelTextItem(self) -> GL3DAxisLabelItem:
        pos = np.zeros(3)
        pos[self.geometry["axis"]] = 0.5 * self.viewBoxRange("axis").sum()
        pos[self.geometry["axisFace"]] = self.style["tickLength"] + self.style["tickTextOffset"] + self.style["labelOffset"]
        labelItem = GL3DAxisLabelItem(pos=pos,
                                      anchor=self.labelStyle["labelAnchor"],
                                      font=self.labelStyle["labelFont"], 
                                      resizeToWorld=True,
                                      resizeTolerance=0.1,
                                      )
        labelItem.setParentItem(self.tickItems)
        return labelItem

    def _createTickitems(self):
            ticks = TickItem(self.style["tickLength"],
                             axis=self.geometry["axis"],
                             face=self.geometry["axisFace"],
                             glOptions="translucent",
                             antialias=True,
                             mode="lines",
                             )
            
            self.tickItems = ticks
            
            translation = np.array([0., 0., 0.])
            translation[self.geometry["axisFace"]] = self.geometry["localOrigin"][self.geometry["axisFace"]]
            
            tr = ticks.transform()
            
            tr.translate(*(-1 *translation))
            scale = [1, 1, 1]
            scale[self.geometry["axisFace"]] *= -1 
            tr.scale(*scale)

            tr.translate(*translation)
            translate_back = [0., 0., 0.,]
            translate_back[self.geometry["axisFace"]] = - 1*np.array(self.style["faceTickOffset"])
            
            tr.translate(*translate_back)
            return ticks
        
    def _initTickItems(self) -> TickLineset:
        tickItem = TickLineset(glOptions="translucent",
                                antialias=True,
                                color=self.style["tickColor"],
                                width=self.style["tickWidth"][0],
                                mode="lines",
                                )
        
        offset = [0., 0., 0.,]
        offset[self.geometry["axisOrtho"]] = self.style["graphFaceOffset"]
        tickItem.translate(*offset)
        if self.style["showTicks"]:
            ticks = self._createTickitems()
            ticks.name="ticks"
            tickItem.addLineItem(ticks)
            ticks.setParentItem(tickItem)
        
        if self.style["showGrid"]:
            gridLength = np.diff(self.viewBoxRange("axisFace")).item()
            grids = TickItem(gridLength,
                             axis=self.geometry["axis"],
                             face=self.geometry["axisFace"],
                             glOptions="translucent",
                             antialias=True,
                             mode="lines",
                             )
            grids.name="grids"
            tickItem.addLineItem(grids)
            grids.setParentItem(tickItem)
            self._GLItems["Grids"] = grids
        else:
            self._GLItems["Grids"] = None
            
        tickItem.setParentItem(self)
        return tickItem
    
    def checkWidths(self, textNum: str):...
    
    @QtCore.Slot(object)
    @QtCore.Slot(object, object)
    def linkedViewChanged(self, view: GL3DViewBox, newRange=None):
        if newRange is None:
            newRange = view.viewRange()[self.viewBoxRange("axis")]
        self.setRange(*newRange)
        

    def tickSpacing(self, minVal: float, maxVal: float, size: float):
        _tickDensity=1
        dif = abs(maxVal - minVal)
        if dif == 0:
            return []

        ref_size = 300. # axes longer than this display more than the minimum number of major ticks
        minNumberOfIntervals = max(
            2.25,       # 2.0 ensures two tick marks. Fudged increase to 2.25 allows room for tick labels.
            2.25 * _tickDensity * math.sqrt(size/ref_size) # sub-linear growth of tick spacing with size
        )

        majorMaxSpacing = dif / minNumberOfIntervals

        mantissa, exp2 = math.frexp(majorMaxSpacing)
        p10unit = 10. ** (
            math.floor(
                (exp2-1)
                / 3.32192809488736
            ) - 1
        )
        
        if 100. * p10unit <= majorMaxSpacing:
            majorScaleFactor = 10
            p10unit *= 10.
        else:
            for majorScaleFactor in (50, 20, 10):
                if majorScaleFactor * p10unit <= majorMaxSpacing:
                    break
        
        majorInterval = majorScaleFactor * p10unit
        levels = [
            (majorInterval, 0),
        ]

        if self.style['maxTickLevel'] >= 1:
            # Modified this section to choose a smaller interval for minor ticks
            if majorScaleFactor == 10:
                minorScaleFactor = 5  # Half of major interval for minor ticks
            elif majorScaleFactor == 20:
                minorScaleFactor = 10  # Half of major interval
            elif majorScaleFactor == 50:
                minorScaleFactor = 25  # Half of major interval
            else:
                minorScaleFactor = majorScaleFactor / 2  # Default to half
            
            minorInterval = minorScaleFactor * p10unit
            levels.append((minorInterval, 0))

        if self.style['maxTickLevel'] >= 2:
            # Keep the extra level logic but ensure it's smaller than minor interval
            if majorScaleFactor == 10:
                extraScaleFactor = 2  # Smaller than minor interval
            elif majorScaleFactor == 20:
                extraScaleFactor = 5  # Smaller than minor interval
            elif majorScaleFactor == 50:
                extraScaleFactor = 10  # Smaller than minor interval
            else:
                extraScaleFactor = minorScaleFactor / 2  # Default to half
            
            extraInterval = extraScaleFactor * p10unit
            if extraInterval < minorInterval:
                levels.append((extraInterval, 0))
        return levels
    
    def _axisSizePixels(self):
        view = self.view()
        
        ax_local_s, ax_local_f = pg.Vector(0, 0, 0), pg.Vector(0, 0, 1)
        
        ax_view_s, ax_view_f = self.mapToView(ax_local_s), self.mapToView(ax_local_f)
        
        
        px_x, px_y, px_z = GL3DAxisItem.map_3D_coords_to_2D(view, ax_view_s.x(), ax_view_s.y(), ax_view_s.z())



    def mapTextToWorld(self, value):
        rmin, rmax = self.range
        view = self.linkedView()
        
        if view is None:
            world_bounds = 0, 1
        else:
            world_bounds = view.state["worldRange"][self.geometry["axis"]]
                                    
        dif = rmax - rmin
        
        if rmax == rmin:
            scale = 1
            offset = 0
            value
        else:
            scale = (world_bounds[1] - world_bounds[0]) / dif
            offset = world_bounds[0] - rmin * scale

        mapped = scale * value + offset
        return mapped * (1 / (world_bounds[1] - world_bounds[0]))
    
    def labelString(self):
        if self.labelUnits == '':
            if not self.autoSIPrefix or self.autoSIPrefixScale == 1.0:
                units = ''
            else:
                units = f'(x{1.0 / self.autoSIPrefixScale:g})'
        else:
            units = f'({self.labelUnitPrefix}{self.labelUnits})'
        
        return f'{self.labelText} {units}' if bool("") else self.labelText
    
    def flipAboutOrtho(self):
        # Flip face to the other side of the graph
        tr = self.transform()
        translate = [0, 0, 0]
        translate[self.geometry["axisOrtho"]] = 1 
        tr.translate(*translate)
        scale = [1, 1, 1]
        scale[self.geometry["axisOrtho"]] *= -1
        tr.scale(*scale)

    def flipAboutFace(self):
        # Flip ticks and values to the other side of the face 
        midPoint = [0, 0, 0]
        midPoint[self.geometry["axisFace"]] = 0.5 
        midPoint_reverse = midPoint.copy()
        midPoint_reverse[self.geometry["axisFace"]] = -0.5
        
        tr = self.transform()
        tr.translate(*midPoint)

        scales = [1, 1, 1]
        scales[self.geometry["axisFace"]] *= -1
        
        tr.scale(*scales)
        tr.translate(*(midPoint_reverse))
    
    @QtCore.Slot(object)
    def cameraPositionChanged(self, plotitem_widget):
        self._cameraPositionChanged=True
    
    @QtCore.Slot(object)
    def autoUpdatePosition(self, plotitem_widget: GL3DViewWidget, block=True):
        if block:
            return
        cameraPosition = plotitem_widget.cameraPosition()
        
        mapped = self.mapFromParent(cameraPosition)        
        
        axisFacePosition = getattr(mapped, self.directionAxisStr[self.geometry["axisFace"]])()
        axisFaceRange = self.viewBoxRange("axisFace")
        
        if axisFacePosition - (axisFaceRange[1] - axisFaceRange[0]) > 0: 
            self.flipAboutFace()

        axisOrthoPosition = getattr(mapped, self.directionAxisStr[self.geometry["axisOrtho"]])()
        axisOrthoRange = self.viewBoxRange("axisOrtho")
        
        if axisOrthoPosition + (axisOrthoRange[1] - axisOrthoRange[0]) < 0: 
            self.flipAboutOrtho()
            
            
    @classmethod
    def clockwise_angle(cls, p1, p2, k2):
        v1 = p2 - p1
        v2 = k2 - p1

        dot = np.dot(v1, v2)
        det = v1[0]*v2[1] - v1[1]*v2[0]  

        angle_rad = np.arctan2(det, dot) 
        clockwise_angle = (-angle_rad) % (2 * np.pi)
        return np.degrees(clockwise_angle)
            
    @QtCore.Slot(object)
    def autoUpdateAnchor(self, plotitem_widget: GL3DViewWidget, block=True):
        if block:
            return
        pos_world_z0 = self.mapToParent(self.__geometryPerformance["localRangeQVector"][0])
        pos_world_z1 = self.mapToParent(self.__geometryPerformance["localRangeQVector"][1])
        
        camera_array0 = np.array([pos_world_z0.x(), pos_world_z0.y(), pos_world_z0.z()])
        camera_array1 = np.array([pos_world_z1.x(), pos_world_z1.y(), pos_world_z1.z()])
        
        camera_world = plotitem_widget.cameraPosition()
        camera_world = np.array([camera_world.x(), camera_world.y()])
        
        if self.clockwise_angle(camera_array0[:2], camera_array1[:2], camera_world[:2]) < 180:
            newAnchor = (1, self.style["valuesAnchor"][1])
        else:
            newAnchor = (0, self.style["valuesAnchor"][1])
        
        if self.labelStyle["labelAutoUpdateAnchor"]:
            self.label.setAnchor(newAnchor)
            
        if self.tickStyle["textAutoUpdateAnchor"]:
            if newAnchor != self.style["valuesAnchor"]:
                self.style["valuesAnchor"]=newAnchor
                for text_item_container in self.tickText:
                    for text_item in text_item_container:
                        text_item.setAnchor(newAnchor)

    def linkToView(self, view):
        self._linkToView_internal(view)

    def unlinkFromView(self):
        oldView = self.linkedView()
        self._linkedView = None
        if oldView is not None:
            oldView.sigResized.disconnect(self.linkedViewChanged)
            if self.geometry["axis"] == 0:
                oldView.sigXRangeChanged.disconnect(self.linkedViewChanged)
            elif self.geometry["axis"] == 1:
                oldView.sigYRangeChanged.disconnect(self.linkedViewChanged)
            else:
                oldView.sigZRangeChanged.disconnect(self.linkedViewChanged)

    def linkedView(self) -> GL3DViewBox:
        return None if self._linkedView is None else self._linkedView()

    def setTickFont(self, font: QtGui.QFont | None):
        self.style['tickFont'] = font
        self.picture = None
        #self.prepareGeometryChange()
        self.update()
    
        
    def linkOptimizeAxes(self, childAxis: GL3DViewBox):
        childLineset = childAxis._GLItems["tickLineset"]
        self._GLItems["tickLineset"].linkTickLineset(childLineset)
        childLineset.setFlag(childLineset.GLGraphicsItemFlag.ItemHasNoContents, True)
        childAxis.hide()
        self.update()
        
    @classmethod
    def map_3D_coords_to_2D(cls, view, world_x, world_y, world_z):
        device_pixel_ratio = view.window().screen().devicePixelRatio()
        widget_height = view.height()
        widget_width = view.width()
        
        viewport = GL.glGetIntegerv(GL.GL_VIEWPORT)
        _, _, viewport_width, viewport_height = viewport
        
        modelview = np.array(view.viewMatrix().data()).reshape(4, 4)
        projection = np.array(view.projectionMatrix(viewport,
                                                    (0, 0, device_pixel_ratio * widget_width, device_pixel_ratio * widget_height)
                                                    ).data()
                              ).reshape(4, 4)
        
        px_x, px_y, px_z = GLU.gluProject(world_x, world_y, world_z, modelview, projection, viewport)
        px_x = viewport_width - px_x
        px_y = viewport_height - px_y
        
        return px_x, px_y, px_z

