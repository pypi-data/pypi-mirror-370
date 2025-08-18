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
from OpenGL import GL
from dataclasses import dataclass, field, InitVar, asdict
import weakref
from pyqtgraph.Qt import isQObjectAlive
from pyvol_terminal.gl_3D_graphing.meta import QABCMeta, abc
import pyqtgraph as pg
from pyqtgraph import getConfigOption
from .GL3DTextItem import GL3DTextItem
from .GL3DGraphicsItems import GL3DLinePlotDataItem, GL3DTextItem
from .GL3DGraphicsItemMixin import GL3DGraphicsItemMixin
from .GL3DPlotDataItemMixin import GL3DFlatMeshPlotDataItemMixin
from .GL3DGraphicsItems import MixedGLLinePlotItem
import collections
from . import validationHelpers


import math
from pprint import pprint

from pyqtgraph.Qt import QtGui, QT_LIB
import importlib

if QT_LIB in ["PyQt5", "PySide2"]:
    QtOpenGL = QtGui
else:
    QtOpenGL = importlib.import_module(f"{QT_LIB}.QtOpenGL")



class _TickLineset(MixedGLLinePlotItem):
    def __init__(self,
                 direction: int,
                 baseCoordTicks: List[List[np.ndarray]]=None, 
                 baseCoordGrid: Tuple[np.ndarray, np.ndarray]=None,
                 borderCoordinates:  Tuple[List[float], List[float]]=None,
                 color: Tuple[float, ...]=getConfigOption('foreground'),
                 width: float=1,
                 showGrid: bool=True,
                 showBorder: bool=False,
                 parentItem=None,
                 **kwargs
                 ):
        
        mode = "lines"    # Keep mode lines for optimized painting for grouped line items 
        
        super().__init__(parentItem=parentItem, color=color, width=width, mode=mode, **kwargs)
        self.direction=direction
        self.baseCoordTicks=baseCoordTicks
        self.baseCoordGrid=baseCoordGrid
        self.tickVector=None
        self.gapOffset=None
        self._border_flag=showBorder
        self.border_cells=None
        self.showGrid=showGrid
        self.base_tick_coords: List[List[float]]=None
        self.base_grid_coords: List[List[float]]=None
        self.endGridCoord=0
        
        if self._border_flag:
            self.border_cells = borderCoordinates


    def _paintHelper(self):
        return super()._paintHelper()
    
    def _childPaint(self):
        return opengl.GLLinePlotItem.paint(self)

    
    def childrenBoundingRect(self):...

    def updateTickPositions(self, tickLevelsWorld):
        tick_arr = []
        t_T=None
        tick_pos=None

        for jdx, tick_coords in enumerate(tickLevelsWorld):
            for tick_pos in tick_coords[1]:
                base_tick_offsets = self.baseCoordTicks[jdx].copy()
                t_0 = base_tick_offsets[0].copy()
                t_T = base_tick_offsets[1].copy()
                t_0[self.direction] = tick_pos
                t_T[self.direction] = tick_pos
                
                tick_arr.append(t_0)
                tick_arr.append(t_T)
                
                if self.showGrid:
                    g_0 = self.baseCoordGrid[0].copy()
                    g_T = self.baseCoordGrid[1].copy()
                    g_0[self.direction] = tick_pos
                    g_T[self.direction] = tick_pos
                    tick_arr.append(g_0)
                    tick_arr.append(g_T)
                    
        if self._border_flag:
            tick_arr.append(self.border_cells[0]) 
            tick_arr.append(self.border_cells[1]) 
        

        tick_arr = np.array(tick_arr)   
        self.setData(pos=tick_arr)


class GLAxisTextItem(GL3DTextItem):
  
    def __init__(self,
                 tickLevel: float=None,
                 localPosition: np.ndarray=None,
                 #orientation:int=None, 
                 #offset=None,
                 ref: int=None,
                 parentItem=None, 
                 **kwargs
                 ):        
        
        super().__init__(parentItem=parentItem, **kwargs)
        self._idRef=ref
        self.localPosition=localPosition
        
        self.setTickLevel(tickLevel)
        #self.setOffset(offset)
        
        
    def setTickLevel(self, tickLevel):self._tickLevel=tickLevel
    def setOffset(self, offset):self._offset=offset
    
    def tickLevel(self):return self._tickLevel
    def offset(self):return self._offset
    def idRef(self):return self._idRef
    
    def setPos(selfm, kwargs):
        return kwargs
    
    def scale(self, *args, **kwargs):
        print("scale")
        return super().scale(*args, **kwargs)   
    
    
    def setData1(self, **kwargs):
        if "pos" in kwargs:
            kwargs = self.setPos(kwargs)
        return super().setData(**kwargs)

    
    @QtCore.Slot(object)
    def updateTextVisibilityForItem(self, axis_item: GLAxisItem):
        if self.idRef() is None:
            return
        if self.idRef() > axis_item._currentTicks[self._tickLevel]-1:
            self.hide()
        else:
            self.show()
            

