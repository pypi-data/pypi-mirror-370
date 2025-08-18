from __future__ import annotations 
from typing import List, Optional, Tuple, Union, Dict, TYPE_CHECKING, Callable, Any
if TYPE_CHECKING:
    from .AbstractGLPlotItem import AbstractGLPlotItem
    from ..widgets.GL3DViewWidget import GL3DViewWidget
    from .GL3DGraphicsItemMixin import GL3DGraphicsItemMixin


import weakref
from PySide6 import QtCore, QtGui, QtWidgets
from pyqtgraph.Qt import QT_LIB
from OpenGL import GL, GLU
from pyqtgraph import Point, Vector, opengl
import numpy as np

from .AbstractGLPlotItem import AbstractGLPlotItem
from .GL3DGraphicsItemMixin import GL3DGraphicsItemMixin
from ..meta import QABCMeta
from abc import abstractmethod
from pyqtgraph.opengl.GLGraphicsItem import GLGraphicsItem

import math
import logging
import warnings
from .GL3DItemGroup import GL3DItemGroup
from dataclasses import dataclass, field
import warnings
from pprint import pprint
import pyqtgraph as pg

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



@dataclass(slots=True)
class _MouseMetrics:
    initPos: np.ndarray|None = field(default=None) 
    pos: np.ndarray|None = field(default=None) 
    lastPos: np.ndarray|None = field(default=None) 
        
    def setInit(self, *args):
        self.pos = np.array(args) if isinstance(*args, (list, tuple)) else args
        self.pos = self.pos[0] if isinstance(self.pos, tuple) and isinstance(self.pos[0], np.ndarray) else self.pos
        self.initPos = self.pos.copy()

    def update(self, args):
        self.lastPos = self.pos.copy()
        #self.pos[:] = args
        self.pos = args
        
    def reset(self):
        self.pos=None
        self.initPos=None
        self.lastPos=None
        
    def validPos(self):
        return not self.pos is None
    
    def delta(self):
        return self.pos - self.lastPos

    def deltaSincePress(self):
        return self.pos - self.initPos


@dataclass(slots=True)
class MouseState:
    intersectedPoint: _MouseMetrics = field(init=False, default=None)
    window: _MouseMetrics = field(init=False, default=None)
    world: _MouseMetrics = field(init=False, default=None)
    
    _interactionKeys: Dict[str, QtCore.Qt.Key] = field(init=False, default=dict)
    _interactionState: Dict[str, bool] = field(init=False, default=dict)
    _btn_modes: Dict[str, bool] = field(init=False, default=dict)
    _opts: Dict[str, bool] = field(init=False, default=dict)

    def __post_init__(self):
        self.intersectedPoint = _MouseMetrics()
        self.window = _MouseMetrics()
        self.world = _MouseMetrics()
        self._interactionKeys = {"axisInteracting" : QtCore.Qt.KeyboardModifier.ControlModifier,
                                 "constantAxisZoom" : (QtCore.Qt.KeyboardModifier.ControlModifier | QtCore.Qt.KeyboardModifier.ShiftModifier),
                                 "pan" : QtCore.Qt.MouseButton.LeftButton,
                                 "axisScale" : QtCore.Qt.MouseButton.RightButton,
                                 
                                 }
        self._interactionState = {"axisInteracting" : False,
                                  "constantAxisZoom" : False,
                                  "intersectedAxis" : None,
                                  "mouse" : False,
                                  "keys" : False,
                                  }
        
        self._opts = {"interactingModifier" : QtCore.Qt.KeyboardModifier.ControlModifier,
                      "constantAxisKey" : QtCore.Qt.KeyboardModifier.ShiftModifier,
                      "interactingMouseBtns" : (QtCore.Qt.MouseButton.LeftButton | QtCore.Qt.MouseButton.RightButton),
                      "axisPanBtn" :  QtCore.Qt.MouseButton.LeftButton,
                      "axisScaleBtn" : QtCore.Qt.MouseButton.RightButton
                      }
        
        self._btn_modes = {"axisPanBtn" :  QtCore.Qt.MouseButton.LeftButton,
                           "axisScaleBtn" : QtCore.Qt.MouseButton.RightButton
                           } 

    def getModType(self, btn):
        if self.mouseInteracting():
            if self.keyInteracting():
                if self._btn_modes["axisPanBtn"] == btn:
                    return "pan"
                elif self._btn_modes["axisScaleBtn"] == btn:
                    return "scale"
    
    def KeyToggleEvent(self, ev: QtGui.QKeyEvent):
        if ev.modifiers() & self._opts["interactingModifier"]:
            if not self.keyInteracting():
                self._setKeyInteracting(True)
            if ev.modifiers() & self._opts["constantAxisKey"]:
                if not self._interactionState["constantAxisZoom"]:
                    self._interactionState["constantAxisZoom"]=True 
        else:
            self._setKeyInteracting(False)

    def userInteracting(self):
        return self.keyInteracting()
    
    def keyInteracting(self):
        return self._interactionState["keys"]
    
    def _setKeyInteracting(self, flag):
        self._interactionState["keys"]=flag
        if not flag:
            self._interactionKeys["constantAxisZoom"]=False
            
    def constantAxis(self):
        return self._interactionState["constantAxisZoom"]
    
    def _setMouseInteracting(self, flag):
        self._interactionState["mouse"]=flag
        
                    
    def mouseToggleEvent(self, ev):
        if ev.buttons() & self._opts["interactingMouseBtns"]:
            if not self._interactionState["mouse"]:
                self._setMouseInteracting(True)
        else:
            self.window.reset()
            self.world.reset()
            self.intersectedPoint.reset()
            self._interactionState["intersectedAxis"] = None
            
    def windowPos(self):
        return self.window.pos()    

    def mouseInteracting(self):
        return self._interactionState["mouse"]
     
    def mouseMove(self, x, y):
        self.window.update(x, y)
    
    def setWorldPoint(self, point):
        self.world.setInit(point)
        
    def updateWorldPoint(self, point):
        self.world.setInit(point)
        self.world.update(point)
        
    def setIntersectPoint(self, ax, point):
        self.intersectedPoint.setInit(point)
        self._interactionState["intersectedAxis"]=ax
        
    def updateIntersectPoint(self, point):
        self.intersectedPoint.update(point)
    
    def setNoInteractionState(self):
        self._interactionState["axisInteracting"] = False
        self._interactionState["constantAxisZoom"] = False
        self._interactionState["intersectedAxis"] = None

    def validWindowPos(self):
        return self.window.validPos()

    def validWorldPos(self):
        return self.world.validPos()
    
    def validIntersectedPoint(self):
        return self.intersectedPoint.validPos()



            
