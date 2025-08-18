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




class _TickLineset(opengl.GLLinePlotItem):
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
                 local_position: np.ndarray=None,
                 ref: int=None,
                 parentItem=None, 
                 **kwargs
                 ):        
        super().__init__(parentItem=parentItem, **kwargs)

        self._idRef=ref
        self._tickLevel=tickLevel
        self.local_position=local_position
        
    def setTickLevel(self, tickLevel):
        self._tickLevel=tickLevel

    def idRef(self):
        return self._idRef

    @QtCore.Slot(object)
    def updateTextVisibilityForItem(self, axis_item: GLAxisItem):
        if self.idRef() is None:
            return
        if self.idRef() > axis_item._currentTicks[self._tickLevel]-1:
            self.hide()
        else:
            self.show()
            
    def tickLevel(self): return self._tickLevel



@dataclass(kw_only=True)
class ObjectPosition:
    name: str = field(default=None)
    pos: InitVar[np.ndarray] = field(default=None)
    offset: InitVar[Dict[str, float]] = field(default=None)
    parent: InitVar[ObjectPosition|None] = field(default=None)    
    
    _offset: np.ndarray = field(init=False, default=None)
    _pos: np.ndarray = field(init=False, default=None)
    _position: np.ndarray = field(init=False, default=None)
    _localPosition: np.ndarray = field(init=False, default=None)
    _parent: ObjectPosition = field(init=False, default=None)

    _children: List[ObjectPosition] = field(default_factory=list)
    
    def __post_init__(self, pos, offset, parent):
        if pos is None:
            pos = np.zeros(3, dtype=float)
        if offset is None:
            offset = np.zeros(3, dtype=float)

        self.setOffset(offset)
        self.setPos(pos)
        self.setLocalPosition(self._pos + self._offset)
        self._children = []
        
        self.setParent(parent)  
        if self.name == "tickBorder":
            pprint(self)

    def children(self):
        return self._children
    
    def getParent(self):
        return self._parent
    
    def getPosition(self):
        return self._position

    def setPosition(self, value):
        self._position=value
    
    def getLocalPosition(self):
        return self._localPosition
    
    def setLocalPosition(self, value):
        self._localPosition=value

    def getPos(self):
        return self._pos
    
    def setPos(self, pos):
        self._pos = pos
        self.update()
        
    def setOffset(self, offset):
        self._offset=offset
        
    def update(self):
        self.setLocalPosition(self.getPos() + self.getOffset())
        print(self.name)
        print(self.getParent())
        self.setPosition(self.getLocalPosition() + (self.getParent().getPosition() if self.getParent() else 0))
        for child in self._children:
            child.update()
    
    def getOffset(self):
        return self._offset
    
    def setParent(self, parent: 'ObjectPosition'=None):
        if parent == self.parent:
            return 
        
        if self.getParent() is not None:
            self.getParent().children().remove(self)
            parent.children().append(self)
        
        self._parent = parent
        
        
        
        self.update()    
        
        
    def diff(self, offset_container):
        return self.getPosition() - offset_container.getPosition()
        
        
    
    @classmethod
    def fromParent(cls, kwargs, parent=None):
        offset_container = cls(**kwargs)
        offset_container.setParent(parent)    
        return offset_container
    
        


