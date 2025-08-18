from __future__ import annotations 
from typing import List, Optional, Tuple, Union, Dict, TYPE_CHECKING, Callable, Any
if TYPE_CHECKING:
    from uuid import uuid4
    from ...interfaces.custom_widgets import CustomPlotDataItem
    from ..graphics_items.GL3DAxisItem import GL3DAxisItem
    from pyvol_terminal.gl_3D_graphing.graphics_items.GL3DViewBox import GL3DViewBox
    
import numpy as np
from pyqtgraph import opengl
from PySide6 import QtGui, QtCore, QtWidgets
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from ..graphics_items.GL3DPlotDataItemMixin import BaseGL3DPlotDataItemMixin
from ..graphics_items import GL3DViewBox
import math
from OpenGL import GL
from OpenGL import GLU
import weakref
from pyqtgraph.Qt import isQObjectAlive
from OpenGL.GL import glEnable, GL_DEPTH_TEST
from pyqtgraph import ButtonItem, icons, Vector
from pprint import pprint
import warnings
import time

class GLButtonitem(QtWidgets.QPushButton):
    def __init__(self, plotitem_widget: QOpenGLWidget, *args, **kwargs):
        icon_pixmap = icons.getGraphPixmap('auto')
        super().__init__(plotitem_widget)
        self.setIcon(QtGui.QIcon(icon_pixmap))
        self.setIconSize(QtCore.QSize(30, 30))
        self.setFixedSize(30, 30)
        self.setStyleSheet("""
                            QPushButton {
                                background: transparent;
                                border: none;
                            }
                            QPushButton:hover {
                                background: rgba(200, 200, 200, 100);
                                border-radius: 5px;
                            }
                            """)
                        
        self.updatePosition()
        plotitem_widget.resized.connect(self.updatePosition)

    @QtCore.Slot()
    def updatePosition(self):
        parent = self.parent()
        if parent:
            parent_size = parent.size()
            x = 5
            y = parent_size.height() - self.height() - 5
            self.move(x, y)
            
    
