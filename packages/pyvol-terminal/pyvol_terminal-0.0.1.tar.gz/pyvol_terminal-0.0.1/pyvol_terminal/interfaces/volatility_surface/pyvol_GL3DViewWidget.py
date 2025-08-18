from __future__ import annotations 
from typing import List, Optional, Tuple, Union, Dict, TYPE_CHECKING, Callable
if TYPE_CHECKING:
    from ...gl_3D_graphing.graphics_items.GL3DGraphicsItems import GL3DSurfacePlotItem, GL3DScatterPlotItem
    from .pyvol_GL3DGraphicsItems import ABCPyVolPlotItemMixin

    
import numpy as np
from pyqtgraph import opengl 
from PySide6 import QtCore, QtGui
from . import utils as utils_volatility_surface
from ... import utils
from pyvol_terminal import misc_widgets
from ...gl_3D_graphing.graphics_items import GL3DGraphicsItems
from pyqtgraph import functions as fn
import math
import pyqtgraph as pg
from ...gl_3D_graphing.widgets.GL3DViewWidget import GL3DViewWidget
from .pyvol_GL3DGraphicsItems import PyVolGL3DScatterPlotItem, PyVolGL3DSurfacePlotItem, PyVolLineItem
import traceback
import time


class PyVolGL3DViewWidget(GL3DViewWidget):    
    rcMapCoordsSig = QtCore.Signal(float, float, float)
    hoverSurfaceSig = QtCore.Signal(float, float, float)
    viewChangedSig = QtCore.Signal(object)
    intenseInteractionEnded = QtCore.Signal()
    
    def __init__(self,
                 spot_text=None,
                 padding=None,
                 queue_interaction: bool=True,
                 **kwargs
                 ):
        if padding is None:
            padding = [0, 0, 0]
        
        self.spot_objects = kwargs.pop("spot_objects", None)
        parent=kwargs.pop("parent", None),
        print(kwargs.keys())
        super().__init__(padding=padding, **kwargs)
        self._mv_handle_interaction_state=None
        self.spot_text=spot_text
        self._cartesian_view_coords = np.array([0., 0., 0.])
        self.queue_interaction=queue_interaction

            
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
        self.setMouseTracking(True)
        self.setAttribute(QtCore.Qt.WA_Hover)

        self.show_spot_text=True
        self.surface_flag=True
        self.scatter_flag=True
        self.surface_visibility={}
        self.spot_text_dict={}
        self.displayed_price_types=[]
        self.surface_plotitems: Dict[str, PyVolGL3DSurfacePlotItem]={}
        self.scatter_plotitems: Dict[str, PyVolGL3DScatterPlotItem]={}
        self._mouseDrag=False
        self._normalising_data={}
        self.plot_items_by_attr = {}
        self.plotted_price_types=[]
        self._displayed_price_type_counter={}
        self.cross_hairs_on=False
        self.text_color = (0, 0, 0, 255)
        self.bg_color = (255, 255, 255, 200)
        self.cross_hairs_enabled=True
        self._mouseZoomFactor=0.999
        
        near_clip, far_clip = self.compute_optimal_clipping()
        
        distance = 4
        azimuth = -90
        elevation = 30
        
        
        self._intense_interacting = False
        
        
        self.opts['near'] = near_clip
        self.opts['far'] = far_clip
        self.opts["distance"] = distance
        self.opts['azimuth'] = azimuth
        self._azimuth_offset = 90
        self._elevation_offset = 90
        
        self.opts["elevation"] = elevation
        self.opts["center"] = QtGui.QVector3D(0, 1, 0)

        self._spherical_bounds = {"azimuth" : [-90, 0],
                                  "elevation" : [0, 90]}
        self.prev_euler_coords = {"distance" : distance,
                                  "azimuth" : azimuth,
                                  "elevation" : elevation}

        self._bounds_cartesian = [[0, 1], [0, 1], [0, 1]]

        
        self.first_plot=True
        self.plot_interaction_buffer=[] 
        self.any_valid_surface=False
        self.price_updated_callbacks=[]
        self._plot_items: List[PyVolLineItem]=[]

        self.prev_x, self.prev_y, self.prev_z = None, None, None
        self.addPlots_callbacks=[]
        self.RemovePlots_callbacks=[]
        
        self._last_update_time = 0
        self._update_interval = 50  # ms between updates
        self._pending_update = False

        self.hoverSurfaceSig.connect(self._update_crosshairs)
        self._cartesian_view_coords = self.cameraPositionVector()
        
        self.scroll_delay = None
        if self.queue_interaction:
            self.scroll_delay = 200
            self._mouseScroll=False
            self.scroll_timer = QtCore.QTimer()
            self.scroll_timer.setSingleShot(True)
            self.scroll_timer.timeout.connect(self._processMouseZoom)
            
        self.setup_mouse_interaction()
        self._init_crosshairs()
        
        self.top_surface: PyVolGL3DSurfacePlotItem=None
        self.add_legend()    

    def wheelEvent(self, ev):
        if self.queue_interaction:
            self._mouseScroll=True
            self._internalCheckIntenseInteraction()
            self.scroll_timer.start(self.scroll_delay)
        return super().wheelEvent(ev)
    
    def _processMouseZoom(self):
        self._mouseScroll=False
        self._internalCheckIntenseInteraction()
  
    def plotItem(self,
                 internal_id
                 ) -> ABCPyVolPlotItemMixin:
        return self.id_map.get(internal_id, None)
    
    def append_addPlots_callbacks(self, callback):
        self.addPlots_callbacks.append(callback)

    def append_removePlots_callbacks(self, callback):
        self.RemovePlots_callbacks.append(callback)

    def repaint_spot(self):
        painter = QtGui.QPainter(self)
        painter.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.TextAntialiasing)
        
        margin = 10
        spot_text=str(self.spot_text)
        text_rect = painter.boundingRect(self.rect(), 
                                         QtCore.Qt.AlignTop | QtCore.Qt.AlignRight | QtCore.Qt.TextDontClip, 
                                         spot_text
                                        )
        text_rect.moveTopRight(self.rect().topRight() - QtCore.QPoint(margin, -margin))
        
        painter.setBrush(QtGui.QColor(*self.bg_color))
        painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0, 200), 1))
        painter.drawRect(text_rect.adjusted(-5, -2, 5, 2))
        painter.setPen(QtGui.QColor(*self.text_color))
        painter.drawText(text_rect, QtCore.Qt.AlignCenter, spot_text)
        painter.end()
        
    @property
    def top_surface(self) -> PyVolGL3DSurfacePlotItem:
        return self._top_surface
    
    @top_surface.setter
    def top_surface(self, surfaceItem: PyVolGL3DSurfacePlotItem):
        self.line_xz.setParentItem(surfaceItem)
        self.line_yz.setParentItem(surfaceItem)
        self._top_surface = surfaceItem

    def get_top_price_type(self):
        if "ask" in self.surface_plotitems:
            self.top_surface = self.surface_plotitems["ask"]
        elif "mid" in self.surface_plotitems:
            self.top_surface = self.surface_plotitems["mid"]
        elif "bid" in self.surface_plotitems:
            self.top_surface = self.surface_plotitems["bid"]
        
    def update_surface_state(self, gl_plot_item: PyVolGL3DSurfacePlotItem):
        self.surface_visibility[gl_plot_item.id()] = gl_plot_item.valid_values
        self.any_valid_surface = any(self.surface_visibility.values())
                    
    def plotitem_from_attr(self, px_type, plot_type):
        return self.plot_items_by_attr[px_type][plot_type]
    
    def _add_to_plot_data_item_dicts(self, item: PyVolLineItem):
        self._normalising_data[item.id()]=False
        if item.px_type in self._displayed_price_type_counter:
            self._displayed_price_type_counter[item.px_type]+=1
        else:
            self._displayed_price_type_counter[item.px_type]=1

    def addItem(self, item, ignoreBounds=False, **kwargs):
        if isinstance(item, PyVolLineItem):
            self._plot_items.append(item)
        
        if isinstance(item, (PyVolGL3DSurfacePlotItem, PyVolGL3DScatterPlotItem)):
            container = self.surface_plotitems if isinstance(item, PyVolGL3DSurfacePlotItem) else self.scatter_plotitems
            container[item.px_type] = item
            self._add_to_plot_data_item_dicts(item)
            self.legend.add_legend_item(item.px_type, item.color)
            self.id_map[item.id()] = item
            
            if isinstance(item, PyVolGL3DSurfacePlotItem):
                self.get_top_price_type()
                item.sigPlotChanged.connect(self.update_surface_state)

        super().addItem(item, ignoreBounds=ignoreBounds, **kwargs)
            
    def removeItem(self, item: ABCPyVolPlotItemMixin):
        if isinstance(item, PyVolLineItem):
            self._plot_items.remove(item)

        if isinstance(item, PyVolGL3DSurfacePlotItem):
            del self.surface_plotitems[item.px_type]
            self.get_top_price_type()
        if isinstance(item, PyVolGL3DScatterPlotItem):
            del self.scatter_plotitems[item.px_type]
            
        if isinstance(item, GL3DGraphicsItems.GL3DScatterPlotItem) or isinstance(item, GL3DGraphicsItems.GL3DScatterPlotItem):
            self.legend.remove_legend_item(item.px_type)
           # del self.plot_items_by_attr[item.px_type][item.item_type]
            self._displayed_price_type_counter[item.px_type]-=1
            if self._displayed_price_type_counter[item.px_type]==0:
                del self._displayed_price_type_counter[item.px_type]
        return super().removeItem(item)
    
    def add_legend(self, legend=None):
        if not legend is None:
            self.legend=legend
        else:
            self.legend=misc_widgets.Legend()
        
    def remove_legend(self):
        if not self.legend is None:
            self.removeItem(self.legend)
            self.legend=None

    def remove_spot_text(self):
        self.show_spot_text = False
        self.spot_text = ""
        self.update()
        
    def toggle_crosshairs(self, check, on_off):
        print(check)
        if on_off == "On":
            enable=True
        else:
            enable=False
        self.cross_hairs_enabled=enable
        if not enable:
            self.line_xz.hide()
            self.line_yz.hide()
            
    def restore_spot_text(self, text=""):
        self.show_spot_text = True
        self.spot_text = text
        self.update()

    def paintGL3(self, *args, **kwargs):
        super().paintGL(*args, **kwargs)
        if self.show_spot_text and self.spot_text:
            painter = QtGui.QPainter(self)
            self.repaint_spot()
            painter.end()

    def compute_optimal_clipping(self):
        largest_point_distance = np.sqrt(2)
        near_clip = max(0.0001, self.opts['distance'] - 1.01 * largest_point_distance) 
        far_clip = self.opts['distance'] 
        return near_clip, far_clip

    def _init_crosshairs(self):
        self.line_yz = None
        self.line_xz = None
        self.cross_hairs_on = False
        line_xz, line_yz = [np.column_stack([np.linspace(0,1,60)]*3)]*2 , np.column_stack([np.linspace(0,1,60)]*3)
        
        self.line_xz = PyVolLineItem(pos=line_xz,
                                     color=(1, 1, 1, 1),
                                     width=2,
                                     mode='line_strip',
                                     antialias=True
                                     )
        self.line_yz = PyVolLineItem(pos=line_yz,
                                    color=(1, 1, 1, 1),
                                    width=2,
                                    mode='line_strip',
                                    antialias=True
                                    )
        self.line_yz.setGLOptions('translucent')
        self.line_xz.setGLOptions('translucent')
        self.line_yz.hide()
        self.line_xz.hide()

    def setup_mouse_interaction(self):
        self.setMouseTracking(True)
        
        self.mouse_move_timer = QtCore.QTimer(self)
        self.mouse_move_timer.setInterval(50)
        self.mouse_move_timer.timeout.connect(self.process_mouse_move)
        self.mouse_move_timer.start()
        
        self.lastMouseWorldCoords=None
        
    def mousePressEvent(self, event):
        if not self.vb.mouse_state.keyInteracting():
            match event.buttons().value:    
                case 2:
                    self.process_right_click(event.pos().x(), event.pos().y())
        super().mousePressEvent(event)

    def process_right_click(self, screen_x, screen_y):
        self.makeCurrent() 
        world_x, world_y, world_z = utils_volatility_surface.map_2D_coords_to_3D(self, screen_x, screen_y)
        if 0 <= world_x <= 1 and 0 <= world_y <= 1 and 0 <= world_z <= 1:        
            local_coords = self.vb.childGroup.mapFromView(pg.Vector(world_x, world_y, world_z))

            self.prev_x = local_coords.x()
            self.prev_y = local_coords.y()
            self.prev_z = local_coords.z()
            self.rcMapCoordsSig.emit(self.prev_x,
                                     self.prev_y,
                                     self.prev_z)
    
    def hide_crosshairs(self):
        self.cross_hairs_on=False
        self.line_yz.hide()
        self.line_xz.hide()

    def leaveEvent(self, event):
        self.lastMouseWorldCoords=None
        self.hide_crosshairs()
        super().leaveEvent(event)

    def mouseMoveEvent(self, ev):
        self.lastMouseWorldCoords = ev.x(), ev.y()
        if self.queue_interaction and ev.buttons() & QtCore.Qt.LeftButton:
            self._mouseDrag=True
            self._internalCheckIntenseInteraction()
        return super().mouseMoveEvent(ev)
        
    def _delayed_view_update(self):
        if self._pending_update:
            self._emit_view_changed()
            
    def _emit_view_changed(self):
        self._last_update_time = QtCore.QTime.currentTime().msecsSinceStartOfDay()
        self._pending_update = False
        self.viewChangedSig.emit(self)
        
    def _internalCheckIntenseInteraction(self):
        state = self._mouseDrag or self._mouseScroll
        if state != self._intense_interacting:
            self._intense_interacting=state
            self.processIntenseInteraction("view", state)
        
    def mouseReleaseEvent(self, event):
        if self.queue_interaction and self._mouseDrag:
            self._mouseDrag=False
            self._internalCheckIntenseInteraction()
        self._mouseDrag=False
        return super().mouseReleaseEvent(event)
    
    def _update_crosshairs(self, x, y, z):
        vect = pg.Vector(x, y, z)
        vect = self.top_surface.mapFromView(vect)
        
        x, y = vect.x(), vect.y()
        
        if not self.cross_hairs_on:
            self.cross_hairs_on = True
            self.line_yz.show()
            self.line_xz.show()

        line_xz = utils.calculate_xy_lines(*self.top_surface.getValues(),
                                            x_fixed=x,
                                            y_fixed=y,
                                            const_axis=True
                                            )
  
        
        line_yz = utils.calculate_xy_lines(*self.top_surface.getValues(),
                                            x_fixed=x,
                                            y_fixed=y,
                                            const_axis=False
                                            )
        
        line_xz[:,2]*=1.05
        line_yz[:,2]*=1.05
        
        self.line_xz.setData(pos=line_xz)
        self.line_yz.setData(pos=line_yz)
    
    def process_mouse_move(self):
        if (self.cross_hairs_enabled
            and self.any_valid_surface
            and not self.lastMouseWorldCoords is None
            ):
            self.makeCurrent() 
            world_x, world_y, world_z = utils_volatility_surface.map_2D_coords_to_3D(self, *self.lastMouseWorldCoords)
            if 0 <= world_x <= 1 and 0 <= world_y <= 1 and 0 <= world_z <= 1:
                self.hoverSurfaceSig.emit(world_x, world_y, world_z)
            else:
                self.cross_hairs_on=False
                self.line_xz.hide()
                self.line_yz.hide()
            self.lastMouseWorldCoords = None

    def get_legend(self):
        return self.legend

    def get_displayed_price_types(self):
        return self._displayed_price_type_counter


    def zoom(self, rMultiplier):
        distance = self.opts['distance'] * rMultiplier
        opts = {"distance" : distance,
                "elevation" : self.opts["elevation"],
                "azimuth" : self.opts["azimuth"]
                }
        if self._outsideBox(opts):
            self.opts["distance"] = distance
            self.update()
            return True
        else:
            return False

    def cameraPositionVector(self, opts=None) -> np.ndarray[float]:
        if opts is None:
            opts = self.opts

        azimuth = opts["azimuth"] + self._azimuth_offset
        elevation = self._elevation_offset - opts["elevation"]
        self._cartesian_view_coords[0] = opts["distance"] * math.sin(math.radians(elevation)) * math.cos(math.radians(azimuth))
        self._cartesian_view_coords[1] = opts["distance"] * math.sin(math.radians(elevation)) * math.sin(math.radians(azimuth))
        self._cartesian_view_coords[2] = opts["distance"] * math.cos(math.radians(elevation))
        return self._cartesian_view_coords

    def _checkCartesianBounds(self, coords):
        return [self._bounds_cartesian[i][0] <= coords[i] < self._bounds_cartesian[i][1] for i in range(3)]
    
    def _outsideBox(self, opts):
        if any([self._bounds_cartesian[idx][1] <= pos for idx, pos in enumerate(self.cameraPositionVector(opts))]):
            return True
        else:
            return False
        
    def _validAngle(self, azimuth, elevation):
        if (self._spherical_bounds["azimuth"][0] <= azimuth <= self._spherical_bounds["azimuth"][1]
            and self._spherical_bounds["elevation"][0] <= elevation <= self._spherical_bounds["elevation"][1]):
            return True
        else:
            return False
    
    def _validView(self, opts):
        cartesian = self.cameraPositionVector(opts)
        
        if any([pos < self._bounds_cartesian[idx][0] or pos > self._bounds_cartesian[idx][1] for idx, pos in enumerate(cartesian)]):
            return False
        else:
            return True
        
    def cameraPositionNumpy(self):
        p = self.cameraPosition()
        return np.array((p.x(), p.y(), p.z()))
    
    def processIntenseInteraction(self, *args, **kwargs): ...