class GL3DViewBox(GL3DGraphicsItemMixin, GLGraphicsItem):

    sigYRangeChanged = QtCore.Signal(object, object)
    sigXRangeChanged = QtCore.Signal(object, object)
    sigZRangeChanged = QtCore.Signal(object, object)
    sigRangeChanged = QtCore.Signal(object, object, object)
    sigRangeChangedManually = QtCore.Signal(object)
    
    sigStateChanged = QtCore.Signal(object)
    sigTransformChanged = QtCore.Signal(object)
    sigResized = QtCore.Signal(object)
    sigViewChange = QtCore.Signal(object)

    
    XAxis = 0
    YAxis = 1
    ZAxis = 2
    XYZAxes = 3

    
    def __init__(self,
                 parentItem=None,
                 worldRange=np.array([[0., 1.]]*3).tolist(),
                 enableMouse=True,
                 defaultPadding=np.array([0.0]*3),
                 **kwargs
                 ):
        super().__init__(parentItem=parentItem)
        self.scalebycounter=0
        self.setFlag(self.GLGraphicsItemFlag.ItemHasNoContents)
        self._updatingRange=False
        self._matrixNeedsUpdate=True
        self._autoRangeNeedsUpdate=True
        
        self._mouseZoomFactor=0.999

        self._view_changed_timer=QtCore.QTimer()
        self._update_axis_ms=100
        self._update_interval = 50 
        self._last_update_time = 0
        self._view_changed_timer.setSingleShot(True)
        self._view_changed_timer.timeout.connect(self._ProcessViewDrag)
        self.mouse_state = MouseState()
        
        self.mouse_info={"mouseAlongAxisPos" : None,
                         "prevmouseAlongAxisPos" : None,
                         "intersectedAxis" : None
                         }
        self._cartesian_view_coords = np.array([0., 0., 0.])
        self._camera_position = np.array([0., 0., 0.])

        self._name=None
        self._viewRange:List[List[float]]=None
        self._itemBoundsCache = weakref.WeakKeyDictionary()
        
        self.state={"autoRange" : [True]*3,
                    "autoVisibleOnly" : [False]*3,
                    "aspectLocked" : False,
                    "defaultPadding" : defaultPadding,
                    "mouseEnabled": [enableMouse, enableMouse, enableMouse],
                    "targetRange" : [[0,1], [0,1], [0, 1]],
                    "viewRange" : [[0,1], [0,1], [0, 1]],
                    "linkedViews" : [None, None, None],
                    "explicitViewRange" : False,
                    "wheelScaleFactor": -1.0 / 14.0,
                    'limits': { 
                                'xLimits': [-1E307, +1E307],   # Maximum and minimum visible X values
                                'yLimits': [-1E307, +1E307],   # Maximum and minimum visible Y values
                                'zLimits' : [-1E307, +1E307],
                                'xRange': [None, None],   # Maximum and minimum X range
                                'yRange': [None, None],   # Maximum and minimum Y range
                                'zRange': [None, None], 
                                },
                    
                    }
        
        
        self.setWorldRange(worldRange)
        
        self.state.update({"worldSize" : [abs(r[0] - r[1]) for r in self.state["worldRange"]],
                           "vertexCoordinates" : self.get_cube_face(self.state["worldRange"]),
                           })
        
        
        self.addedItems: List[GL3DGraphicsItemMixin]=[]
        
        
        
        self._range_arr = {"worldRange" : np.array(self.state["worldRange"], dtype=float),
                           "viewRange" : np.array(self.state["viewRange"], dtype=float),
                           }
        
        
        self.childGroup = GL3DItemGroup(parentItem=self)
        self.childGroup.itemsChangedListeners.append(self)
    
    def implements(self, interface):
        return interface == 'ViewBox'

    def addItem(self, item, ignoreBounds=False):
        item.setParentItem(self.childGroup)
        if not item in self.addedItems and not ignoreBounds:
            self.addedItems.append(item)          

        self.queueUpdateAutoRange()
        
    def removeItem(self, item):
        item.setParentItem(None)
        if item in self.addedItems:
            self.addedItems.remove(item)
            
        self.queueUpdateAutoRange()

        
    
    def setWorldRange(self, worldRange: List[List[float]]):
        for wr in worldRange:
            if wr[0] > wr[1]:
                raise ValueError(f"worldRange[jdx][0] < worldRange[jdx][1] for each axis")
        
        try:
            shape = np.shape(worldRange)
            if shape != (3, 2):
                raise ValueError(F"worldRange must have shape == (3,2)")
        except:            
            raise ValueError(F"worldRange must have shape == (3,2)")
        self.state["worldRange"] = worldRange
        
    def viewRange(self) -> List[List[np.ndarray]]:
        return [x[:] for x in self.state["viewRange"]]
    
    def viewRangeArr(self) -> List[List[np.ndarray]]:
        self._range_arr["viewRange"][:] = self.viewRange()
        return self._range_arr["viewRange"]

    def worldRange(self) -> List[List[np.ndarray]]:
        return [x[:] for x in self.state["worldRange"]]
    
    def worldRangeArr(self) -> List[List[np.ndarray]]:
        self._range_arr["worldRange"][0, :] = self.state["worldRange"][0][:]
        self._range_arr["worldRange"][1, :] = self.state["worldRange"][1][:]
        self._range_arr["worldRange"][2, :] = self.state["worldRange"][2][:]
        return self._range_arr["worldRange"]

    def targetRange(self) -> List[List[np.ndarray]]:
        return [x[:] for x in self.state["targetRange"]]
    
    def _internal_update(self):
        return QtWidgets.QGraphicsItem.update()

    def innerSceneItem(self):
        return self.childGroup

    def queueUpdateAutoRange(self):
        self._autoRangeNeedsUpdate = True
        self.update()

    def _effectiveLimits(self):
        return (self.state['limits']['xLimits'], self.state['limits']['yLimits'], self.state['limits']['zLimits'])
    
    def updateViewRange(self, forceX=False, forceY=False, forceZ=False):
        viewRange = [self.state['targetRange'][0][:], self.state['targetRange'][1][:], self.state['targetRange'][2][:]]
        changed = [False]*3
        
        aspect = self.state['aspectLocked']  # size ratio / view ratio
        limits = self._effectiveLimits()

        minRng = [self.state['limits']['xRange'][0], self.state['limits']['yRange'][0], self.state['limits']['zRange'][0]]
        maxRng = [self.state['limits']['xRange'][1], self.state['limits']['yRange'][1], self.state['limits']['zRange'][1]]

        for ax in [0, 1, 2]:
            if limits[ax][0] is None and limits[ax][1] is None and minRng[ax] is None and maxRng[ax] is None:
                continue
            # max range cannot be larger than bounds, if they are given
            if limits[ax][0] is not None and limits[ax][1] is not None:
                if maxRng[ax] is not None:
                    maxRng[ax] = min(maxRng[ax], limits[ax][1] - limits[ax][0])
                else:
                    maxRng[ax] = limits[ax][1] - limits[ax][0]

        for ax in [0, 1, 2]:
            range = viewRange[ax][1] - viewRange[ax][0]
            if minRng[ax] is not None and minRng[ax] > range:
                viewRange[ax][1] = viewRange[ax][0] + minRng[ax]
                self.state["targetRange"][ax] = viewRange[ax]
            if maxRng[ax] is not None and maxRng[ax] < range:
                viewRange[ax][1] = viewRange[ax][0] + maxRng[ax]
                self.state["targetRange"][ax] = viewRange[ax]
            if limits[ax][0] is not None and viewRange[ax][0] < limits[ax][0]:
                delta = limits[ax][0] - viewRange[ax][0]
                viewRange[ax][0] += delta
                viewRange[ax][1] += delta
                self.state["targetRange"][ax] = viewRange[ax]
            if limits[ax][1] is not None and viewRange[ax][1] > limits[ax][1]:
                delta = viewRange[ax][1] - limits[ax][1]
                viewRange[ax][0] -= delta
                viewRange[ax][1] -= delta
                self.state["targetRange"][ax] = viewRange[ax]
 
        thresholds = [(viewRange[axis][1] - viewRange[axis][0]) * 1.0e-9 for axis in (0,1,2)]
        changed = []
        for ax in [0,1,2]:
            con_1 = abs(viewRange[ax][0] - self.state["viewRange"][ax][0]) > thresholds[ax]
            con_2 = abs(viewRange[ax][1] - self.state["viewRange"][ax][1]) > thresholds[ax]
            changed.append(any((con_1, con_2)))

        self.state["viewRange"] = viewRange
        if any(changed):
            self._matrixNeedsUpdate = True
            self.update()

            # Inform linked views that the range has changed
            for ax in [0, 1, 2]:
                if not changed[ax]:
                    continue
                link = self.linkedView(ax)
                if link is not None:
                    link.linkedViewChanged(self, ax)

            if changed[0]:
                self.sigXRangeChanged.emit(self, tuple(self.state["viewRange"][0]))
            if changed[1]:
                self.sigYRangeChanged.emit(self, tuple(self.state["viewRange"][1]))
            if changed[2]:
                self.sigZRangeChanged.emit(self, tuple(self.state["viewRange"][2]))
            
            self.sigRangeChanged.emit(self, self.state["viewRange"], changed)
            
    def linkedView(self, ax):
        ## Return the linked view for axis *ax*.
        ## this method _always_ returns either a ViewBox or None.
        v = self.state['linkedViews'][ax]
        if v is None or isinstance(v, str):
            return None
        else:
            return v()  ## dereference weakref pointer. If the reference is dead, this returns None

    
    def itemBoundsChanged(self, item):
        self._itemBoundsCache.pop(item, None)
        if any((self.state['autoRange'][0],
                self.state['autoRange'][1],
                self.state['autoRange'][2]
                )):
            self.queueUpdateAutoRange()
            
    def itemsChanged(self):
        self.queueUpdateAutoRange()
    
    def itemChange(self, change, value):
        
        ret = super().itemChange(change, value)

        if change == self.GLGraphicsItemChange.ItemParentWidgetChange:
            parent_widget = self.parentWidget()
            if not parent_widget is None and hasattr(parent_widget, 'sigPrepareForPaint'):
                parent_widget.sigPrepareForPaint.disconnect(self.prepareForPaint)
        elif change == self.GLGraphicsItemChange.ItemParentWidgetHasChanged:
            
            parent_widget = self.parentWidget()
            if not parent_widget is None and hasattr(parent_widget, 'sigPrepareForPaint'):
                parent_widget.sigPrepareForPaint.connect(self.prepareForPaint)
            parent_widget.sigPrepareForPaint.emit()
        return ret
                        
    def _resetTarget(self):
        self.state['targetRange'] = [self.state["viewRange"][0][:], self.state["viewRange"][1][:], self.state["viewRange"][2][:]]

    def setRange(self, xRange=None, yRange=None, zRange=None, padding=None, update=True, disableAutoRange=True):
        changes = {}   # axes
        setRequested = [False]*3
        if not xRange is None:
            changes[0] = xRange
            setRequested[0] = True
        if not yRange is None:
            changes[1] = yRange
            setRequested[1] = True
        if not zRange is None:
            changes[2] = zRange
            setRequested[2] = True
        if len(changes) == 0:
            raise Exception("Must specify at least one of rect, xRange, yRange or zRange")
                
        changed = [False]*3
        
   
        # Disable auto-range for each axis that was requested to be set
        if disableAutoRange:
            xOff = False if setRequested[0] else None
            yOff = False if setRequested[1] else None
            zOff = False if setRequested[2] else None

            self.enableAutoRange(x=xOff, y=yOff, z=zOff)
            changed.append(True)


        for ax, range in changes.items():
            mn = min(range)
            mx = max(range)

            preserve = False
            if mn == mx:
                preserve = True
                dy = self.state["viewRange"][ax][1] - self.state["viewRange"][ax][0]
                if dy == 0:
                    dy = 1
                mn -= dy*0.5
                mx += dy*0.5
        
            if not preserve:
                if padding is None:
                    xpad = self.state["defaultPadding"][ax]
                else:
                    xpad = padding
                p = (mx-mn) * xpad
                mn -= p
                mx += p

            if self.state['targetRange'][ax] != [mn, mx]:
                self.state['targetRange'][ax] = [mn, mx]
                changed[ax] = True

        lockX, lockY, lockZ = setRequested
        if lockX and lockY and lockZ:
            lockX = False
            lockY = False
            lockZ = False

        self.updateViewRange(lockX, lockY, lockZ)
        if any(changed):
            if changed[0] and not self.state['autoRange'][0]:
                self._autoRangeNeedsUpdate = True
            elif changed[1] and not self.state['autoRange'][1]:
                self._autoRangeNeedsUpdate = True
            elif changed[2] and not self.state['autoRange'][2]:
                self._autoRangeNeedsUpdate = True
                
            self.sigStateChanged.emit(self)
            
        
    def updateAutoRange(self):
        if self._updatingRange:
            return
        self._updatingRange = True
        try:
            if not any(self.state['autoRange']):
                return

            targetRect = self.viewRange()
            fractionVisible = self.state['autoRange'][:]
            for i in [0,1,2]:
                if type(fractionVisible[i]) is bool:
                    fractionVisible[i] = 1.0

            childRange = None
            kwargs = {}
            orthoRange = [None, None, None]
            for ax in [0, 1, 2]:
                if self.state['autoVisibleOnly'][ax]:
                    orthoRange[ax] = [targetRect[x] for x in range(3) if x != ax]    

            childRange = self.childrenBounds(frac=fractionVisible, orthoRange=orthoRange)
            
            try:
                pass
            except:
                pass
            
            for ax, s in enumerate("xyz"):
                if not self.state['autoRange'][ax]:
                    continue
                xr = childRange[ax]
                if xr is not None:
                    wp = (xr[1] - xr[0]) * self.state["defaultPadding"][ax]
                    childRange[ax][0] -= wp
                    childRange[ax][1] += wp
                    targetRect[ax] = childRange[ax]
                    kwargs[f"{s}Range"] = targetRect[ax]

            if len(kwargs) == 0:
                return
            kwargs['padding'] = 0.0
            kwargs['disableAutoRange'] = False
            self.setRange(**kwargs)
        finally:
            (f"finally")
            self._autoRangeNeedsUpdate = False
            self._updatingRange = False
            
    def setZRange(self, min, max, padding=None, update=True):
        """
        Set the visible Z range of the view to [*min*, *max*].
        The *padding* argument causes the range to be set larger by the fraction specified.
        (by default, this value is between the default padding and 0.1 depending on the size of the ViewBox)
        """
        self.setRange(zRange=[min, max], update=update, padding=padding)

    def setYRange(self, min, max, padding=None, update=True):
        """
        Set the visible Y range of the view to [*min*, *max*].
        The *padding* argument causes the range to be set larger by the fraction specified.
        (by default, this value is between the default padding and 0.1 depending on the size of the ViewBox)
        """
        self.setRange(yRange=[min, max], update=update, padding=padding)

    def setXRange(self, min, max, padding=None, update=True):
        """
        Set the visible X range of the view to [*min*, *max*].
        The *padding* argument causes the range to be set larger by the fraction specified.
        (by default, this value is between the default padding and 0.1 depending on the size of the ViewBox)
        """
        self.setRange(xRange=[min, max], update=update, padding=padding)


    def childrenBounds(self, frac=[1., 1., 1.], orthoRange=(None, None, None), items: List[GL3DGraphicsItemMixin]=None):
        """
        Method is similar to pyqtgraph.ViewBox, except this method does calculate the bounds for all items and axis in 1 call
        
        """
        if items is None:
            items = self.addedItems
        itemBounds = []
        
        for item in items:
            if not item.visible():
                continue
 
            if hasattr(item, 'dataBounds') and not item.dataBounds is None:
                if frac is None:
                    frac = (1.0, 1.0, 1.0)
                
                bounds_unchecked = item.dataBounds(frac, orthoRange)
                bounds = []
                bounds_arr = []
                for b_i in bounds_unchecked:
                    
                    if (b_i is None or (b_i[0] is None or b_i[1] is None)
                        or not math.isfinite(b_i[0])
                        or not math.isfinite(b_i[1])
                        ):
                        bounds.append([b_i, False])
                        bounds_arr.append(b_i)
                    else:
                        bounds.append([b_i, True])
                        bounds_arr.append(b_i)
                itemBounds.append(bounds)
            else:
                if item.flags() & item.GLGraphicsItemFlag.ItemHasNoContents:
                    continue
                bounds = self.mapFromItemToView(item, item.boundingRect()).boundingRect()
                itemBounds.append((bounds, True, True, 0))

        range = [None, None, None]
        for item_bound in itemBounds:
            for idx, (bounds, flag) in enumerate(item_bound):
                if flag:
                    if not range[idx] is None:
                        range[idx] = [min(bounds[0], range[idx][0]), max(bounds[1], range[idx][1])]
                    else:
                        range[idx] = [bounds[0], bounds[1]]
        return range


    def enableAutoRange(self, axis=None, enable=True, x=None, y=None, z=None):
        
        if not x is None or not y is None or not z is None:
            if not x is None:
                self.enableAutoRange(GL3DViewBox.XAxis, x)
            if not y is None:
                self.enableAutoRange(GL3DViewBox.YAxis, y)
            if not z is None:
                self.enableAutoRange(GL3DViewBox.ZAxis, z)
            return

        if enable is True:
            enable = 1.0

        if axis is None:
            axes = [0, 1, 2]
        
        elif axis == GL3DViewBox.XAxis or axis == 'x':
            axes = [0]
        elif axis == GL3DViewBox.YAxis or axis == 'y':
            axes = [1]
        elif axis == GL3DViewBox.ZAxis or axis == 'z':
            axes = [2]
        else:
            raise Exception('axis argument must be GLViewBox.XAxis, GLViewBox.YAxis, or GLViewBox.XYAxes.')
        for ax in axes:
            if self.state['autoRange'][ax] != enable:
                if enable is False and self._autoRangeNeedsUpdate:
                    self.updateAutoRange()

                self.state['autoRange'][ax] = enable
                self._autoRangeNeedsUpdate |= (enable is not False)
                self.update()
        self.sigStateChanged.emit(self)
        
    def changeParent(self):
        self._updateView()


    @QtCore.Slot()
    def prepareForPaint(self):
        #autoRangeEnabled = (self.state['autoRange'][0] is not False) or (self.state['autoRange'][1] is not False)
        # don't check whether auto range is enabled here--only check when setting dirty flag.
        if self._autoRangeNeedsUpdate: # and autoRangeEnabled:
            self.updateAutoRange()
        self.updateMatrix()
        
    def _updateView(self):
        ## called to see whether this item has a new view to connect to
        ## NOTE: This is called from GraphicsObject.itemChange or GraphicsWidget.itemChange.

        if not hasattr(self, '_connectedView'):
            # Happens when Python is shutting down.
            return

        ## It is possible this item has moved to a different GLViewBox or widget;
        ## clear out previously determined references to these.
        self.forgetViewBox()
        self.forgetViewWidget()
        
        ## check for this item's current viewbox or view widget
        view = self.getViewBox()
        #if view is None:
            ### "  no view"
            #return

        oldView = None
        if self._connectedView is not None:
            oldView = self._connectedView()
            
        if view is oldView:
            ## "  already have view", view
            return

        ## disconnect from previous view
        if oldView is not None:
            Device = 'Device' if hasattr(oldView, 'sigDeviceRangeChanged') else ''
            for signal, slot in [(f'sig{Device}RangeChanged', self.viewRangeChanged),
                                 (f'sig{Device}TransformChanged', self.viewTransformChanged)]:
                try:
                    getattr(oldView, signal).disconnect(slot)
                except (TypeError, AttributeError, RuntimeError):
                    # TypeError and RuntimeError are from pyqt and pyside, respectively
                    pass
            
            self._connectedView = None

        ## connect to new view
        if view is not None:
            view.sigRangeChanged.connect(self.viewRangeChanged)
            view.sigTransformChanged.connect(self.viewTransformChanged)
            self._connectedView = weakref.ref(view)
            self.viewRangeChanged()
            self.viewTransformChanged()
        
        self._replaceView(oldView)
        
        self.viewChanged(view, oldView)
        
    def viewChanged(self, view, oldView):
        """Called when this item's view has changed
        (ie, the item has been added to or removed from a GLViewBox)"""
        
    def _replaceView(self, oldView, item=None):
        if item is None:
            item = self
        for child in item.childItems():
            if isinstance(child, GL3DGraphicsItemMixin):
                if child.getViewBox() is oldView:
                    child._updateView()
                        #self._replaceView(oldView, child)
            else:
                self._replaceView(oldView, child)
        

    def forgetViewBox(self):
        self._viewBox = None

    def forgetViewWidget(self):
        self._viewWidget = None

    def mapFromItemToView(self, item, obj):
        """Maps *obj* from the local coordinate system of *item* to the view coordinates"""
        self.updateMatrix()
        return self.childGroup.mapFromItem(item, obj)


    def updateMatrix(self, changed=None):
        if not self._matrixNeedsUpdate:
            return

        vb_viewRange = self.viewRangeArr() 
        vb_worldRange = self.worldRangeArr() 

        range_view = vb_viewRange[:, 1] - vb_viewRange[:, 0]
        range_view[range_view == 0] = 1.0

        range_world = vb_worldRange[:, 1] - vb_worldRange[:, 0]
        range_world[range_world == 0] = 1.0

        scale = range_world / range_view
        offset = vb_worldRange[:, 0] - vb_viewRange[:, 0] * scale

        self.childGroup.resetTransform()
        tr = self.childGroup.transform()
        tr.translate(*offset)
        tr.scale(*scale)
        
        self.childGroup.setTransform(tr)
        self._matrixNeedsUpdate = False
        self.sigTransformChanged.emit(self)




    def viewWorldRange(self):
        vr0 = self.state["viewRange"][0]
        vr1 = self.state["viewRange"][1]
        vr2 = self.state["viewRange"][2]
        
        return QtCore.QRectF(vr0[0], vr1[0], vr2[0], vr0[1]-vr0[0], vr1[1]-vr1[0], vr2[1]- vr2[0])    
    
    def autoRangeEnabled(self):
        return self.state['autoRange'][:]

    def viewWorldRect(self):
        vr0 = self.state["viewRange"][0]
        vr1 = self.state["viewRange"][1]
        vr2 = self.state["viewRange"][2]
        
        return QtCore.QRectF(vr0[0], vr1[0], vr2[0], vr0[1]-vr0[0], vr1[1]-vr1[0], vr2[1]- vr2[0])
    
    def zoomWorld(self, ev, delta):
        for i in [1, 1/4]:
            rMultiplier = self._mouseZoomFactor**(i*delta)
            parent = self.parentWidget()
            distance = parent.opts['distance'] * rMultiplier
            opts = parent.opts.copy()
            opts["distance"] = distance
            opts["elevation"] = parent.opts["elevation"]
            opts["azimuth"] = parent.opts["azimuth"]

            if self._verifyOutsideBox(opts):
                parent.opts["distance"] = distance
                self.update()
            #    self.requestViewUpdate()
                zoomChanged=True
            else:
                zoomChanged=False
                            
            if zoomChanged:
                return 
        
    def zoomAxis(self, ev, delta):
        self.parentWidget().makeCurrent() 
        if self.mouse_state.constantAxis():
            pxCoords = ev.position().x(), ev.position().y()
            world_coords = GL3DViewBox.map_2D_coords_to_3D(self.parentWidget(), *pxCoords) 
            intersectedAxis, intersectedPoint = self.findIntersectingAxis(self.cameraPositionNumpy(), world_coords)
        else:
            wr = self.state["worldRange"]
            intersectedPoint = [0.5 * (wr[0][0] + wr[0][1]),
                                0.5 * (wr[1][0] + wr[1][1]),
                                0.5 * (wr[2][0] + wr[2][1]),
                                ]
            intersectedAxis = None

        s = 1.02 ** (delta * self.state['wheelScaleFactor'])
        
        s = [s if ax != intersectedAxis else None for ax in range(3)]

        intersectedPoint = self.childGroup.mapFromView(pg.Vector(*intersectedPoint))
        
        self._resetTarget()
        self.scaleBy(s=s, center=(intersectedPoint.x(), intersectedPoint.y(), intersectedPoint.z()))
        self.state["autoRange"] = 3 * [False]



    def scaleBy(self, **kwargs):
        self.scalebycounter+=1
        s, center, x, y, z = kwargs.get("s", None), kwargs.get("center", None), kwargs.get("x", None), kwargs.get("y", None), kwargs.get("z", None)

        if s is not None:
            x, y, z = s[0], s[1], s[2]

        affect = [x is not None, y is not None, z is not None]
        if not any(affect):
            return

        scaled_axes = [i for i in range(3) if affect[i]]
        if not scaled_axes:
            return

        # Get current view ranges
        view_ranges = self.viewRange()
        
        new_ranges = [None, None, None]

        for ax in scaled_axes:
            scale_factor = [x, y, z][ax]
            current_min, current_max = view_ranges[ax]
            width = current_max - current_min
            
            c = center[ax]
            new_width = width * scale_factor
            new_min = c - (c - current_min) * scale_factor
            new_max = c + (current_max - c) * scale_factor
            new_ranges[ax] = [new_min, new_max]
            print(f"c: {c}")

        set_kwargs = {}
        if new_ranges[0] is not None:
            set_kwargs['xRange'] = new_ranges[0]
        if new_ranges[1] is not None:
            set_kwargs['yRange'] = new_ranges[1]
        if new_ranges[2] is not None:
            set_kwargs['zRange'] = new_ranges[2]
        from pprint import pprint
        pprint(np.round(view_ranges, 3))
        pprint(set_kwargs)
        self.setRange(**set_kwargs, padding=0)
        self._matrixNeedsUpdate=True
        self.update()
        
    def mouseEnabled(self):
        return self.state['mouseEnabled'][:]
 
    def setDefaultPadding(self, padding=0.02):
        """
        Sets the fraction of the data range that is used to pad the view range in when auto-ranging.
        By default, this fraction is 0.02.
        """
        self.state['defaultPadding'] = padding

    def wheelEvent(self, ev: QtGui.QWheelEvent):
        delta = ev.angleDelta().x()
        if delta == 0:
            delta = ev.angleDelta().y()
        self.zoomAxis(ev, delta)
        self.parentWidget().update()
    
    def _emit_view_changed(self):
        self._last_update_time = QtCore.QTime.currentTime().msecsSinceStartOfDay()
        self._pending_update = False
        self.sigViewChange.emit(self)
        
    def requestViewUpdate(self):
        current_time = QtCore.QTime.currentTime().msecsSinceStartOfDay()
        elapsed = current_time - self._last_update_time
        
        if elapsed > self._update_interval:
            self._emit_view_changed()
        else:
            if not self._pending_update:
                self._pending_update = True
                QtCore.QTimer.singleShot(self._update_interval - elapsed,
                                         self._delayed_view_update)
                
    def _delayed_view_update(self):
        if self._pending_update:
            self._emit_view_changed()
   
        
    def _ProcessViewDrag(self, dP, center):
        if (np.abs(dP) > np.amin(self.state["worldSize"])).any():
            return 
        mask = [1.,]*3
        mask[self.mouse_state.intersectedAxis] = 0.
        mask = np.array(mask)
        
        s = ((mask * 0.2) + 1) ** dP   
        dx, dy, dz = s
        self._resetTarget()
        
        self.scaleBy(x=dx, y=dy, z=dz, center=center)
        self._matrixNeedsUpdate=True

    def mousePressEvent(self, ev):
        self.mouse_state.mouseToggleEvent(ev)
    
    def mouseReleaseEvent(self, ev):
        self.mouse_state.mouseToggleEvent(ev)

    def mouseMoveEvent(self, ev):
        if self.userInteracting():
            if bin(ev.buttons().value).count("1") == 1:
                mode = self.mouse_state.getModType(ev.buttons())
                if mode == "scale":
                    pos = ev.pos().x(), ev.pos().y()
                    camera_pos = self.cameraPositionNumpy()
                    self.parentWidget().makeCurrent() 
                    world_coords = GL3DViewBox.map_2D_coords_to_3D(self.parentWidget(), *pos)   
                    intersectedAxis, intersectedPoint = self.findIntersectingAxis(camera_pos, world_coords)
                    if not intersectedAxis is None:
                        intersectedPoint = np.array([point if idx != intersectedAxis else 0 for idx, point in enumerate(intersectedPoint)])
                        if not self.mouse_state.validIntersectedPoint():
                            self.mouse_state.setIntersectPoint(intersectedAxis, intersectedPoint)
                        else:
                            self.mouse_state.updateIntersectPoint(intersectedPoint)
                            delta = -1 * self.mouse_state.intersectedPoint.delta()
                            p_0 = self.mouse_state.intersectedPoint.initPos
                            self._ProcessViewDrag(delta, p_0)
                            
                elif mode == "pan":
                    pos = ev.pos().x(), ev.pos().y()
                    camera_pos = self.cameraPositionNumpy()
                    self.parentWidget().makeCurrent() 
                    world_coords = GL3DViewBox.map_2D_coords_to_3D(self.parentWidget(), *pos)   
                    intersectedAxis, intersectedPoint = self.findIntersectingAxis(camera_pos, world_coords)
                    if not intersectedAxis is None:
                        intersectedPoint = np.array([point if idx != intersectedAxis else 0 for idx, point in enumerate(intersectedPoint)])
                        if not self.mouse_state.validIntersectedPoint():
                            self.mouse_state.setIntersectPoint(intersectedAxis, intersectedPoint)
                        else:
                            self.mouse_state.updateIntersectPoint(intersectedPoint)
                            delta = -1 * self.mouse_state.intersectedPoint.delta()
                            self.translateBy(**{ax : delta[i] for i, ax in enumerate("xyz") if i != intersectedAxis} )
                self.state["autoRange"] = 3 * [False]
                return 

    
    def translateBy(self, t=None, x=None, y=None, z=None):
        """
        Translate the view by *t*, which may be a Point or tuple (x, y).

        Alternately, x or y may be specified independently, leaving the other
        axis unchanged (note that using a translation of 0 may still cause
        small changes due to floating-point error).
        """
        vr = self.targetRange()
        for i, ax in enumerate((x, y, z)):
            if not ax is None:
                vr[i] += ax
        kwargs = {}
        
        if not x is None:
            kwargs["xRange"] = vr[0]
        if not y is None:
            kwargs["yRange"] = vr[1]
        if not z is None:
            kwargs["zRange"] = vr[2]
        self.setRange(**kwargs, padding=0)

    @classmethod
    def zoom_2d(cls, point, drag, viewRange, base=1.1):
        axis_mins = np.array([vr[0] for vr in viewRange])
        axis_maxs = np.array([vr[1] for vr in viewRange])

        scales = base ** -drag
        
        new_axis_mins = scales * axis_mins + (1 - scales) * point
        new_axis_maxs = scales * axis_maxs + (1 - scales) * point
        return [[new_min, new_max] for new_min, new_max in zip(new_axis_mins, new_axis_maxs)]


    def _verifyOutsideBox(self, opts):
        if any([self.state["worldRange"][idx][1] <= pos for idx, pos in enumerate(self.parentWidget().cameraPosition(opts))]):
            return True
        else:
            return False
        
    def _checkCartesianBounds(self, coords):
        return [self.state["worldRange"][i][0] <= coords[i] < self.state["worldRange"][i][1] for i in range(3)]

    def keyPressEvent(self, ev):
        ev.accept()
        self.mouse_state.KeyToggleEvent(ev)


    def keyReleaseEvent(self, ev):
        self.mouse_state.KeyToggleEvent(ev)
        
            
    def focusOutEvent(self, event):...
        #print("OpenGLWidget lost focus!")

    def cameraPositionNumpy(self):
        p = self.parentWidget().cameraPosition()
        self._camera_position[:] = p.x(), p.y(), p.z()
        return self._camera_position
    
    
    def targetRect(self, ax):
        """
        Return the region which has been requested to be visible.
        (this is not necessarily the same as the region that is *actually* visible--
        resizing and aspect ratio constraints can cause targetRect() and viewRect() to differ)
        """
        try:
            tr0, tr1 = [self.state['targetRange'][i] for i in range(3) if i != ax]

            return QtCore.QRectF(tr0[0], tr1[0], tr0[1]-tr0[0], tr1[1] - tr1[0])
        except:
            raise

    @classmethod
    def line_rectangle_intersection(cls, P1, P2, rect_corners):
        P1 = np.array(P1)
        P2 = np.array(P2)
        rect_corners = [np.array(c) for c in rect_corners]
        
        v1 = rect_corners[1] - rect_corners[0]
        v2 = rect_corners[2] - rect_corners[0]
        normal = np.cross(v1, v2)
        normal = normal / np.linalg.norm(normal)

        # Plane equation: (P - P0) · normal = 0
        P0 = rect_corners[0]
        
        # Line direction
        line_dir = P2 - P1
        line_dir = line_dir / np.linalg.norm(line_dir)
        
        # Check if line is parallel to the plane (no intersection)
        denom = np.dot(normal, line_dir)
        if np.abs(denom) < 1e-6:
            return None  # Line is parallel to the plane
        
        # Compute intersection point on the plane
        t = np.dot(normal, P0 - P1) / denom
        intersection = P1 + t * line_dir
        
        # Check if intersection point is within the rectangle
        # Project the point onto the rectangle's plane and check barycentric coordinates
        u = np.dot(intersection - P0, v1) / np.dot(v1, v1)
        v = np.dot(intersection - P0, v2) / np.dot(v2, v2)
        
        if 0 <= u <= 1 and 0 <= v <= 1:
            return intersection
        else:
            return None

    @classmethod
    def map_2D_coords_to_3D(cls, widget: "GL3DViewWidget", x: float, y: float):
        widget_width = widget.width()
        widget_height = widget.height()
        device_pixel_ratio = widget.window().screen().devicePixelRatio()
    
        ndc_x = x / widget_width
        ndc_y = y / widget_height

        viewport = GL.glGetIntegerv(GL.GL_VIEWPORT)
        
        _, _, viewport_width, viewport_height = viewport

        mouse_x_physical = ndc_x * viewport_width
        mouse_y_physical = ndc_y * viewport_height
        mouse_y_physical = viewport_height - mouse_y_physical 
        
        
        gl_px_width, gl_px_height = 1, 1
        
        depth = GL.glReadPixels(int(mouse_x_physical), int(mouse_y_physical), gl_px_width, gl_px_height, GL.GL_DEPTH_COMPONENT, GL.GL_FLOAT)[0][0]
        modelview = np.array(widget.viewMatrix().data()).reshape(4, 4)
        projection = np.array(widget.projectionMatrix(viewport, (0, 0, device_pixel_ratio * widget_width, device_pixel_ratio* widget_height)).data()).reshape(4, 4)
        depth = 0.
        world_x, world_y, world_z = GLU.gluUnProject(mouse_x_physical, mouse_y_physical, depth, modelview, projection, viewport)
        return world_x, world_y, world_z

    @classmethod
    def map_3D_coords_to_2D(cls, widget, world_x, world_y, world_z):
        device_pixel_ratio = widget.window().screen().devicePixelRatio()
        widget_height = widget.height()
        widget_width = widget.width()
        
        viewport = GL.glGetIntegerv(GL.GL_VIEWPORT)
        _, _, viewport_width, viewport_height = viewport
        
        modelview = np.array(widget.viewMatrix().data()).reshape(4, 4)
        projection = np.array(widget.projectionMatrix(viewport,
                                                     (0, 0, device_pixel_ratio * widget_width, device_pixel_ratio * widget_height)).data()).reshape(4, 4)
        
        px_x, px_y, px_z = GLU.gluProject(world_x, world_y, world_z, modelview, projection, viewport)
        px_y = viewport_height - px_y
        return px_x, px_y, px_z
    
    def FacingVerticesPx(self):
        closest_faces = self.closestFaces()
        view_widget = self.parentWidget()

        ax_boundingRectPx = []
        for ax, face in enumerate(closest_faces):
            vertexCoords = self.state["vertexCoordinates"][ax][face]
            screen_coords = []
            for coord in vertexCoords:
                x_px, y_px, z_px = self.map_3D_coords_to_2D(view_widget, *coord)
                screen_coords.append([x_px, y_px])
                
            ax_boundingRectPx.append(screen_coords)

        ax_boundingRectPx = np.array(ax_boundingRectPx).round(4).tolist()
        return ax_boundingRectPx

    def extendPoint(self, p1, p2):
        p2_new = [0, 0, 0]
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        dz = p2[2] - p1[2]
        d = (dx**2 + dy**2 + dz**2)**0.5    
        dNew = 2 * self.parentWidget().opts["distance"]
        p2_new[0] = p1[0] + dx / d * dNew
        p2_new[1] = p1[1] + dy / d * dNew
        p2_new[2] = p1[2] + dz / d * dNew
        return p1, p2
    
    def findIntersectingAxis(self, p1, p2):
        p1, p2 = self.extendPoint(p1, p2)
        closest_faces = self.closestFaces()
        vertexCoordinates = self.state["vertexCoordinates"]
        intersectionAxis = None
        intersectingPoint = None
        for ax in range(3):
            face_side = closest_faces[ax]
            rect = vertexCoordinates[ax][face_side]
            intersection = GL3DViewBox.line_rectangle_intersection(p1, p2, rect)
            if not intersection is None:
                intersectionAxis=ax
                intersectingPoint=intersection
                break
        
        return intersectionAxis, intersectingPoint

    def screen_coords(self, world_coordinates):
        if len(world_coordinates) == 3:
            world_coordinates = np.append(world_coordinates, 1)
        mvp = self.parentWidget().currentProjection() * self.parentWidget().currentModelView()  
        return np.array(mvp.data()).reshape(4, 4) @ world_coordinates
            
    def closestFaces(self):
        cameraPosition = self.parentWidget().cameraPosition()
        worldRange = self.state["worldRange"]
        pos = cameraPosition.x(), cameraPosition.y(), cameraPosition.z()

        faces = []
        for ax in range(3):
            ax_l, ax_p = worldRange[ax]
            p = pos[ax]
            ax_face = 0 if (p - ax_l) < (ax_p - p) else 1
            faces.append(ax_face)
        return faces

    def get_cube_face2(self, worldRange):
        axis_px_rect = []
        
        for ax in range(3):
            
            inner_rect = []
            for ax_lim in worldRange[ax]:
                wr_i = np.delete(worldRange, ax, axis=0)
                point = [np.insert([wr_i[i][j], wr_i[j][i]], ax, ax_lim) for j in range(2) for i in range(2)]
                inner_rect.append(point)
            axis_px_rect.append(inner_rect)
                
        return axis_px_rect

    def _childPaint(self):...
    
    def _paintHelper(self):... 

    def get_cube_face(self, worldRange):
        axis_px_rect = []
        
        for ax in range(3):
            # Get the other two axes (e.g., if ax=0 (x), then other_axes=[1,2] (y,z))
            other_axes = [i for i in range(3) if i != ax]
            ax1, ax2 = other_axes
            
            inner_rect = []
            for ax_lim in worldRange[ax]:  # min and max of current axis
                # Get min/max for the other two axes
                ax1_min, ax1_max = worldRange[ax1]
                ax2_min, ax2_max = worldRange[ax2]
                
                # Generate the 4 vertices of this face
                # (No longer using 'j' inside a comprehension)
                face_vertices = [
                    [ax_lim, ax1_min, ax2_min],  # Vertex 1
                    [ax_lim, ax1_max, ax2_min],  # Vertex 2
                    [ax_lim, ax1_max, ax2_max],  # Vertex 3
                    [ax_lim, ax1_min, ax2_max],  # Vertex 4
                ]
                
                # Reorder axes to match original structure (x,y,z)
                # (Since we hardcoded ax1, ax2, we need to restore the correct order)
                ordered_face = []
                for vertex in face_vertices:
                    # Reconstruct the vertex in x,y,z order
                    new_vertex = [0, 0, 0]
                    new_vertex[ax] = vertex[0]          # Fixed axis (ax_lim)
                    new_vertex[ax1] = vertex[1]         # First other axis
                    new_vertex[ax2] = vertex[2]         # Second other axis
                    ordered_face.append(new_vertex)
                
                inner_rect.append(ordered_face)
            
            axis_px_rect.append(inner_rect)
        
        return axis_px_rect
    
    def userInteracting(self): return self.mouse_state.keyInteracting()
    
    
    