class GL3DViewWidget(opengl.GLViewWidget):    
    sigPrepareForPaint = QtCore.Signal()
    sigViewAngleChanged = QtCore.Signal(object)
    
    def __init__(self,
                 parent : QtCore.QObject | None = None,
                 viewBox: GL3DViewBox | None = None,
                 axisItems: dict[str, GL3DAxisItem] | None = None,
#                 defaultWorldRange:Tuple[Tuple[float, float], ...]|None=None,
                 axis_relative_lengths: Tuple[float, float, float]=(1,1,1),
                 padding=[0, 0, 0],
                 **kwargs
                 ):
        self.vb=None
        self.custom_modifier = QtCore.QKeyCombination(QtCore.Qt.KeyboardModifier.ControlModifier | QtCore.Qt.KeyboardModifier.ShiftModifier | QtCore.Qt.KeyboardModifier.AltModifier)
        self.key_sec = QtGui.QKeySequence(QtCore.Qt.KeyboardModifier.ControlModifier, QtCore.Qt.KeyboardModifier.ShiftModifier, QtCore.Qt.KeyboardModifier.AltModifier)
        print(parent)
        super().__init__(parent=parent)
        
        defaultWorldRange = ((0.,1.), (0., 1.), (0., 1.))
        
        self.opts.update({"cachedPosition" : None})
        
        self._initView(viewBox, axis_relative_lengths)
        
        self._mouseZoomFactor=0.999
        
        self._zoomingWorld=False
        self._zoomingAxis=False
        self._update_axis_ms=100
        self._update_interval = 50 
        self._last_update_time = 0
        
        self.mouse_info={"mouseAlongAxisPos" : None,
                         "prevmouseAlongAxisPos" : None,
                         "intersectedAxis" : None
                         }
        
        if isinstance(padding, (int, float)):
            padding = [float(padding)]*3
            
        self.axes: Dict[str, List[GL3DAxisItem]] = {i : [] for i in range(3)}
        
        self.opts.update({#"azimuth" : -50,
                          "azimuth" : -45,#45,
                          "distance" : 10,
                          "center" : QtGui.QVector3D(0, 1, 0),
                          #"elevation": -30
                          #"center" : QtGui.QVector3D(0, 0, 0)}
                     #     "elevation" : 0,
                          })
        
        self.opts3D = {"queuedViewUpdate" : False,
                       }
        
        self.setAxisItems(axisItems)

        self.id_map: Dict[uuid4, 'BaseGL3DPlotDataItemMixin'|'CustomPlotDataItem']={}
        self.text_items={ax : {} for ax in "xyz"}
    
        self.autoBtn = GLButtonitem(self, icons.getGraphPixmap('auto'), 15)
        self.autoBtn.setMouseTracking(True)
        self.autoBtn.clicked.connect(self.autoBtnClicked)
      
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if not self.autoBtn is None:
            self.autoBtn.updatePosition()

    @QtCore.Slot()
    def autoBtnClicked(self):
        self.vb.enableAutoRange(enable=True)
        self.vb.sigRangeChangedManually.emit(self.vb.mouseEnabled()[:])

    def _initView(self, viewBox, relative_axis_lengths):
        worldRange = tuple((0, length) for length in relative_axis_lengths)
        if viewBox is None:
            viewBox = GL3DViewBox.GL3DViewBox(worldRange=worldRange)
        self.vb = viewBox
        self.vb.setParentWidget(self)
        super().addItem(self.vb)
        
        self._cameraPosArr = np.array([0., 0., 0.])
        self._centerPosArr = np.array([0., 0., 0.])    

    def initializeGL(self):
        super().initializeGL()
        glEnable(GL_DEPTH_TEST)  

    def create_border(self):
        
        worldRange = self.vb.state["worldRange"]

        corners = np.array([[0, 0, 0], 
                            [1, 0, 0],  
                            [1, 1, 0], 
                            [0, 1, 0]
                            ])
        
        corners = np.array([[worldRange[0][0], worldRange[1][0], worldRange[2][0]],
                           [worldRange[1][1], worldRange[1][0], worldRange[2][0]],
                           [worldRange[1][1], worldRange[1][1], worldRange[2][0]],
                           [worldRange[0][0], worldRange[1][1], worldRange[2][0]]]
                           )

        segments = np.vstack([corners[i] for i in range(4) for _ in (0, 1)])
        
        
      #  segments = [[x, y, z] for z in worldRange[0] for y in worldRange[1] for x in worldRange[2]]
        segments[1::2] = np.roll(corners, -1, axis=0)  
        
        self._borders=[]
        borderline = opengl.GLLinePlotItem(pos=segments,
                                           color=(130,130,130,130),
                                           glOptions="translucent",
                                           mode="lines"
                                           )
        self._borders.append(borderline)
        super().addItem(borderline)
        
    def compute_optimal_clipping(self):
        largest_point_distance = np.sqrt(3)
        near_clip = max(0.0001, self.opts['distance'] - 1.01 * largest_point_distance) 
        far_clip = self.opts['distance'] 
        return near_clip, far_clip

    def prepareForPaint(self):     
        self.sigPrepareForPaint.emit()
        return 
    
    def paintGL(self):
        self.prepareForPaint()
        return super().paintGL()
                    
    def addItem(self, item, ignoreBounds=False):
        if ignoreBounds:
            super().addItem(item)
        else:
            if not self.vb is None:
                self.vb.addItem(item, ignoreBounds=ignoreBounds)
            else:
                super().addItem(item)
            
    def removeItem(self, item):
        if item.parentItem() == self.vb.childGroup:
            self.vb.removeItem(item)
        else:
            super().removeItem(item)

    def setAxisItems(self, axisItems: 'List[GL3DAxisItem] | None' = None) -> None:
        if axisItems is None:
            axisItems = []
        
        for axis in axisItems:
            origin = axis.geometry["worldOrigin"]
            direction = axis.geometry["axis"]
            
            if direction in self.axes:
                for oldAxis in self.axes[direction]:
                    if all(((np.array(oldAxis.geometry["worldOrigin"]) == origin).all(),
                            (oldAxis.geometry["axisFace"] == np.array(axis.geometry["axisFace"])).all()
                            )):
                        oldAxis.unlinkFromView()
                        self.removeItem(oldAxis)
                        self.axes[direction].remove(oldAxis)

            self.axes[direction].append(axis)
            axis.linkToView(self.vb)
            super().addItem(axis)

    def showAxis(self, axis_direction_coords: Tuple[int, Tuple[float, float, float]], show: bool=True):
        s = self.getScale(axis_direction_coords)
        """
        if show:
            s.show()
        else:
            s.hide()
        """

    def getScale(self, axis_direction_coords: Tuple[Tuple[float, float, float], Tuple[int, int]]):
        return self.getAxis(*axis_direction_coords)
    
    def getAxis(self, direction: int, axis_specs: Tuple[Tuple[float, float, float], Tuple[int, int]]=None) -> List[GL3DAxisItem]:
        """
        Return the specified AxisItem.

        Parameters
        ----------
        direction : {0, 1, 2}
            Axis direction of the axis to return.
            
        orthogonalVertices : If origin O of is 0,0,0 of the unit-view, then the x-axis with plane (xy) that goes along x: 0 to 1 with z==0
                                would have the orthogalVertices: {'direction' : (1, 0, 0),
                                                                  'planeDirection' : (0, 1, 0),
                                                                  'perpendicularDirection : (0, 0, 1)
                                                                  }
                                

 
        Returns
        -------
        AxisItem
            The :class:`~GLAxisItem`.

        Raises
        ------
        KeyError
            If the specified axis is not present.
        """
        if direction in self.axes:
            if axis_specs is None:
                return self.axes[direction]
            for ax in self.axes[direction]: 
                if all([p1 == p2 for p1, p2 in zip(ax.geometry["worldOrigin"], axis_specs[0])]) and all([p1 == p2 for p1, p2 in enumerate(axis_specs[1]) if p1 != ax.geometry["axisOrtho"]]):
                    return ax
        raise ValueError(f"Axis with direction {direction} and vertices {axis_specs} is not in the widget")
    
    
    def mousePressEvent(self, ev):
        super().mousePressEvent(ev)
        self.vb.mousePressEvent(ev)

    def mouseReleaseEvent(self, ev):
        self.vb.mouseReleaseEvent(ev)

    def mouseMoveEvent(self, ev):
        if self.vb.userInteracting():
            self.vb.mouseMoveEvent(ev)
        else:
            super().mouseMoveEvent(ev)
        
    @classmethod
    def zoom_2d(cls, point, drag, viewRange, base=1.1):
        axis_mins = np.array([vr[0] for vr in viewRange])
        axis_maxs = np.array([vr[1] for vr in viewRange])

        scales = base ** -drag
        
        new_axis_mins = scales * axis_mins + (1 - scales) * point
        new_axis_maxs = scales * axis_maxs + (1 - scales) * point
        return [[new_min, new_max] for new_min, new_max in zip(new_axis_mins, new_axis_maxs)]


    def cameraPositionNumpy(self):
        p = self.cameraPosition()
        self._cameraPosArr[:] = p.x(), p.y(), p.z()
        return self._cameraPosArr
    
    def centerPositionNumpy(self):
        p = self.opts['center']
        self._centerPosArr[:] = p.x(), p.z(), p.z()
        return self._centerPosArr


    @classmethod
    def map_2D_coords_to_3D(cls, widget: GL3DViewWidget, x: float, y: float):
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
        
        depth = GL.glReadPixels(int(mouse_x_physical), int(mouse_y_physical), 1, 1, GL.GL_DEPTH_COMPONENT, GL.GL_FLOAT)[0][0]

        modelview = np.array(widget.viewMatrix().data()).reshape(4, 4)
        projection = np.array(widget.projectionMatrix(viewport, (0, 0, device_pixel_ratio * widget_width, device_pixel_ratio* widget_height)).data()).reshape(4, 4)
        
        world_x, world_y, world_z = GLU.gluUnProject(mouse_x_physical, mouse_y_physical, depth, modelview, projection, viewport)

        return world_x, world_y, world_z
    
    def cameraPosition(self, opts=None):
        if opts is None:
            cachedPosition = self.opts["cachedPosition"]
            if cachedPosition is None:
                return super().cameraPosition()
            else:
                return cachedPosition
        else:
            "Getting camera position given opts"
            old_opts = self.opts.copy()
            self.opts = opts
            pos = super().cameraPosition()
            self.opts = old_opts
            return pos

    def cameraTuple(self):
        center = self.opts['center']
        dist = self.opts['distance']
        if self.opts['rotationMethod'] == "quaternion":
            camera = center - self.opts['rotation'].rotatedVector(Vector(0, 0, dist) )
            return camera.x(), camera.y(), camera.z()
        else:
            elev = math.radians(self.opts['elevation'])
            azim = math.radians(self.opts['azimuth'])
            
        return center.x() + dist * math.cos(elev) * math.cos(azim), center.y() + dist * math.cos(elev) * math.sin(azim), center.z() + dist * math.sin(elev)

    def points_intersect_axis(size, start, end):
        
        ndx = start[0] - end[0]
        ndy = start[1] - end[1]
        ndz = start[2] - end[2]

        sxy = ndx * size[1]
        sxz = ndx * size[2]
        syx = ndy * size[0]
        syz = ndy * size[2]
        szx = ndz * size[0]
        szy = ndz * size[1]

        cxy = end[0]*start[1] - end[1]*start[0]
        cxz = end[0]*start[2] - end[2]*start[0]
        cyz = end[1]*start[2] - end[2]*start[1]

        axy = abs(ndx*ndy)
        axz = abs(ndx*ndz)
        ayz = abs(ndy*ndz)
 
        face_num = 0
        axis=None
        face_tau = abs(ndz*axy)

        if start[0] < 0 and 0 < end[0]:
            tau = -start[0] * ayz
            if tau < face_tau and cxy >= 0 and cxz >= 0 and cxy <= -sxy and cxz <= -sxz:
                face_tau = tau
                face_num = 1
                axis=0

        elif end[0] < size[0] and size[0] < start[0]:
            tau = (start[0] - size[0]) * ayz
            if tau < face_tau and cxy <= syx and cxz <= szx and cxy >= syx - sxy and cxz >= szx - sxz:
                face_tau = tau
                face_num = 2
                axis=0

        if start[1] < 0 and end[1] > 0:
            tau = -start[1] * axz
            if tau < face_tau and cxy <= 0 and cyz >= 0 and cxy >= syx and cyz <= -syz:
                face_tau = tau
                face_num = 3
                axis=1

        elif start[1] > size[1] and end[1] < size[1]:
            tau = (start[1] - size[1]) * axz
            if tau < face_tau and cxy >= -sxy and cyz <= szy and cxy <= syx - sxy and cyz >= szy - syz:
                face_tau = tau
                face_num = 4
                axis=1

        if start[2] < 0 and end[2] > 0:
            tau = -start[2] * axy
            if tau < face_tau and cxz <= 0 and cyz <= 0 and cxz >= szx and cyz >= szy:
                face_tau = tau
                face_num = 5
                axis=2

        elif start[2] > size[2] and end[2] < size[2]:
            tau = (start[2] - size[2]) * axy
            if tau < face_tau and cxz >= -sxz and cyz >= -syz and cxz <= szx - sxz and cyz <= szy - syz:
                face_tau = tau
                face_num = 6
                axis=2

        if face_num > 0:
            return axis
        else:
            return None
        
    def points_intersect_axis_points(size, start, end):
        ndx = start[0] - end[0]
        ndy = start[1] - end[1]
        ndz = start[2] - end[2]

        sxy = ndx * size[1]
        sxz = ndx * size[2]
        syx = ndy * size[0]
        syz = ndy * size[2]
        szx = ndz * size[0]
        szy = ndz * size[1]

        cxy = end[0]*start[1] - end[1]*start[0]
        cxz = end[0]*start[2] - end[2]*start[0]
        cyz = end[1]*start[2] - end[2]*start[1]

        axy = abs(ndx*ndy)
        axz = abs(ndx*ndz)
        ayz = abs(ndy*ndz)
        axyz = abs(ndz*axy)

        face_num = 0
        face_tau = abs(ndz*axy)

        if start[0] < 0 and 0 < end[0]:
            tau = -start[0] * ayz
            if tau < face_tau and cxy >= 0 and cxz >= 0 and cxy <= -sxy and cxz <= -sxz:
                face_tau = tau
                face_num = 1

        elif end[0] < size[0] and size[0] < start[0]:
            tau = (start[0] - size[0]) * ayz
            if tau < face_tau and cxy <= syx and cxz <= szx and cxy >= syx - sxy and cxz >= szx - sxz:
                face_tau = tau
                face_num = 2

        if start[1] < 0 and end[1] > 0:
            tau = -start[1] * axz
            if tau < face_tau and cxy <= 0 and cyz >= 0 and cxy >= syx and cyz <= -syz:
                face_tau = tau
                face_num = 3

        elif start[1] > size[1] and end[1] < size[1]:
            tau = (start[1] - size[1]) * axz
            if tau < face_tau and cxy >= -sxy and cyz <= szy and cxy <= syx - sxy and cyz >= szy - syz:
                face_tau = tau
                face_num = 4

        if start[2] < 0 and end[2] > 0:
            tau = -start[2] * axy
            if tau < face_tau and cxz <= 0 and cyz <= 0 and cxz >= szx and cyz >= szy:
                face_tau = tau
                face_num = 5

        elif start[2] > size[2] and end[2] < size[2]:
            tau = (start[2] - size[2]) * axy
            if tau < face_tau and cxz >= -sxz and cyz >= -syz and cxz <= szx - sxz and cyz <= szy - syz:
                face_tau = tau
                face_num = 6

        if face_num > 0:
            tend = face_tau / axyz
            tstart = 1.0 - tend
            return np.round((tstart*start[0]+tend*end[0], tstart*start[1]+tend*end[1], tstart*start[2]+tend*end[2]),6)
        else:
            return None
        
    
        
    def wheelEvent(self, ev):
        if self.vb.userInteracting():
            self.vb.wheelEvent(ev)
        else:
            super().wheelEvent(ev)
            
    def get_unzoom_transform(self):
        """
        Returns a QMatrix4x4 that would visually undo the current zoom level.
        The inverse of the current zoom transformation.
        """
        # Calculate current zoom factor (assuming distance is inversely proportional to zoom)
        # If distance decreases, zoom increases, and vice versa
        base_distance = 4.0  # Reference distance where zoom=1.0
        current_zoom = base_distance / self.opts['distance']
        unzoom_matrix = QtGui.QMatrix4x4()
        unzoom_matrix.scale(current_zoom / 1.0)
        return unzoom_matrix

    def orbit(self, azim, el):
        if azim != 0 and el!= 0:
            self.sigViewAngleChanged.emit(self)
            self.opts["cachedPosition"]=None
        super().orbit(azim, el)

    
    def _outsideBox(self, opts):
        if any([self.vb.state["worldRange"][idx][1] <= pos for idx, pos in enumerate(self.cameraPosition(opts))]):
            return True
        else:
            return False
        
    def _checkCartesianBounds(self, coords):
        return [self.vb.state["worldRange"][i][0] <= coords[i] < self.vb.state["worldRange"][i][1] for i in range(3)]


    def _emit_view_changed(self):
        self._last_update_time = QtCore.QTime.currentTime().msecsSinceStartOfDay()
        self._pending_update = False
        self.viewChangedSignal.emit(self)
        
                
                
    def _delayed_view_update(self):
        if self._pending_update:
            self._emit_view_changed()
        
    def simulateKeys(self, ctrl=False, shift=False):
        """Programmatically set key states"""
        self._ctrl_pressed = ctrl
        self._shift_pressed = shift
        self.update()

    def keyPressEvent(self, ev):
        self.vb.keyPressEvent(ev)
        super().keyPressEvent(ev)

    def keyReleaseEvent(self, ev):
        self.vb.keyPressEvent(ev)
        super().keyReleaseEvent(ev)

    def focusOutEvent(self, event):
        self.vb.focusOutEvent(event)
        super().focusOutEvent(event)  # Call parent method
    

    def queuedViewUpdate(self): return self.opts3D["queuedViewUpdate"]
    
    
    