@dataclass(slots=True)
class AxisGeometry:
    axis: int
    origin: np.ndarray[float]
    planeRectSize: np.ndarray[float]
    graphPlaneOffset: np.ndarray[float] | float = field(default=0.) 
    tickLength: float = field(default=0.07)
    planeTickOffset: float = field(default=0.) 
    tickTextOffset: float = field(default=0.)
    tickTextMinWidth: float = field(default=0.25)
    labelOffset: float  = field(default=0.)
    
    planeAxis: int = field(init=False, default=None)
    _Orientation: int = field(init=False, default=False)
    _cachedData: Dict[str, float|np.ndarray] = field(default=dict)
    _bounds: List[Tuple[float, float]] = field(default=list)
    
    def __post_init__(self):
        self._cachedData = {"planeBoundingRect" : None,
                            "tickBoundingRect" : None,
                            "tickTextBoundingRect" : None,
                            "labelPosition" : None,
                            "tickTextPosition" : None}
        
        self.planeAxis = [i for i, val in enumerate(self.planeRectSize) if val != 0 and i != self.axis].pop(0)
        self._Orientation = int(-1 * self.planeRectSize[self.planeAxis] / abs(self.planeRectSize[self.planeAxis]))
        
        if isinstance(self.graphPlaneOffset, float):
            _perpendicular_plane_axis = [i for i in range(3) if i != self.axis and i != self.planeAxis].pop(0)
            planeOffset_new = np.zeros(3)
            planeOffset_new[_perpendicular_plane_axis] = self.graphPlaneOffset
            self.graphPlaneOffset = planeOffset_new
        
        self.planeBoundingRect()
        self.tickBoundingRect()
        self.labelPosition()
        self.getRangeNoLabel()
    
    def Orientation(self): return self._Orientation
    
    def originPosition(self) -> np.ndarray:
        return self.origin
    
    def planePosition(self) -> np.ndarray:
        parent_position = self.originPosition().copy()
        return parent_position + self.graphPlaneOffset
    
    def planeBoundingRect(self) -> np.ndarray:
        if not self._cachedData["planeBoundingRect"] is None:
            return self._cachedData["planeBoundingRect"]
        else:
            self._cachedData["planeBoundingRect"]=np.append(self.planePosition(), self.planeRectSize)
            return self._cachedData["planeBoundingRect"]
        
    def tickBoundingRect(self) -> np.ndarray:
        if not self._cachedData["tickBoundingRect"] is None:
            return self._cachedData["tickBoundingRect"]
        planeBoundingRect = self.planePosition().copy()
        position = planeBoundingRect[:3]
        position[self.planeAxis] += self.compute_offset(1 * self.planeTickOffset)

        size = [0., 0., 0.]
        size[self.axis] = self.planeRectSize[self.axis]
        size[self.planeAxis] = self.compute_offset(self.tickLength)            
        
        self._cachedData["tickBoundingRect"]=np.append(position, size)
        return self._cachedData["tickBoundingRect"]
    
    def tickTextPosition(self):
        if not self._cachedData["tickTextPosition"] is None:
            return self._cachedData["tickTextPosition"]
        
        boundingRect = self.tickBoundingRect().copy()
        boundingRect[self.planeAxis] += boundingRect[3 + self.planeAxis] + self.compute_offset(self.tickTextOffset)
        self._cachedData["tickTextPosition"] = boundingRect[:3]
        return self._cachedData["tickTextPosition"]
    
    def tickTextBoundingRect(self):
        if not self._cachedData["tickTextBoundingRect"] is None:
            return self._cachedData["tickTextBoundingRect"]
        
        size = [0., 0., 0.]
        size[self.axis] = self.planeRectSize[self.axis]
        size[self.planeAxis] = self.compute_offset(self.tickTextMinWidth)
        self._cachedData["tickTextBoundingRect"] = np.append(self.tickTextPosition(), size)
        return self._cachedData["tickTextBoundingRect"]
        
    def labelPosition(self):
        if not self._cachedData["labelPosition"] is None:
            return self._cachedData["labelPosition"]

        parentBoundingRect = self.tickTextBoundingRect()
        position = parentBoundingRect.copy()[:3]
        position[self.axis] += 0.5 * self.planeRectSize[self.axis]
        position[self.planeAxis] += self.compute_offset(self.labelOffset)
        
        self.getRangeNoLabel()
        
        if any(lo <= val <= hi for val, (lo, hi) in zip(position, self._bounds)):
            lim_idx = (self.Orientation() + 1) // 2
            lim = self._bounds[self.planeAxis][lim_idx]
            position = parentBoundingRect.copy()[:3]
            position[self.axis] += 0.5 * self.planeRectSize[self.axis]
            position[self.planeAxis] = lim + self.compute_offset(self.labelOffset)
        self._cachedData["labelPosition"]=position
        return position
    
    def compute_offset(self, offset):
        return self.Orientation() * offset
    
    def getRangeNoLabel(self):
        axis_data_keys = ["planeBoundingRect", "tickBoundingRect", "tickTextBoundingRect"]
        
        lims = [[],[],[]]
        
        for key in axis_data_keys:
            boundingRect = self._cachedData[key]
            for i in range(3):
                lims[i].append(boundingRect[i])
                lims[i].append(boundingRect[i] + boundingRect[3 + i])
        
        self._bounds = [(min(data), max(data)) for data in lims]