class GLAxisItem(GL3DGraphicsItemMixin):
    sigAxisChanged = QtCore.Signal(QtCore.QObject)
    
    
    """
    
    axis indexes are ordered x == 0, y == 1, z == 2
       
    
    
    """
    
    def __init__(self,
                 direction: int,
                 origin: Tuple[int, int, int],
                 planeCorner: Tuple[int, int, int],
                 orthogonalVertices: Dict[str, Tuple[float, float, float]]=None,
                 
                 planeDirection: int=1,
                 text: str="",
                 labelFont: QtGui.QFont | None=QtGui.QFont("Neue Haas Grotesk", 16),
                 labelColor: str=getConfigOption('foreground'),
                 labelOffsetPlane: float=0.3, 
                 labelOffsetDirection: float=0., 
                 labelResizeToWorld: bool=True,
                 labelAutoUpdateAnchor: bool=None,
                 labelAnchor: Tuple[float, float]=(0.5, 0.5),
                 showLabel: bool=None,
                 valuesFont: QtGui.QFont | None=QtGui.QFont("Neue Haas Grotesk", 10),
                 valuesColor: Tuple[float,...]=getConfigOption('foreground'),
                 tickLength: float=0.07,
                 ValuesOffset: float=0.01,
                 tickColor: Tuple[float,...]=getConfigOption('foreground'),
                 linkView: GL3DViewBox=None,
                 parentItem=None,
                 maxTickLength=-5,
                 showPlaneBorder: bool=True,
                 showValues: bool=True,
                 tickOffset: float=0.,
                 tickBorderOffset: float=0.1,
                 planeOffset: float=1.,
                 invertedFromWorld: bool=False,
                 autoValueAnchor: bool=True,
                 valuesAnchor: Tuple[float, float]=(0., 0.),
                 valuesResizeToWorld: bool=True,
                 valuesAutoUpdateAnchor: bool=True,
                 showGrid: bool=True,
                 **kwargs
                 ):
        super().__init__(parentItem=parentItem)
      
        
        self.setFlag(self.GLGraphicsItemFlag.ItemHasNoContents)
        self.setParentItem(parentItem)

        self._nTicksMajor = 6
        
        self._linkedView = None
        self._name=None
        
        self.style = {
                    'tickTextOffset': [5, 2],  ## (horizontal, vertical) spacing between text and axis
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
                    "autoValueAnchor" : autoValueAnchor,
                    "showGrid" : showGrid,
                }
        self.textWidth = 30  ## Keeps track of maximum width / height of tick text
        self.textHeight = 18
        self._currentTicks=[0 for _ in range(self.style["maxTickLevel"] + 1)]
        
        self.offsetStyle = {"planeOffset" : planeOffset,
                            "tickBorder" : tickBorderOffset,
                            "ticks" : tickOffset,
                            "tickValues" : ValuesOffset,
                            "labelOffsetPlane" : labelOffsetPlane,
                            "labelOffsetDirection" : labelOffsetDirection,
                            }
        
        
        self.ObjectPositionContainer = {
                                }
        
        self.offsetVectors =  {"planeOffset" : None,
                               "tickBorder" : None,
                               "ticks" : None,
                               "tickValues" : None,
                               "labelOffsetPlane" : None,
                               "labelOffsetDirection" : None,
                               }
        
        self._baseGeometry = {"direction" : direction,
                              "orthogonalVertices" : orthogonalVertices,
                              "origin" : np.array(origin),
                              "planeCorner" : np.array(planeCorner),
                              "gridPlaneCoordinates" : None,
                              "grid_f" : None,
                              "borderCoordinates" : None,
                              "planeOrientation" : [None, None],
                             "ticks" : [],
                             "tickValues" : None,     
                             "planeDirection" : None,
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
        
        self.tickStyle = {"valuesResizeToWorld" : valuesResizeToWorld,
                          "valuesAnchor" : valuesAnchor,
                          "valuesAutoUpdateAnchor" : valuesAutoUpdateAnchor or valuesAnchor != (0, 0),
                          "showValues" : showValues,
                          'valuesFont': valuesFont,
                          "tickLength" : tickLength,
                          
                          }
        self._siPrefixEnableRanges = None
        
        
        showLabel = False
        
        
        showLabel = showLabel if not bool(text) is None else showValues
        labelAutoUpdateAnchor = showLabel and (labelAutoUpdateAnchor or labelAnchor != (0, 0))
        self.labelStyle = {"labelText" : text,
                           "labelColor" : labelColor or getConfigOption('foreground'),
                           "labelFont" : labelFont,
                           "labelAnchor" : labelAnchor,
                           "labelAutoUpdateAnchor" : labelAutoUpdateAnchor,
                           "labelResizeToWorld" : labelResizeToWorld,
                           "labelOffsetPlane" : labelOffsetPlane,
                           "labelOffsetDirection" : labelOffsetDirection,
                           "showLabel" : showLabel,
                           }
        
        self._baseTickWorldCoords = None
        
        self._buildBaseCoords()
        
        self._GLItems["planeBorder"] = self._buildPlaneBorderCoordinates()
        self._GLItems["values"] = self._initValueTextItems()
        self._GLItems["label"] = self._initLabelTextItem()
        self._GLItems["tickLineset"]= self._initTickItems()
        
        self.setRange(self._baseGeometry["origin"][0], self._baseGeometry["orthogonalVertices"]["direction"][0])
        self.setLabel(**self.labelStyle)

        self._linkedView = None
        
        if linkView is not None:
            self._linkToView_internal(linkView)
            
        self.setTickStyle(valuesColor=valuesColor,
                          valuesFont=QtGui.QFont("Neue Haas Grotesk", 10),
                          valuesAnchor=self.style["valuesAnchor"],
                          )
    def _setViewBoxRange(self, viewBoxRange):
        self.viewBoxRange=viewBoxRange
    def _setDataHelper(self):...
        
    def setData(self):...
    def clipDataFromVRange(self):...

    def _buildPlaneBorderCoordinates(self) -> opengl.GLLinePlotItem:
        p1 = self._baseGeometry["origin"].copy()
        p2 = self._baseGeometry["origin"].copy()
        p2[self.axisDirection()] = self._baseGeometry["planeCorner"][self.axisDirection()]
        
        p4 = self._baseGeometry["origin"].copy()
        p4[self._baseGeometry["planeDirection"]] = self._baseGeometry["planeCorner"][self._baseGeometry["planeDirection"]]
        p3 = self._baseGeometry["planeCorner"]
        
        segments = sum([[a, b] for a, b in zip([p1, p2, p3, p4], [p2, p3, p4, p1])], [])
        
        borderline = opengl.GLLinePlotItem(pos=segments,
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

    
    @classmethod
    def fromViewBoxRange(cls,
                         viewRange: list[list[float]] | Dict[str, list[float]],   # limits of the viewBox in world coordinates [[x_min, x_max], [y_min, y_max], [z_min, z_max]] or {"x" : [x_min, x_max], "y" : [y_min, y_max], "z" : [z_min, z_max]}
                         direction: str | int,
                         extremums: Tuple[int, int, int]|Dict[str, int]=None, #    extremum values must be either 0 or 1, and orients the axis origin in world coordinates. {"x" : int, "y" : int ,..} or (int, int ,int)
                         planeDirection: str | int | None = None,         # planeDirection is the direction that shares the rectangular-plane with the axis-direction along the viewRange. e.g. for the unit-cube with direction==x planeDirection==y for the xy plane
                         **kwargs
                         ) -> 'GLAxisItem':
        
        if planeDirection is None or extremums is None:
            raise ValueError(f"If axisVertexPoints is None, planeDirection and extremums needs to be provided")
        else:
            planeDirection = validationHelpers.verifyPlaneDirection(direction, planeDirection)
            extremums = validationHelpers.verifyExtrumums(extremums)
            perpendicularDirection = np.delete([0, 1, 2], [direction, planeDirection]).item()
            
            axisOrigin = [None, None, None]
            
            for idx, ext in enumerate(extremums):
                axisOrigin[idx] = viewRange[idx][ext]

            directionVertex = axisOrigin.copy()
            extremum_idx = extremums[direction]
            
            directionVertex[direction] = viewRange[direction][1-extremum_idx]

            planeVertex = axisOrigin.copy()
            
            orthogonal_extremum_idx = 1 - extremums[planeDirection]
            
            planeVertex[planeDirection] = viewRange[planeDirection][orthogonal_extremum_idx]
            
            perpendicularVertex = axisOrigin.copy()
            orthogonal_extremum_idx = 1 - extremums[perpendicularDirection]
            perpendicularVertex[perpendicularDirection] = viewRange[perpendicularDirection][orthogonal_extremum_idx]

            orthogonalVertices = {"direction" : directionVertex,
                                  "planeDirection" : planeVertex,
                            #      "perpendicularDirection" : perpendicularVertex
                                  }
            
            planeDimensions = [0, 0, 0]
            
            planeDimensions[direction] = directionVertex[direction] - axisOrigin[direction]
            planeDimensions[planeDirection] = planeVertex[planeDirection] - axisOrigin[planeDirection]
            
            offset_mag = 0.15
            
            
            if "planeOffset" in kwargs:
                planeOffset = 3*[0]
                planeOffset[perpendicularDirection] = -1 * offset_mag * viewRange[perpendicularDirection][orthogonal_extremum_idx] / abs(viewRange[perpendicularDirection][orthogonal_extremum_idx])
                kwargs["planeOffset"] = planeOffset

            axisItem  = cls(direction=direction,
                            origin=axisOrigin,
                            planeCorner=planeDimensions,
                            orthogonalVertices=orthogonalVertices,
                            planeDirection=planeDirection,
                            **kwargs
                            )    

            return axisItem

    def _childPaint(self):...
    def _paintHelper(self):... 

    def _buildLabelBaseCoordinates(self):        
        midPoint = np.zeros(3)
        
        midPoint_ax_dir = 0.5 * (self._baseGeometry["planeCorner"][self.axisDirection()] + self._baseGeometry["origin"][self.axisDirection()])
        midPoint[self.axisDirection()] = midPoint_ax_dir
        #midPoint[self.axisDirection()] = 0.5 * (self._baseGeometry["origin"][self.axisDirection()] + orthogonalVertices["direction"][self.axisDirection()])
        
        offset = -1*self._baseGeometry["planeOrientation"][self._baseGeometry["planeDirection"]] * self.offsetStyle["labelOffsetPlane"]
        offset_arr = np.zeros(3)
        offset_arr[self._baseGeometry["planeDirection"]]=offset
        kwargs = {"name":"label",
                  "pos":midPoint,
                  "offset" : offset_arr
                  }
        
        self.ObjectPositionContainer["label"] = ObjectPosition.fromParent(kwargs,
                                                                            parent=self.ObjectPositionContainer["tickEnd"][0])        

        self._baseGeometry["label"] = self.ObjectPositionContainer["label"].getPosition()
        
        
    def _buildGridBaseCoordinates(self):
        gridStart = self._baseGeometry["origin"].copy()        
        kwargs = {"name":"planeOffset",
                  "pos" : gridStart,
                  "offset": np.array(self.offsetStyle["planeOffset"])
                  }
        
        self.ObjectPositionContainer["planeoffset_start"] = ObjectPosition.fromParent(kwargs)
        
        gridStart = self.ObjectPositionContainer["planeoffset_start"].getPosition()
        
        gridEnd_local_position = np.zeros(3)
        gridEnd_local_position[self._baseGeometry["planeDirection"]] = self._baseGeometry["planeCorner"][self._baseGeometry["planeDirection"]] - self._baseGeometry["origin"][self._baseGeometry["planeDirection"]]
        kwargs = {"name":"planeoffset_end",
                  "pos" : gridEnd_local_position,
                  }
        
        self.ObjectPositionContainer["planeoffset_end"] = ObjectPosition.fromParent(kwargs,
                                                                              parent=self.ObjectPositionContainer["planeoffset_start"])

        gridEnd = self.ObjectPositionContainer["planeoffset_end"].getPosition()
        self._baseGeometry["gridPlaneCoordinates"] = (gridStart.tolist().copy(), gridEnd.tolist().copy())
        
        


    def _buildtickBorderCoordinates(self):
        position = np.zeros(3)
        position[self._baseGeometry["planeDirection"]] = -1 * self._baseGeometry["planeOrientation"][self._baseGeometry["planeDirection"]] * self.offsetStyle["tickBorder"]
        kwargs = {"name":"tickBorder",
                  "pos":position,
                    }

        offsetContainer =  ObjectPosition.fromParent(kwargs,
                                                       parent=self.ObjectPositionContainer["planeoffset_start"]
                                                       )

        self.ObjectPositionContainer["tickBorder"] = offsetContainer
        
        
        borderPositionStart = self.ObjectPositionContainer["tickBorder"].getPosition()
        #borderPositionStart[self.axisDirection()] = self._baseGeometry["origin"][self.axisDirection()]
        
        pos = np.zeros(3)
        pos[self.axisDirection()] = self._baseGeometry["planeCorner"][self.axisDirection()]
        kwargs = {"name":"tickBorder",
                   "pos":pos}
        
        endPositionContainer = ObjectPosition.fromParent(kwargs, self.ObjectPositionContainer["tickBorder"])
        borderPositionEnd = endPositionContainer.getPosition()
        
        borderPositon = np.vstack((borderPositionStart, borderPositionEnd))

        
        self._baseGeometry["borderCoordinates"] = [borderPositon[0,:].tolist(), borderPositon[1,:].tolist()]
        
      
        
        
    def _builderTickBaseCoord(self):
        self._baseGeometry["tickStart"]=[]
        self._baseGeometry["tickEnd"]=[]
        self._baseGeometry["tickValues"]=[]


        orthogonalVertices = self._baseGeometry["orthogonalVertices"]
        tickOrientationToPlane = self._baseGeometry["origin"][self._baseGeometry["planeDirection"]] - orthogonalVertices["planeDirection"][self._baseGeometry["planeDirection"]]

        self.ObjectPositionContainer["tickStart"] = [None for idx in range(self.style["maxTickLevel"] + 1)]
        self.ObjectPositionContainer["tickEnd"] = [None for idx in range(self.style["maxTickLevel"] + 1)]

        self.ObjectPositionContainer["tickValues"] = [None for idx in range(self.style["maxTickLevel"] + 1)]
        
        for idx in range(self.style["maxTickLevel"] + 1):
            
            tickLocalPositionStart = np.zeros(3)
            offset = np.array([tickOrientationToPlane * self.offsetStyle["ticks"] if idx == self._baseGeometry["planeDirection"] else 0 for idx in range(3)])
            
            kwargs = {"name":"tickStart",
                        "pos":tickLocalPositionStart,
                        "offset":offset
                        }
            
            line_length_mag = self.tickStyle["tickLength"] / (1 + idx)
            
            offsetContainerTick =  ObjectPosition.fromParent(kwargs,
                                                               parent=self.ObjectPositionContainer["tickBorder"]
                                                        )
            
            tickEndPos = np.zeros(3)
            tickEndPos[self._baseGeometry["planeDirection"]] = -1 * self._baseGeometry["planeOrientation"][self._baseGeometry["planeDirection"]] * line_length_mag
            
            OffsetTickEnd = ObjectPosition.fromParent({"name":None,     
                                                         "pos" :  tickEndPos,                                             
                                                         },
                                                        parent=offsetContainerTick)
            

            
            offset = np.array([tickOrientationToPlane * self.offsetStyle["tickValues"] if idx == self._baseGeometry["planeDirection"] else 0 for idx in range(3)])
            kwargs = {"name":"tickValues",
                      "offset": offset
                      }
            
            offsetContainerTickValues =  ObjectPosition.fromParent(kwargs,
                                                                    parent=OffsetTickEnd
                                                                    )

            self.ObjectPositionContainer["tickStart"][idx] = offsetContainerTick
            self.ObjectPositionContainer["tickEnd"][idx] = OffsetTickEnd
            self.ObjectPositionContainer["tickValues"][idx] = offsetContainerTickValues
            
            tickStart = offsetContainerTick.getPosition()
            tickEnd = OffsetTickEnd.getPosition()
          #  tickEnd[self._baseGeometry["planeDirection"]] = tickStart[self._baseGeometry["planeDirection"]] + -1 *tick_length_with_dir
            
            tick_coords = [tickStart, tickEnd]
            print(f'tick_coords: {tick_coords}')
            
            self._baseGeometry["ticks"].append(tick_coords)
            
            tickValuesStart = offsetContainerTickValues.getPosition()
            
            self._baseGeometry["tickValues"].append(tickValuesStart)



    def _buildBaseCoords(self):
        plane_diff = self._baseGeometry["planeCorner"] - self._baseGeometry["origin"]
        
        self._baseGeometry["planeOrientation"] = [diff / abs(diff) if diff != 0 else 0 for diff in plane_diff]
        self._baseGeometry["planeDirection"] = [direction for direction, orientation in enumerate(self._baseGeometry["planeOrientation"]) if direction!=self.axisDirection() and orientation != 0][0]
        
        self._buildGridBaseCoordinates()
        
        
        self._buildtickBorderCoordinates()
        self._builderTickBaseCoord()
        self._buildLabelBaseCoordinates()
                
        
    
    def axisDirection(self):
        return self._baseGeometry["direction"]
                
    
    def tickValues(self, minVal:float, maxVal:float, size: float):
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

    def updateTickValues(self, tickLevels, tickLevelsWorld):
        
        for jdx, (ticks, ticksWorld) in enumerate(zip(tickLevels, tickLevelsWorld)):
            for idx, (tick, tickWorld) in enumerate(zip(ticks[1], ticksWorld[1])):
                text_item=self._GLItems["values"][jdx][idx]
                text_item.local_position[self.axisDirection()] = tickWorld
                text_item.blockUpdates(True)
                text_item.setData(pos=text_item.local_position, text=str(round(tick,2)))
                text_item.blockUpdates(False)
                

  
    def setRange(self, mn: float, mx: float):
        self.range = [mn, mx]
        tickLevels, tickLevelsWorld = self.tickValues(*self.range, 1)
        if self.style["showValues"]:
            self.updateTickValues(tickLevels, tickLevelsWorld)
        self._GLItems["tickLineset"].updateTickPositions(tickLevelsWorld)
        self.sigAxisChanged.emit(self)        
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
        del kwargs["labelOffsetDirection"]

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
        
        kwargs = {#"resizeToWorld" : self.labelStyle["labelResizeToWorld"],
                  "text" : self.labelStyle["labelText"],
                  "color" : self.labelStyle["labelColor"],
                  "font" : self.labelStyle["labelFont"],
             #     "anchor" : self.labelStyle["labelAnchor"],
                  }
        
        

        self._GLItems["label"].setData(**kwargs)
    
    
    
    def orthogonalVertices(self) -> Dict[str, Tuple[float, float, float]]:
        return self._baseGeometry["orthogonalVertices"]
        
        
    def showLabel(self, show: bool=True):
        if show:
            self._GLItems["label"].show()
        else:
            self._GLItems["label"].hide()
    
    def setTickStyle(self,
                     tickColor: str | None=None,
                     tickAnchor: Tuple[float, float]=(0., 0.),
                     valuesFont: str | None=None,
                     valuesResizeToWorld: bool=True,
                     valuesAutoUpdateAnchor: bool=None,
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
        if not valuesResizeToWorld is None:
            self.tickStyle["valuesResizeToWorld"] = valuesResizeToWorld
        if not tickAnchor is None:
            self.tickStyle["tickAnchor"] = tickAnchor
        if not showValues is None:
            self.tickStyle["showValues"] = showValues
        
        if not valuesAutoUpdateAnchor is None:
            self.tickStyle["valuesAutoUpdateAnchor"] = (valuesAutoUpdateAnchor or tickAnchor != (0, 0)) and self.tickStyle["showValues"]

        if self.tickStyle["showValues"]:
        
            if "values" in self._GLItems and valuesFont:
                for tick_level in self._GLItems["values"]:
                    for item in tick_level:
                        item.setData(font=self.tickStyle["valuesFont"])
    
    def _initLabelTextItem(self) -> GLAxisTextItem:
        labeItem = GLAxisTextItem(local_position=self._baseGeometry["label"],
                                  pos=self._baseGeometry["label"],
                                  anchor=self.labelStyle["labelAnchor"],
                                  font=self.labelStyle["labelFont"], 
                                  )
        labeItem.setParentItem(self)
        return labeItem
        
    
    def _initValueTextItems(self) -> List[List[GLAxisTextItem]]:
        gl_objects_level = []
        idx=0
        for jdx in range(self.style["maxTickLevel"] + 1):
            gl_objects = []
            for idx in range(self.style["maxNticksperLevel"]):
                local_position = self._baseGeometry["tickValues"][jdx].copy()
                gl_object = GLAxisTextItem(tickLevel=jdx,
                                           local_position=local_position,
                                           ref=idx,
                                           anchor=self.tickStyle["valuesAnchor"],
                                           font=self.tickStyle["valuesFont"], 
                                           )
                gl_object.setParentItem(self)
                gl_object.hide()
                self.sigAxisChanged.connect(gl_object.updateTextVisibilityForItem)
                gl_objects.append(gl_object)
                idx+=1
                
            gl_objects_level.append(gl_objects)
        return gl_objects_level

    def _initTickItems(self) -> _TickLineset:
        tickItem = _TickLineset(self.axisDirection(),
                               baseCoordTicks=self._baseGeometry["ticks"],
                               baseCoordGrid=self._baseGeometry["gridPlaneCoordinates"],
                               borderCoordinates=self._baseGeometry["borderCoordinates"],
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
   #     print(newRange)
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
                        
            if self.tickStyle["valuesAutoUpdateAnchor"] or self.labelStyle["labelAutoUpdateAnchor"]:
                    plotitem_widget.sigViewAngleChanged.connect(self.autoUpateAnchor)
                    self.autoUpateAnchor(plotitem_widget)


    @classmethod
    def compute_azimuth(cls, origin, point):
        dx = point[0] - origin[0]
        dy = point[1] - origin[1] 
        angle = math.atan2(dy, dx)
        return math.degrees(angle) % 360

    @classmethod
    def compute_dp(cls, origin, point):
        dx = point[0] - origin[0]
        dy = point[1] - origin[1]
        perp_slope = -dx/dy if dy != 0 else float('inf')

        m = perp_slope
        
        length = 0.2
        if np.isinf(m):
            dx, dy = 0, length / 2
        else:
            dx = (length / 2) / np.sqrt(1 + m**2)
            dy = m * dx
        return perp_slope, dx, dy
    
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
    def autoUpateAnchor(self, plotitem_widget: GL3DViewWidget):
        
        angle = GLAxisItem.clockwise_angle(self._baseGeometry["origin"][:2],
                                           self.orthogonalVertices()["direction"][:2],
                                           plotitem_widget.cameraPositionNumpy()[:2]
                                           )
#        print(f"\n{self.axisDirection()}")
#        print(f"angle: {angle}")
        half = int(angle // 90) % 4
        

        if half % 4==0:
            newAnchor = (1, self.style["valuesAnchor"][1])
        else:
            newAnchor = (0, self.style["valuesAnchor"][1])
        
        if self.labelStyle["labelAutoUpdateAnchor"]:
            self._GLItems["label"].setAnchor(newAnchor)
            
        if self.tickStyle["valuesAutoUpdateAnchor"]:
            if newAnchor != self.style["valuesAnchor"]:
                self.style["valuesAnchor"]=newAnchor
                for text_item_container in self._GLItems["values"]:
                    for text_item in text_item_container:
                        text_item.setAnchor(newAnchor)
                        
        
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