def window_to_world_ray(view: "GL3DViewWidget", wx: float, wy: float):
    """Convert a window point (wx, wy) to a 3D ray (origin, direction) in world space."""
    # Get modelview and projection matrices
    modelview = view.viewMatrix()
    projection = view.projectionMatrix()

    # Compute the inverse of (projection * modelview)
    mvp = projection @ modelview
    inv_mvp = np.linalg.inv(mvp)

    # Convert window coordinates to normalized device coordinates (NDC)
    # Note: PyQtGraph uses Qt's coordinate system where Y increases downward.
    # So, we may need to flip Y if necessary.
    width, height = view.width(), view.height()
    ndc_x = (2.0 * wx) / width - 1.0
    ndc_y = 1.0 - (2.0 * wy) / height  # Flip Y to match OpenGL NDC

    # Near and far points in NDC
    near_ndc = np.array([ndc_x, ndc_y, -1.0, 1.0])  # z = -1 (near plane)
    far_ndc = np.array([ndc_x, ndc_y, 1.0, 1.0])    # z = 1 (far plane)

    # Transform to world coordinates
    near_world = inv_mvp @ near_ndc
    near_world /= near_world[3]  # Perspective divide

    far_world = inv_mvp @ far_ndc
    far_world /= far_world[3]

    # Ray origin and direction
    origin = near_world[:3]
    direction = far_world[:3] - origin
    direction /= np.linalg.norm(direction)  # Normalize

    return origin, direction
       

def ray_intersects_cube(origin, direction, cube_bounds):
    """Check if a ray intersects a cube defined by [[xmin, xmax], [ymin, ymax], [zmin, zmax]]."""
    tmin = -np.inf
    tmax = np.inf
    
    for i in range(3):  # Check x, y, z axes
        if np.abs(direction[i]) < 1e-6:  # Ray parallel to slab
            if origin[i] < cube_bounds[i][0] or origin[i] > cube_bounds[i][1]:
                return False
        else:
            t1 = (cube_bounds[i][0] - origin[i]) / direction[i]
            t2 = (cube_bounds[i][1] - origin[i]) / direction[i]
            tmin = max(tmin, min(t1, t2))
            tmax = min(tmax, max(t1, t2))
    
    return tmax >= tmin and tmax >= 0  # Intersection exists and is in front of the camera

def is_window_point_inside_cube(view: "GL3DViewWidget", wx: float, wy: float, cube_bounds):
    """Check if the window point (wx, wy) is inside the cube."""
    origin, direction = window_to_world_ray(view, wx, wy)
    return ray_intersects_cube(origin, direction, cube_bounds)