class GLAxisItem(GL3DGraphicsItemMixin):
    sigAxisChanged = QtCore.Signal(QtCore.QObject)
    
    
    """
    
    axis indexes are ordered x == 0, y == 1, z == 2
       
    """
    
    def __init__(self,
                 direction: int,
                 origin: Tuple[int, int, int],
                 planeRectSize: Tuple[int, int, int],                 
                 text: str="",
                 labelFont: QtGui.QFont | None=QtGui.QFont("Neue Haas Grotesk", 16),
                 labelColor: str=getConfigOption('foreground'),
                 labelOffset: float=0., 
                 labelResizeToWorld: bool=True,
                 labelAutoUpdateAnchor: bool=None,
                 labelAnchor: Tuple[float, float]=(0.5, 0.5),
                 showLabel: bool=None,
                 valuesFont: QtGui.QFont | None=QtGui.QFont("Neue Haas Grotesk", 10),
                 valuesColor: Tuple[float,...]=getConfigOption('foreground'),
                 tickLength: float=None,
                 ValuesOffset: float=0.01,
                 tickColor: Tuple[float,...]=getConfigOption('foreground'),
                 linkView: GL3DViewBox=None,
                 parentItem=None,
                 maxTickLength=-5,
                 showPlaneBorder: bool=True,
                 showValues: bool=True,
                 planeTickOffset: float=0.,
                 tickTextOffset: float=0.,
                 tickBorderOffset: float=0.1,
                 graphPlaneOffset: float=0.,
                 invertedFromWorld: bool=False,
                 valuesAnchor: Tuple[float, float]=(0., 0.),
                 textResizeToWorld: bool=True,
                 textAutoUpdateAnchor: bool=True,
                 focus: bool=False,
                 showGrid: bool=True,
                 **kwargs
                 ):
        super().__init__(parentItem=parentItem)
        self.flipped=False
        
        self.setFlag(self.GLGraphicsItemFlag.ItemHasNoContents)
        self.setParentItem(parentItem)

        self._nTicksMajor = 6
        
        self._linkedView = None
        self._name=None
        if tickLength is None:
            tickLength = abs([size for ax, size in enumerate(planeRectSize) if ax != direction and size != 0].pop(0)) / 15
        
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
                    "showPlaneBorder"  : showPlaneBorder,
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
                    "showGrid" : showGrid,
                    "focus" : focus
                }
        self.textWidth = 30  ## Keeps track of maximum width / height of tick text
        self.textHeight = 18
        self._currentTicks=[0 for _ in range(self.style["maxTickLevel"] + 1)]
        
        self.transformCondtions = {}
        
        self.offsetStyle = {"graphPlaneOffset" : graphPlaneOffset,
                            "tickBorder" : tickBorderOffset,
                            "ticks" : planeTickOffset,
                           # "tickText" : ValuesOffset,
                            "labelOffsetPlane" : labelOffset,
                            }
    
        self.fixedWidth = None
        self.fixedHeight = None

        self.logMode = False

        self._tickDensity = 1.0   # used to adjust scale the number of automatically generated ticks
        self._tickLevels  = None  # used to override the automatic ticking system with explicit ticks
        self._tickSpacing = None  # used to override default tickSpacing method
        self.scale = 1.0
        self.autoSIPrefix = True
        self.autoSIPrefixScale = 1.0

        self.labelText = ""
        self.labelUnits = ""
        self.labelUnitPrefix = ""
        self._labelItem = None
        self._GLItems = {"values" : None,
                         "ticks" : None, 
                         "tickLineset" : None,
                         "label" : None
                         }
        self._GLItems: Dict[str, GL3DTextItem|GL3DLinePlotDataItem]
        
        self.tickStyle = {"textResizeToWorld" : textResizeToWorld,
                          "valuesAnchor" : valuesAnchor,
                          "textAutoUpdateAnchor" : textAutoUpdateAnchor or valuesAnchor != (0, 0),
                          "showValues" : showValues,
                          'valuesFont': valuesFont,
                          "tickLength" : tickLength,
                          }
        self._siPrefixEnableRanges = None
        
        
        
        
        
        showLabel = False
        
        self._axisGeometry = AxisGeometry(axis=direction,
                                           origin=np.array(origin),
                                           planeRectSize=np.array(planeRectSize),
                                           graphPlaneOffset=graphPlaneOffset,
                                           tickLength=tickLength,
                                 #          planeTickOffset=planeTickOffset,
                                           tickTextOffset=tickTextOffset,
                                           labelOffset=labelOffset,
                                           )        
        showLabel = showLabel if not bool(text) is None else showValues
        labelAutoUpdateAnchor = showLabel and (labelAutoUpdateAnchor or labelAnchor != (0, 0))
        self.labelStyle = {"labelText" : text,
                           "labelColor" : labelColor or getConfigOption('foreground'),
                           "labelFont" : labelFont,
                           "labelAnchor" : labelAnchor,
                           "labelAutoUpdateAnchor" : labelAutoUpdateAnchor,
                           "labelResizeToWorld" : labelResizeToWorld,
                           "labelOffsetPlane" : labelOffset,
                           "showLabel" : showLabel,
                           }
        
        self._baseTickWorldCoords = None
        


        self._GLItems["planeBorder"] = self._initPlaneRectBorderItem()
        self._GLItems["text"] = self._initValueTextItems()
        self._GLItems["label"] = self._initLabelTextItem()
        self._GLItems["tickLineset"]= self._initTickItems()
        
        self.setRange(self._axisGeometry.originPosition()[self.axisDirection()], self._axisGeometry.originPosition()[self.axisDirection()] + self._axisGeometry.planeRectSize[self.axisDirection()])
        self.setLabel(**self.labelStyle)

        self._linkedView = None
        
        if linkView is not None:
            self._linkToView_internal(linkView)
            
        self.setTickStyle(valuesColor=valuesColor,
                          valuesFont=QtGui.QFont("Neue Haas Grotesk", 10),
                          valuesAnchor=self.style["valuesAnchor"],
                          )
        
        
        self._buildOptimizers()
        
        print(f"origin: {self._axisGeometry.originPosition()}")
        if direction == 2 and planeRectSize[1] != 0:
            print(planeRectSize)
            import sys 
            sys.exit()
            
        
        
    def _setViewBoxRange(self, viewBoxRange):
        self.viewBoxRange=viewBoxRange
        
    def _setDataHelper(self):...
    def clipDataFromVRange(self):...
    
    @classmethod
    def fromViewBoxRange(cls,
                         viewRange: list[list[float]] | Dict[str, list[float]],   # limits of the viewBox in world coordinates [[x_min, x_max], [y_min, y_max], [z_min, z_max]] or {"x" : [x_min, x_max], "y" : [y_min, y_max], "z" : [z_min, z_max]}
                         direction: str | int,
                         origin: Tuple[int, int, int]|Dict[str, int]=None, #    extremum values must be either 0 or 1, and orients the axis origin in world coordinates. {"x" : int, "y" : int ,..} or (int, int ,int)
                         planeDirection: str | int | None = None,         # planeDirection is the direction that shares the rectangular-plane with the axis-direction along the viewRange. e.g. for the unit-cube with direction==x planeDirection==y for the xy plane
                         **kwargs
                         ) -> 'GLAxisItem':
        planeDirection = validationHelpers.verifyPlaneDirection(direction, planeDirection)
        direction_size = [d - origin[direction] for d in viewRange[direction] if d != origin[direction]][0]
        planeDirection_size = [d - origin[planeDirection] for d in viewRange[planeDirection] if d != origin[planeDirection]][0]
        
        planeRectSize = [0, 0, 0]
        planeRectSize[direction] = direction_size
        planeRectSize[planeDirection] = planeDirection_size

        axisItem  = cls(direction=direction,
                        origin=origin,
                        planeRectSize=planeRectSize,
                        
                        planeDirection=planeDirection,
                        **kwargs)    
        return axisItem
    
    def _initPlaneRectBorderItem(self) -> opengl.GLLinePlotItem:
        planeBoundingRect = self._axisGeometry.planeBoundingRect()
        
        p1 = planeBoundingRect[:3]
        p2 = p1.copy()
        p2[self.axisDirection()] += planeBoundingRect[3 + self.axisDirection()]
        
        p3 = p1.copy()
        p3 += planeBoundingRect[3:]
        
        p4 = p1.copy()
        p4[self._axisGeometry.planeAxis] += planeBoundingRect[3 + self._axisGeometry.planeAxis]
        
        segments = [p1, p2, p2, p3, p3, p4, p4, p1]
        
        borderline = MixedGLLinePlotItem(pos=segments,
                                            color= self.style["tickColor"],
                                            glOptions="translucent",
                                            mode="lines",
                                            )
        borderline.setParentItem(self)
        return borderline
    

    

    def _validate_kwargs(self, direction, orthoCoords, perpendicular_axis, viewBoxRange):

        c_viewBoxRange = viewBoxRange.copy() if isinstance(viewBoxRange, list) else viewBoxRange.tolist().copy()
        _ = c_viewBoxRange.pop(direction)
        orthoCoords = list(orthoCoords)
        if not all(orthoCoords[idx] in ax for idx, ax in enumerate(c_viewBoxRange)):
            raise ValueError("Orthogonal Coordinates do not match the viewBox range")



    def _childPaint(self):...
    def _paintHelper(self):... 

      
    def _initValueTextItems(self) -> List[List[GLAxisTextItem]]:
        gl_objects_level = []
        idx=0
        
        tickTextPosition = self._axisGeometry.tickTextPosition() + self.style["tickTextOffset"]
        for jdx in range(self.style["maxTextLevel"] + 1):
            gl_objects = []
            for idx in range(self.style["maxNticksperLevel"]):
                localPosition = tickTextPosition.copy()
                gl_object = GLAxisTextItem(tickLevel=jdx,
                                           localPosition=localPosition,
                                           ref=idx,
                                           anchor=self.tickStyle["valuesAnchor"],
                                           font=self.tickStyle["valuesFont"], 
                                           resizeToWorld=True
                                           )
                gl_object.setParentItem(self)
                gl_object.hide()
                self.sigAxisChanged.connect(gl_object.updateTextVisibilityForItem)
                gl_objects.append(gl_object)
                idx+=1
            gl_objects_level.append(gl_objects)
        return gl_objects_level





    def axisDirection(self):
        return self._axisGeometry.axis
                
    
    def tickText(self, minVal:float, maxVal:float, size: float):
        minVal, maxVal = sorted((minVal, maxVal))

        minVal *= self.scale
        maxVal *= self.scale

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
            values = (np.arange(num) * spacing + start) / self.scale
            ## remove any ticks that were present in higher levels
            ## we assume here that if the difference between a tick value and a previously seen tick value
            ## is less than spacing/100, then they are 'equal' and we can ignore the new tick.
            close = np.any(
                np.isclose(
                    allValues,
                    values[:, np.newaxis],
                    rtol=0,
                    atol=spacing/self.scale*0.01
                ),
                axis=-1
            )
            values = values[~close]
            allValues = np.concatenate([allValues, values])
            ticks.append((spacing/self.scale, values.tolist()))
            ticksWorld.append((self.getWorldCoord(spacing/self.scale), self.getWorldCoord(values).tolist()))
            self._currentTicks[i] = len(values.tolist())
        return ticks, ticksWorld

    def updateText(self, tickLevels, tickLevelsWorld):
        
        for jdx, (ticks, ticksWorld) in enumerate(zip(tickLevels, tickLevelsWorld)):
            for idx, (tick, tickWorld) in enumerate(zip(ticks[1], ticksWorld[1])):
                text_item=self._GLItems["text"][jdx][idx]
                text_item.localPosition[self.axisDirection()] = tickWorld
                text_item.blockUpdates(True)
                text_item.setData(pos=text_item.localPosition, text=str(round(tick,2)))
                text_item.blockUpdates(False)
                

  
    def setRange(self, mn: float, mx: float):
        self.range = [mn, mx]
        tickLevels, tickLevelsWorld = self.tickText(*self.range, 1)
        if self.style["showValues"]:
            self.updateText(tickLevels, tickLevelsWorld)
        self._GLItems["tickLineset"].updateTickPositions(tickLevelsWorld)
        self.update()
        
    def setTextFont(self, font=None):
        if font is None:
            getConfigOption("foreground")
            
    def setLabel(
                self,
                labelText: str | None=None,
                labelColor: str | None=None,
                labelFont: str | None=None,
                labelAnchor: str=None,
                labelResizeToWorld: bool=None,
                labelAutoUpdateAnchor: bool=None,
                showLabel: bool=None,
                **kwargs):  
        
        
        if not labelText is None:
            
            
            self.labelStyle["labelText"] = labelText
        
        visible = bool(self.labelStyle["labelText"])
        if visible:
            self._GLItems["label"].setData(text=self.labelStyle["labelText"])
        else:
            self._GLItems["label"].setData(text="")
        if not showLabel is None:
            if showLabel and not visible:
                raise
            
        self.showLabel(visible)
        
        del kwargs["labelOffsetPlane"]

        if not labelColor is None:
            self.labelStyle["labelColor"] = labelColor
        if not labelFont is None:
            self.labelStyle["labelFont"] = labelFont
        if not labelAnchor is None:
            self.labelStyle["labelAnchor"] = labelAnchor
        if not labelResizeToWorld is None:
            self.labelStyle["labelResizeToWorld"] = labelResizeToWorld and visible
            self.labelStyle["labelText"]
        
        if not labelAutoUpdateAnchor is None:
            self.labelStyle["labelAutoUpdateAnchor"] = (labelAutoUpdateAnchor or labelAnchor != (0, 0)) and visible
        
        kwargs = {"resizeToWorld" : self.labelStyle["labelResizeToWorld"],
                  "text" : self.labelStyle["labelText"],
                  "color" : self.labelStyle["labelColor"],
                  "font" : self.labelStyle["labelFont"],
             #     "anchor" : self.labelStyle["labelAnchor"],
                  }
        
        self._GLItems["label"].setData(**kwargs)
    
    def originPosition(self):
        return self._axisGeometry.originPosition()
    
    def planeAxes(self):
        axes = [self._axisGeometry.axis, self._axisGeometry.planeAxis]
        axes.sort()
        return axes
    
    def showLabel(self, show: bool=True):
        if show:
            self._GLItems["label"].show()
        else:
            self._GLItems["label"].hide()
    
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
                for tick_level in self._GLItems["text"]:
                    for item in tick_level:
                        item.setData(font=self.tickStyle["valuesFont"])
    
    def _initLabelTextItem(self) -> GLAxisTextItem:
        
        pos = np.zeros(3)
        pos[self.axisDirection()] = 1
        orientation = self._axisGeometry.Orientation()
        pos[self._axisGeometry.planeAxis] = 0.75 * self._axisGeometry.Orientation()
        labeItem = GLAxisTextItem(localPosition=self._axisGeometry.labelPosition(),
                                  pos=pos,#self._axisGeometry.labelPosition(),
                                  anchor=self.labelStyle["labelAnchor"],
                                  font=self.labelStyle["labelFont"], 
                                  )
        labeItem.setParentItem(self)
        return labeItem
        
    

    def _initTickItems(self) -> _TickLineset:
        
        
        ticksBoundingRect = self._axisGeometry.tickBoundingRect()
        
        
        tick_pos_container = []
        
        
        
        for idx in range(self.style["maxTickLevel"] + 1):
            
            tickStart = ticksBoundingRect[:3]
            tickEnd = tickStart.copy() + ticksBoundingRect[3:] / (1+idx)
            
            
            tick_coords = [tickStart, tickEnd]
            tick_pos_container.append(tick_coords)
            

        gridStart = self._axisGeometry.originPosition().copy()        
        
        
        
        axisBoundingRect = self._axisGeometry.planeBoundingRect()
        
        gridStart = axisBoundingRect[:3]
        
        gridEnd = axisBoundingRect[:3] + axisBoundingRect[3:]
            
        
        
        gridPositions = (gridStart.tolist().copy(), gridEnd.tolist().copy())

        
        
        start = self._axisGeometry.tickBoundingRect()[:3]
        end = start.copy()
        end[self.axisDirection()] = self._axisGeometry.tickBoundingRect()[3 + self.axisDirection()]

        
        borderPositions = [start.tolist(), end.tolist()]
        

        tickItem = _TickLineset(self.axisDirection(),
                               baseCoordTicks=tick_pos_container,
                               baseCoordGrid=gridPositions,
                               borderCoordinates=borderPositions,
                               glOptions="translucent",
                               antialias=True,
                               color=self.style["tickColor"],
                               width=self.style["tickWidth"][0],
                               showGrid=self.style["showGrid"],
                               showBorder=self.style["showPlaneBorder"],
                               )
        tickItem.setParentItem(self)
        return tickItem
        
    def checkWidths(self, textNum: str):...
    
    @QtCore.Slot(object)
    @QtCore.Slot(object, object)
    def linkedViewChanged(self, view: GL3DViewBox, newRange=None):
        if newRange is None:
            newRange = view.viewRange()[self.axisDirection()]
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

    def getWorldCoord(self, value):
        view = self.linkedView()
        if view is None:
            world_bounds = 0, 1
        else:
            world_bounds = view.state["worldRange"][self.axisDirection()]

        dif = self.range[1] - self.range[0]
        rmin, rmax = self.range
        if rmax == rmin:
            scale = 1
            offset = 0
            value
        else:
            scale = (world_bounds[1] - world_bounds[0]) / dif
            offset = world_bounds[0] - rmin * scale
        return scale * value + offset
    
    def labelString(self):
        return self.labelStyle["labelText"]
        
    def _linkToView_internal(self, view: GL3DViewBox):
        self.unlinkFromView()
        self._linkedView = weakref.ref(view)

        self._setViewBoxRange(view.state["worldRange"])
        
        if self.axisDirection() == 0:
            view.sigXRangeChanged.connect(self.linkedViewChanged)
        elif self.axisDirection() == 1:
            view.sigYRangeChanged.connect(self.linkedViewChanged)
        else:
            view.sigZRangeChanged.connect(self.linkedViewChanged)
        view.sigResized.connect(self.linkedViewChanged)
        if isinstance(view.parentWidget(), GLViewWidget):
            plotitem_widget = view.parentWidget()
                        
            if self.tickStyle["textAutoUpdateAnchor"] or self.labelStyle["labelAutoUpdateAnchor"]:
                    plotitem_widget.sigViewAngleChanged.connect(self.autoUpateAnchor)
                    self.autoUpateAnchor(plotitem_widget)
            if self.style["focus"]:
                plotitem_widget.sigViewAngleChanged.connect(self.updateFocusParameters)
           
    
    
    @QtCore.Slot(object)
    def updateFocusParameters(self, plotitem_widget: GL3DViewWidget):
        cameraPosition = plotitem_widget.cameraTuple()
        if self.axisDirection() == 2:
            angle = self.style["planeToCameraFn"](cameraPosition)
            #print(f"angle: {math.degrees(angle)}")
            
            
            
            
            return 

        current_angle = self.transformCondtions["azimuth"]["current"](cameraPosition)
        next_angle = self.transformCondtions["azimuth"]["next"](cameraPosition)
        """
        print("")
        print(self.axisDirection())

        print(f"current_angle: {math.degrees(current_angle)}")
        print(f"next_angle: {math.degrees(next_angle)}")
        """
        

        if self._axisGeometry.planeRectSize[2] == 0:
            if plotitem_widget.vb.worldRange():
                pass
        
        if current_angle > math.pi and next_angle < math.pi:
            self.flipAxis()
        
        
        
        
        if not 2 in (self.axisDirection(), self._axisGeometry.planeAxis):
            if cameraPosition[2] < self._axisGeometry.originPosition()[2]:
                if self.visible():
                    print(f"\nhiding:\n")
                    print(f"elevation: {plotitem_widget.opts['elevation']}")
                    print(f"angle: {math.degrees(current_angle)}")
                    print(f"cameraPosition: {cameraPosition}")

                    print(f"self._axisGeometry.originPosition()[2]: {self._axisGeometry.originPosition()[2]}")
                    self.hide()
            else:
                if not self.visible():
                    print(f"\nshowing:\n")
                    print(f"elevation: {plotitem_widget.opts['elevation']}")
                    print(f"angle: {math.degrees(current_angle)}")
                    print(f"cameraPosition: {cameraPosition}")

                    print(f"self._axisGeometry.originPosition()[2]: {self._axisGeometry.originPosition()[2]}")

                    self.show()
                
    def flipAxis(self):
        

        midPoint = self._axisGeometry.originPosition().copy() 
        midPoint[self._axisGeometry.planeAxis] += 0.5 * self._axisGeometry.planeRectSize[self._axisGeometry.planeAxis]
        
                
        
        tr = pg.Transform3D()
        tr.translate(*midPoint)

        scales = [1, 1, 1]
        scales[self._axisGeometry.planeAxis] *= -1
        
        tr.scale(*scales)
        tr.translate(*(-1 * midPoint))
        
        
        
        next = self.transformCondtions["azimuth"]["current"]
        current  = self.transformCondtions["azimuth"]["next"]
        
        
        self.transformCondtions["azimuth"]["next"]= next
        self.transformCondtions["azimuth"]["current"] = current
        
        
        self.setTransform(tr)
        

        """
        change[self.axisDirection()] = self._axisGeometry.planeRectSize[self.axisDirection()]
        self._GLItems["tickLineset"].translate(*change)
        """
        
    
        
    
    @QtCore.Slot(object)
    def autoUpateAnchor(self, plotitem_widget: GL3DViewWidget):
        
        cameraPosition = plotitem_widget.cameraTuple()
        
        if math.pi > self.style["planeToCameraFn"](cameraPosition):
            newAnchor = (1, self.style["valuesAnchor"][1])
        else:
            newAnchor = (0, self.style["valuesAnchor"][1])
        
        if self.labelStyle["labelAutoUpdateAnchor"]:
            self._GLItems["label"].setAnchor(newAnchor)
            
        if self.tickStyle["textAutoUpdateAnchor"]:
            if newAnchor != self.style["valuesAnchor"]:
                self.style["valuesAnchor"]=newAnchor
                for text_item_container in self._GLItems["text"]:
                    for text_item in text_item_container:
                        text_item.setAnchor(newAnchor)
                        
        if self.axisDirection() == 0:
            for text_item_container in self._GLItems["text"]:
                for text_item in text_item_container:
                    print("")
                    #print(cameraPosition)
                    #print(text_item.anchor())
                    print(self._axisGeometry.originPosition())
                    print(self.mapToParent(self._axisGeometry.originPosition()))
                    print(self.mapFromParent(self._axisGeometry.originPosition()))


    def linkToView(self, view):
        self._linkToView_internal(view)

    def unlinkFromView(self):
        oldView = self.linkedView()
        self._linkedView = None
        if oldView is not None:
            oldView.sigResized.disconnect(self.linkedViewChanged)
            if self.axisDirection() == 0:
                oldView.sigXRangeChanged.disconnect(self.linkedViewChanged)
            elif self.axisDirection() == 1:
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


    def _buildOptimizers(self):
        self.style["textAnchorVar"] = tuple([int(val / abs(val)) if idx != self._axisGeometry.axis and val != 0 else 0 for idx, val in enumerate(self._axisGeometry.planeRectSize[:2])])
        planeRectSize = self._axisGeometry.planeRectSize.copy()[:2]
        textPositionOrigin = self._axisGeometry.tickTextPosition()
        planeLength = [int(val) if idx == self._axisGeometry.planeAxis else 0 for idx, val in enumerate(planeRectSize)]
        
        if planeLength[0] > 0 and planeLength[1] == 0:
            anchorCondition = lambda camera: (-1 * math.atan2(camera[1] - textPositionOrigin[1], camera[0] - textPositionOrigin[0])) % (2 * math.pi)
        elif planeLength[0] < 0 and planeLength[1] == 0:
            anchorCondition = lambda camera: (-1 * math.atan2(-(camera[1] - textPositionOrigin[1]), -(camera[0] - textPositionOrigin[0]))) % (2 * math.pi) 
        elif planeLength[0] == 0 and planeLength[1] > 0:
            anchorCondition = lambda camera: (-1 * math.atan2(-(camera[0] - textPositionOrigin[0]), camera[1] - textPositionOrigin[1])) % (2 * math.pi)
        elif planeLength[0] == 0 and planeLength[1] < 0:
            anchorCondition = lambda camera: (-1 * math.atan2(camera[0] - textPositionOrigin[0], -(camera[1] - textPositionOrigin[1]))) % (2 * math.pi)
        
        self.style["planeToCameraFn"] = anchorCondition
        
        if self.style["focus"]:
            if self.axisDirection() != 2:
            
                self.transformCondtions["azimuth"] = {"current" : None,
                                                       "next" : None}            
                def create_anchor_condition(plane_rect_size, axis_origin_position, axis_direction):
                    axis_length = [int(val) if idx == axis_direction else 0 for idx, val in enumerate(plane_rect_size)]
                    print(axis_length)
                    
                    if axis_length[0] > 0 and axis_length[1] == 0:
                        return lambda camera: (-1 * math.atan2(camera[1] - axis_origin_position[1], camera[0] - axis_origin_position[0])) % (2 * math.pi)
                    elif axis_length[0] < 0 and axis_length[1] == 0:
                        return lambda camera: (-1 * math.atan2(-(camera[1] - axis_origin_position[1]), -(camera[0] - axis_origin_position[0]))) % (2 * math.pi)
                    elif axis_length[0] == 0 and axis_length[1] > 0:
                        return lambda camera: (-1 * math.atan2(-(camera[0] - axis_origin_position[0]), camera[1] - axis_origin_position[1])) % (2 * math.pi)
                    elif axis_length[0] == 0 and axis_length[1] < 0:
                        return lambda camera: (-1 * math.atan2(camera[0] - axis_origin_position[0], -(camera[1] - axis_origin_position[1]))) % (2 * math.pi)
                
                plane_rect_size = self._axisGeometry.planeRectSize.copy()
                axis_origin_position = self._axisGeometry.originPosition().copy()
                self.transformCondtions["azimuth"]["current"] = create_anchor_condition(plane_rect_size, axis_origin_position, self.axisDirection())
                plane_rect_size = self._axisGeometry.planeRectSize.copy()
                axis_origin_position = self._axisGeometry.originPosition().copy() + plane_rect_size
                plane_rect_size*= -1
                self.transformCondtions["azimuth"]["next"] = create_anchor_condition(plane_rect_size, axis_origin_position, self.axisDirection())  
            else:
                plane_rect_size = self._axisGeometry.planeRectSize.copy()
                axis_origin_position = self._axisGeometry.originPosition().copy()
                axis_length = [int(val) if idx == self._axisGeometry.planeAxis else 0 for idx, val in enumerate(plane_rect_size)]
                print(axis_length)

    @classmethod
    def createFocusSet(cls, viewRange, **kwargs):
        pass