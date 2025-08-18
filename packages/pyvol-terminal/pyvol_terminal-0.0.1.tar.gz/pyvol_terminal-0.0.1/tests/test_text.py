from __future__ import annotations
from typing import List, Optional, Tuple, Union, Dict, TYPE_CHECKING
    
import pyqtgraph as pg
from pyqtgraph import opengl 
import numpy as np
from typing import List, Optional
from PySide6 import QtCore, QtGui
from pyqtgraph import functions as fn
from pyqtgraph.opengl.GLGraphicsItem import GLGraphicsItem
from pyqtgraph import opengl
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6 import QtWidgets
from typing import List, Optional, Tuple, Union, Dict, TYPE_CHECKING
import sys
from PySide6 import QtGui, QtCore
import pyqtgraph.opengl as gl
import numpy as np
from pyqtgraph.opengl import GLTextItem
from OpenGL import GL as opengl
from OpenGL import GLU
from PySide6 import QtGui
from pprint import pprint
import copy
import math
from pyvol_terminal.interfaces.volatility_surface import view_box

np.set_printoptions(suppress=True)


def project_point(azimuth_deg, elevation_deg, distance, point):
    azimuth = np.radians(azimuth_deg)
    elevation = np.radians(elevation_deg)
    
    forward = np.array([
        np.cos(elevation) * np.cos(azimuth),
        np.cos(elevation) * np.sin(azimuth),
        np.sin(elevation)
    ])
    
    up = np.array([0, 0, 1])
    right = np.cross(forward, up)
    if np.linalg.norm(right) < 1e-10:
        right = np.array([1.0, 0.0, 0.0])
    else:
        right /= np.linalg.norm(right)
    
    up = np.cross(right, forward)
    up /= np.linalg.norm(up)
    
    eye = np.array([0, 1, 0]) - distance * forward
    vec = point - eye
    
    x = np.dot(vec, right)
    y = np.dot(vec, up)
    z = np.dot(vec, forward)
    
    if abs(z) < 1e-10:
        z = 1e-10 if z >= 0 else -1e-10
    
    u = x / z
    v = y / z
    return u, v

def get_world_width(ref_azimuth, ref_elevation, ref_distance, ref_segment_pixel_ref_view,
                    new_azimuth, new_elevation, new_distance, new_pixel_width):
    A = np.array([0, 0, 0])
    B = np.array([1, 0, 0])
    
    uA_ref, vA_ref = project_point(ref_azimuth, ref_elevation, ref_distance, A)
    uB_ref, vB_ref = project_point(ref_azimuth, ref_elevation, ref_distance, B)
    D_ref = np.sqrt((uB_ref - uA_ref)**2 + (vB_ref - vA_ref)**2)
    
    uA_new, vA_new = project_point(new_azimuth, new_elevation, new_distance, A)
    uB_new, vB_new = project_point(new_azimuth, new_elevation, new_distance, B)
    D_new = np.sqrt((uB_new - uA_new)**2 + (vB_new - vA_new)**2)
    
    world_width = (new_pixel_width * D_ref) / (ref_segment_pixel_ref_view * D_new)
    return world_width



class WorldSizedText(GLTextItem):
    origin = np.array([0, 1, 0])
    width_in_world_coord_param = 0.1
    world_width_character = 0.014286
    
    
    def __init__(self, anchor_right, *args, **kwargs):
        if anchor_right:
            self.axis_offset=kwargs["pos"][1]
        self.anchor_right=anchor_right
        self._right_anchor_pos=copy.deepcopy(kwargs["pos"])
      #  print(f"\n{kwargs["text"]}")
  #      print(kwargs["font"].pointSize())
        super().__init__(*args, **kwargs)
        


    def setParent(self, parent: View):
        
        super().setParent(parent)
        return 
        print("")
        print("-----------")
        print(f"{self.text}")
        print(f"self.width_character: {self.world_width_character}")
        print(f"len(self.text): {len(self.text)}")
        print(f"pxWidth()_prev: {self.pxWidth()}")
        print(f"worldWidth()_prev: {self.worldWidth()}")

  #      self.maintain_text_world_width()
        print(f"self._right_anchor_pos: {self._right_anchor_pos}")
        print(f"self.font.pointSizeF: {self.font.pointSizeF()}")
        print(f"pxWidth: {self.pxWidth()}")
        
        
        self.update()
        
        if self.anchor_right:
            self.shiftToWidget(parent)


    def shiftToWidget(self, widget):
        return 
        text_width_world = self.worldWidth()
        camera_pos = widget.cameraPositionNumpy()
        current_angle = math.degrees(math.atan2(*(-1*camera_pos[:2])))
        
        #current_angle = widget.opts["azimuth"]
      
        print("")
        
        
        el_x = math.degrees(math.atan2(camera_pos[0], camera_pos[2]))
        el_y = math.degrees(math.atan2(*camera_pos[1:]))
        x, y = self.offset_xy(text_width_world, current_angle, 0)
        pos = self._right_anchor_pos.copy()
        pos[0] = pos[0] + x
        pos[1] = pos[1] + y
        print(f"\nself._right_anchor_pos: {self._right_anchor_pos}")
        print(f"camera: {camera_pos}")
        print(f"azi: {widget.opts["azimuth"]}")
        
        print(f"current_angle: {current_angle}")
        print(f"el_x: {el_x}")
        print(f"el_y: {el_y}")
        print(f"x: {x}")
        print(f"y: {y}")
        print(f"pos: {pos}")

        self.setData(pos = pos)

    @QtCore.Slot()
    def updatePixelSize(self, view_widget: View):
        self.maintain_text_world_width()
        
        print(f"\n{self.text}")
        print(self.font.pointSizeF())
        print(len(self.text))


    @QtCore.Slot()
    def updatePixelSize2(self, view_widget: View):
        target_width = len(self.text) * self.world_width_character
        print("")
        print("-----------")
        print(f"{self.text}")
        metrics = QtGui.QFontMetricsF(self.font)
        rect = metrics.boundingRect(self.text).getRect()
        coords = metrics.boundingRect(self.text).getCoords()
        print(f"rect: {rect}")
        print(f"coords: {coords}")
        print(f"self.font.pointSizeF(): {self.font.pointSizeF()}")
        self.maintain_text_world_width()
        #self.font.setPixelSize(pixelSize)
        #self.setData(font=self.font)
        print(f"update:")
        #self.maintain_text_world_width()
        
        print(f"pxWidth(): {self.pxWidth()}")
        print(f"self.font.pointSizeF(): {self.font.pointSizeF()}")
        print(f"pointWidth(): {self.pointWidth()}")
        print(f"self.worldWidth(): {self.worldWidth()}")
        print(f"self.pxHeight(): {self.pxHeight()}")
        print(f"self.worldWidth(): {self.pxHeight()}")
        
        rect = metrics.boundingRect(self.text).getRect()
        coords = metrics.boundingRect(self.text).getCoords()

        print(f"rect: {rect}")
        print(f"coords: {coords}")
        
        

        if self.anchor_right:
            self.shiftToWidget(view_widget)
    
    def update_size(self, view_widget: View):
        target_width = len(self.text) * self.world_width_character
        
        # Get current metrics and actual text width
        metrics = QtGui.QFontMetricsF(self.font)
        current_px_width = metrics.boundingRect(self.text).width()
        pixel_size_world = view_widget.pixelSize(self._right_anchor_pos)
        current_world_width = current_px_width * pixel_size_world
        
        if current_world_width <= 0:
            return
        
        # Calculate required scaling factor
        scale_factor = target_width / current_world_width
        
        # Scale the font size while maintaining units
        if self.font.pixelSize() > 0:
            # Pixel-based font: scale directly
            new_px = max(1, int(self.font.pixelSize() * scale_factor))
            self.font.setPixelSize(new_px)
        else:
            # Point-based font: scale points
            new_pt = self.font.pointSizeF() * scale_factor
            if new_pt < 0.1:
                new_pt = 0.1
            self.font.setPointSizeF(new_pt)
        
        self.setData(font=self.font)

    def maintain_text_world_width(self):
        current_world_width = self.worldWidth()
        if current_world_width <= 0:
            return
        
        scale_factor = len(self.text) * self.world_width_character / current_world_width
        
        
        
        current_font = self.font
        current_point_size = current_font.pointSizeF()
        new_size = current_point_size * scale_factor

        current_font.setPointSizeF(new_size)
        self.setData(font=current_font)

            
    def maintain_text_world_width2(self):
        current_world_width = self.worldWidth()
        if current_world_width <= 0:
            return
        
        print(f"current_world_width: {current_world_width}")
        scale_factor = len(self.text) * self.world_width_character / current_world_width
        
        dx = current_world_width * (1- scale_factor)
        dy = current_world_width * (1- scale_factor)
        dz = current_world_width * (1- scale_factor)
      #  self.scale(dx,0,0 )
       
        
        print(f"scale_factor: {scale_factor}")
        
        current_font = self.font
        current_point_size = current_font.pointSizeF()
      #  print(f"current_world_width: {current_world_width}")
     #   print(f"current_point_size: {current_point_size}")
        new_size = current_point_size * scale_factor
    #    print(f"new_size: {new_size}")
        if new_size < 0.1: 
            new_size = 0.1
        current_font.setPointSizeF(new_size)
        self.setData(font=current_font)


    def offset_xy(self, txt_width, theta, elevation):
        x = -txt_width * math.cos(math.radians(theta))
        print(f"x_ang: {math.cos(math.radians(theta))}")
        y = txt_width * math.sin(math.radians(theta))
        print(f"y_ang: {math.sin(math.radians(theta))}")
        return x, y
    
    @classmethod
    def euclidean_distance(cls, point1, point2):
        return math.sqrt((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2 + (point2[2] - point1[2]) ** 2)
    """
    def pxHeight(self):
        metrics = QtGui.QFontMetricsF(self.font)
        return metrics.boundingRect(self.text).height()
    
    def pxWidth(self):
        metrics = QtGui.QFontMetricsF(self.font)
        return metrics.boundingRect(self.text).width()
    
    def pointWidth(self):
        return self.pxWidth() * 72 / self.view().screen().logicalDotsPerInch()

    def worldWidth(self):
        return self.pxWidth() * self.view().pixelSize(self._right_anchor_pos)

    def worldWidthPoint(self):
        return self.pointWidth() * self.view().pointSize(self._right_anchor_pos)

    """

    def pxHeight(self):
        metrics = QtGui.QFontMetricsF(self.font)
        return metrics.boundingRect(self.text).height()
    
    def pxWidth(self):
        metrics = QtGui.QFontMetricsF(self.font)
        return metrics.boundingRect(self.text).width()
    
    def pointWidth(self):
        return self.pxWidth() * 72 / self.view().screen().logicalDotsPerInch()

    def worldWidth(self):
        return self.pxWidth() * self.view().pixelSize(np.array(self.pos))

    def worldWidthPoint(self):
        return self.pointWidth() * self.view().pointSize(np.array(self.pos))



class AxisItem3D:
    def __init__(self, axis_direction, label, colour, axis_pos_vector, axis_origin, tick_direction, tick_size_major, axRange=None, offset_label=0.05, offset_tick_num=None, font=None, parent=None):
        self.axis_direction=axis_direction
        self.label=label
        self.colour=colour
        self._nTicks = axis_pos_vector.size
        self.offset_label=offset_label
        self.font=font if not font is None else QtGui.QFont('Neue Haas Grotesk',  pointSize=12)
        #self.font.setPixelSize(12)
 #      self.font.setPointSizeF(12)
        self.parent=parent
        self.axis_vector = np.zeros(3)
        self.axis_vector[axis_direction]=1
        self.axis_origin=axis_origin
        tick_axis_gap = tick_size_major / 3
        self._tickBufferLinePos = None
        self.tickBufferLine = self._initTickBufferLine(axis_pos_vector, self.axis_vector, self.axis_origin, tick_direction, tick_axis_gap)
        self._tickItemMajor = self._initTickMajorItems(axis_pos_vector, self.axis_vector, self._tickBufferLinePos[0], tick_direction, tick_size_major)
        
        dMajor = axis_pos_vector[1] - axis_pos_vector[0]
        self._tickItemMinor = self._initTickMinorItems(self._tickItemPosMajor, dMajor)
        self.tick_size_major=tick_size_major
        if not axRange is None:
            self.tick_strings=[f"{int(round((i / (1+ 0*self.axis_direction)), 1))}" for i in np.linspace(np.amin(axRange), np.amax(axRange), self._nTicks)]
        #    if axis_direction == 0:
        #        for idx, s in enumerate(self.tick_strings):
          #          s = s + "...."
          #          self.tick_strings[idx] = s
                
        else:
            self.tick_strings=[f"{i}" for i in np.arange(self._nTicks)] #* self._nTicks
        self.tick_values=np.full(self._nTicks, np.nan)
        
        self.tickNumPositions = None
        self.tickNums = self._initTickNums()
        
        self.label = self._initLabelItem(label, axis_pos_vector, self.axis_vector, self.axis_origin, tick_direction, self.offset_label)
        self._ticks_visible=False

    def reset_numItem_pxWidth222(self):
        pointPxDratio=[]
        for textNum in self.tickNums:
            pointPxDratio.append(textNum._pointPxDistanceRatio_default)
        maxPointPxDratio = np.amax(pointPxDratio)
        for textNum in self.tickNums:
            textNum._pointPxDistanceRatio_default=maxPointPxDratio
            
    
    def _initTickBufferLine(self, tick_values, axis_vector, axis_origin, tick_direction, tick_axis_gap):
        tick_values = np.asarray(tick_values)
        axis_vector = np.asarray(axis_vector)
        axis_origin = np.asarray(axis_origin)
        tick_direction = np.asarray(tick_direction)

        t_min = tick_values.min()
        t_max = tick_values.max()

        start = axis_origin + t_min * axis_vector + tick_direction * tick_axis_gap
        end = axis_origin + t_max * axis_vector + tick_direction * tick_axis_gap
        self._tickBufferLinePos=np.vstack((start, end))
        return gl.GLLinePlotItem(pos=self._tickBufferLinePos, color="white", width=2.5)

    def _initTickMajorItems(self, tick_values, axis_vector, shifted_axis_origin, tick_direction, tick_size):
        tick_values = np.asarray(tick_values)
        axis_vector = np.asarray(axis_vector)
        tick_direction = np.asarray(tick_direction)
        shifted_axis_origin = np.asarray(shifted_axis_origin)
        starts = shifted_axis_origin + np.outer(tick_values, axis_vector)
        ends = starts + tick_size * tick_direction
        self._tickItemPosMajor = [np.vstack((start, end)) for start, end in zip(starts, ends)]
        return [gl.GLLinePlotItem(pos=coord, color="white", width=2.5) for coord in self._tickItemPosMajor]

        
    def _initTickMinorItems(self, coordinates_major, dMajor):
        
        self._tickItemPosMinor = copy.deepcopy(coordinates_major[1:])
        tick_items =[]
        
        for coordinate in self._tickItemPosMinor:
            dSizeMajor = coordinate[1] - coordinate[0]
            coordinate[1] = coordinate[0] + dSizeMajor / 2
            coordinate[:, self.axis_direction] -= dMajor / 2

            tick = gl.GLLinePlotItem(pos=coordinate, color="white", width=1.5)
            tick_items.append(tick)
        return tick_items


    def setParent(self, parent):
        self.parent=parent
        for idx, tickNum in enumerate(self.tickNums):
            if hasattr(tickNum, "updatePixelSize"):
                self.parent.viewChangedSignal.connect(tickNum.updatePixelSize)
            self.parent.addItem(tickNum, viewBoxAdd=False)
            tickNum.setParent(self.parent)       
        
        for tick in self._tickItemMajor + self._tickItemMinor:
            tick.setParent(self.parent)
            parent.addItem(tick, viewBoxAdd=False)
  #      self.parent.addItem(self.label, viewBoxAdd=False)
   #     self.label.setParent(self.parent)
   #     if hasattr(self.label, "updatePixelSize"):
    #        self.parent.viewChangedSignal.connect(self.label.updatePixelSize)
        self._ticks_visible=True
        self.parent.addItem(self.tickBufferLine)

        
    #    self.reset_numItem_pxWidth()
        
    
    def _initTickNums(self) -> List[WorldSizedText]:
        gl_objects = []
        if self.axis_direction == 0:
            anchor_right=True
        else:
            anchor_right=False
        idx=0
        print(f"len(self.tick_strings)-1: {len(self.tick_strings)-1}")
        for pos_vec, tick_str in zip(self._tickItemPosMajor, self.tick_strings):
            print(idx)
            if not idx in [0, len(self.tick_strings)-1]:
                idx+=1
                continue 
            idx+=1
            pos = pos_vec[1,:]

            gl_object = WorldSizedText(anchor_right, pos=pos, text=tick_str, font=self.font, color=self.colour)
        #   gl_object = GLTextItem(pos=pos, text=tick_str, font=self.font, color=self.colour)
            gl_objects.append(gl_object)
            
        return gl_objects

    def create_tick_strings(self):
        return [str(val) for val in self.tick_values]
    
    def create_tick_values(self, min_val, max_val, n_ticks):
        return np.linspace(min_val, max_val, n_ticks)

    def setLabel(self, label):
        self._label=label
        self.label.setData(text=label)
    
    def getLabel(self):
        return self._label
      
    @QtCore.Slot()
    def update_values(self, plot_view):
        self.min, self.max = plot_view.min, plot_view.max
        self.tick_values = self.create_tick_values(self.min, self.max, self._nTicks)
        self.tick_strings = self.create_tick_strings()
        for tick_str, pos_vec, tick_object in zip(self.tick_strings, self._tickItemPosMajor, self.tickNums):
            pos = pos_vec[1,:]
            if not self._ticks_visible:
                tick_object.show()
            try:
                tick_object.setData(text=tick_str, pos=pos)      
            except:
                pass
        if not self._ticks_visible:
            self._ticks_visible=True

    def _initLabelItem(self, label, tick_values, axis_vector, axis_origin, tick_direction, label_offset):
        tick_values = np.asarray(tick_values)
        axis_vector = np.asarray(axis_vector)
        axis_origin = np.asarray(axis_origin)
        tick_direction = np.asarray(tick_direction)

        t_min = tick_values.min()
        t_max = tick_values.max()
        t_mid = 0.5 * (t_min + t_max)

        midpoint = axis_origin + t_mid * axis_vector
        offset = label_offset * tick_direction
        if self.axis_direction == 0:
            anchor_right=True
        else:
            anchor_right=False
        return GLTextItem(pos=midpoint + offset, text=label, font=self.font, color=self.colour)#WorldSizedText(anchor_right, pos=midpoint + offset, text=label, font=self.font, color=self.colour)


class CustomGrid(gl.GLGridItem):
    def __init__(self, n_lines, *args, **kwargs):
        self.n_lines=int(2*n_lines -1)
        super().__init__(*args, **kwargs)

    def updateLines(self):
        if self.lineplot is None:
            return
        x, y, _ = self.size()
        xvals = np.linspace(-x/2., x/2., self.n_lines)
        yvals = np.linspace(-y/2., y/2., self.n_lines)
        
        set1 = np.zeros((len(xvals), 6), dtype=np.float32)
        set1[:, 0] = xvals
        set1[:, 1] = yvals[0]
        set1[:, 3] = xvals
        set1[:, 4] = yvals[-1]

        set2 = np.zeros((len(yvals), 6), dtype=np.float32)
        set2[:, 0] = xvals[0]
        set2[:, 1] = yvals
        set2[:, 3] = xvals[-1]
        set2[:, 4] = yvals

        pos = np.vstack((set1, set2)).reshape((-1, 3))
        self.lineplot.setData(pos=pos, color=self.color())
        self.update()


class CustomAxisItem(pg.AxisItem):
    def __init__(self, axis_direction=None, tick_engine=None, *args, **kwargs):
        self.axis_direction=axis_direction
        self.title=None
        self.tick_engine=tick_engine
        self.global_count=0
        super().__init__(*args, **kwargs)
        self.enableAutoSIPrefix(False)

    def tickStrings(self, values, scale, spacing):
        return self.tick_engine.function(values)      
    
class AxisManager(QtCore.QObject):
    def __init__(self,
                 view_widget,
                 n_major_ticks=[5] * 3
                 ):
        super().__init__()
        self.view_widget=view_widget
        self.str_int_map = {"x" : 0,
                            "y" : 1,
                            "z" : 2}
        self.int_str_map = {value : key for key, value in self.str_int_map.items()}
        self.n_ticks_dict={0 : n_major_ticks[0],
                           1 : n_major_ticks[1],
                           2 : n_major_ticks[2]}
        self.axis_2D_items: dict[str, List[CustomAxisItem]] = {0 : [],
                                                               1 : [],
                                                               2 : []}              
        self.axis_3D_items: dict[str, None] = {0 : None,
                                                     1 : None,
                                                     2 : None}
        self.colours = {0 : "white",
                        1 : "white",
                        2 : "white",
                        }
        self.axis_x = None  
        self.axis_y = None
        self.axis_z = None
        self.labels=["Strike", "Expiry", "Implied Volatility"]        
        self.offset_ticks = {0 : np.array([-0.2, 0, 0]),
                             1 : np.array([0, 0.2, 0]),
                             2 : np.array([0.2, 0.2, 0]),
                             }
        
        
        self._base_label_positions = {0 : np.array([0.5, 0, 0]),
                                      1 : np.array([1, 0.5, 0]),
                                      2 : np.array([1, 1, 0.5])}
        self.base_ticknum_positions = {}
        self.offset_tick_num = {jdx : np.zeros(3) for jdx in range(3)}
        self.tick_size_major=1/15
        axis_pos = np.linspace(0, 1, self.n_ticks_dict[0])
        self.tick_size_structure={0 : np.array([0, -1, 0]),
                                  1 : np.array([1, 0, 0]),
                                  2 : np.array([1, 1, 0]),
                                  }        
        self.axis_pos_vector = {jdx : np.linspace(0, 1, self.n_ticks_dict[jdx]) for jdx in range(3)}

        self.axis_origin_container = {0 : (0, 0, 0),
                                      1 : (1, 0, 0),
                                      2 : (1, 1, 0)
                                      }
        self.tick_direction_container = {0 : (0, -1, 0),
                                         1 : (1, 0, 0),
                                         2 : (1, 0, 0)}
        
        self.base_axis_coordinates={0 : [np.array([idx, 0, 0]) for idx in axis_pos],
                                    1 : [np.array([1, idx, 0]) for idx in axis_pos],
                                    2 : [np.array([1, 1, idx]) for idx in axis_pos],
                                    }        
        
        self.offset_labels = {0 : 0.2,
                              1 : 0.2,
                              2 : 0.2,
                              }
        self._init_axis_3D_items(view_widget)
        self.initialised_default=True

    def _init_axis_3D_items(self, view_widget):
        Range = np.array([view_widget.min, view_widget.max])
        for axis_direction, label in zip([0, 1, 2], self.labels):
       #     if axis_direction != 0: 
               # continue
            print(f"axis: {axis_direction}")
            view_range = Range * (1 + axis_direction*0.1)
            if axis_direction > 1:
                break
            axis_str = self.int_str_map[axis_direction]
            axis_item = AxisItem3D(axis_direction, 
                                    label,
                                    self.colours[axis_direction],
                                    self.axis_pos_vector[axis_direction],
                                    self.axis_origin_container[axis_direction],
                                    self.tick_direction_container[axis_direction],
                                    self.tick_size_major,
                                    view_range,
                                    self.offset_labels[axis_direction],
                                    self.offset_tick_num[axis_direction])
            
            if not view_widget is None:
                view_widget.addItem(axis_item)
                axis_item.setParent(view_widget)
                view_widget.axisChangedSignal.connect(axis_item.update_values)
                
            self.axis_3D_items[axis_direction] = axis_item
        view_widget.update()

    def get_label(self,
                  axis_direction: str
                  ) -> str:
        return self.axis_3D_items[axis_direction].label.getLabel()

    def switch_axis(self, axis_direction, axis_label):
        if isinstance(axis_direction, str):
            axis_direction=self.str_int_map[axis_direction]
        self.axis_3D_items[axis_direction].setLabel(axis_label)  
        for axis_item in self.axis_2D_items[axis_direction]:
            axis_item.setLabel(axis_label)
            
    def add_2D_axis_item(self, axis_item, axis_direction):
        self.axis_2D_items[axis_direction].append(axis_item)
        
    def addWidget(self, widget):
        self.view_widget=widget
        if not self.initialised_default:
            self._init_axis_3D_items()
        for axis_item in self.axis_3D_items.values():
            widget.axisChangedSignal.connect(axis_item.update_values)
    

class GridManager:
    def __init__(self,
                 widget: opengl.GLViewWidget,
                 n_major_ticks: int
                 ) -> GridManager:
        self.widget=widget
        self.size=[1] * 3
        self.n_major_ticks=n_major_ticks
        self.n_minor_ticks=[2 * t  for t in n_major_ticks]
        print(f"self.n_minor_ticks: {self.n_minor_ticks}")
        self.spacing= [size / minor_tick for size, minor_tick in zip(self.size, self.n_minor_ticks)]
        self._major_minor_scale = 0.5
        
        self.grid_xy = self._create_grid(self.size, self.spacing, translation=(0.5, 0.5, 0))
        
        offset_yz = -0.3 
        offset_xz = 0.3
        
        self.grid_yz = self._create_grid(self.size, self.spacing, rotation=(90, 0, 1, 0), translation=(0 + offset_yz, 0.5, 0.5))
        self.grid_xz = self._create_grid(self.size, self.spacing, rotation=(90, 1, 0, 0), translation=(0.5, 1 + offset_xz, 0.5))
        if not widget is None:
            self._addGrids(widget)
    
    def addWidget(self,
                  widget: opengl.GLViewWidget
                  ) -> None:
        self.widget=widget
        self._addGrids(self.widget)
    
    def _addGrids(self,
                  widget: opengl.GLViewWidget
                  ) -> None:
        widget.addItem(self.grid_xy)
        widget.addItem(self.grid_yz)
        widget.addItem(self.grid_xz)

        self.widget=widget
        
    def _create_grid(self, size, spacing, rotation=None, translation=None):      
        print(f" self.n_major_ticks[0]: {self.n_major_ticks[0]}")  
        grid = CustomGrid(n_lines=self.n_major_ticks[0])
        grid.setSize(*size)
        grid.setSpacing(*spacing)
        if rotation:
            grid.rotate(*rotation)        
        if translation:
            grid.translate(*translation)
        return grid

class View(gl.GLViewWidget):
    rc_pos_unnorm_signal = QtCore.Signal(float, float, float)
    mouse_position_signal = QtCore.Signal(float, float, float)
    viewChangedSignal = QtCore.Signal(object)
    axisChangedSignal = QtCore.Signal(object)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.vb=view_box.ViewBox()

        self.setMouseTracking(True)
        self.setAttribute(QtCore.Qt.WA_Hover)
        self.setAttribute(QtCore.Qt.WA_DontCreateNativeAncestors) 
        self.show_spot_text=True
        near_clip, far_clip = self.compute_optimal_clipping()
        self._mouseZoomFactor=0.999
        distance = 4
        azimuth = -0#-45 #+ math.degrees(math.asin(1/3))#-90
        elevation = 15#math.degrees(math.acos(math.sqrt(2)/4))#0#30
        self._bounds_cartesian = [[0, 1], [0, 1], [0, 1]]
        self.cross_hairs_enabled=True

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
        self._cartesian_view_coords = np.array([0., 0., 0.])
        self._cartesian_view_coords = self.cameraPostionVector()
        self.interacting=False
        self.min = 100000.
        self.max = 120000.#95000#125000.
        self.setMouseTracking(True)
        self.update()    

    def pointSize(self, pos):
        PIXELS_PER_POINT = self.screen().logicalDotsPerInch() / 72.0
        
        # Get the pixel size at the given position
        pixel_size = self.pixelSize(pos)
        
        # Calculate the point size
        point_size = pixel_size * PIXELS_PER_POINT
        
        return point_size

    def compute_optimal_clipping(self):
        largest_point_distance = np.sqrt(3)
        near_clip = max(0.0001, self.opts['distance'] - 1.01 * largest_point_distance) 
        far_clip = self.opts['distance'] 
        return near_clip, far_clip

    def setAxisItems(self, axisItems) -> None:
        for axis_item in axisItems.values():
            axis_item.setParent(self)
            self.addItem(axis_item)
            
    def mousePressEvent(self, event):
        match event.buttons().value :    
            case 1: 
                self.interacting=True
                
            case 2:
                self.mouse_pos = event.pos()  
                self.opts["azimuth"] = -14.477512185929925
                
        #        self.viewChangedSignal.emit(self)
                #self.process_right_click(self.mouse_pos)
        super().mousePressEvent(event)

    def process_right_click(self, mouse_pos):
        return 
        world_x, world_y, world_z = self.get_mouse_pos(mouse_pos)
        if 0 <= world_x <= 1 and 0 <= world_y <= 1 and 0 <= world_z <= 1:        
            self.prev_x, self.prev_y, self.prev_z = self.vb.plot_views["x"].unnormalise(world_x),\
                                                    self.vb.plot_views["y"].unnormalise(world_y),\
                                                    self.vb.plot_views["z"].unnormalise(world_z)
            self.rc_pos_unnorm_signal.emit(self.prev_x, self.prev_y, self.prev_z)

    def cameraPositionNumpy(self):
        p = self.cameraPosition()
        return np.array((p.x(), p.y(), p.z()))

    def mouseMoveEvent(self, ev):
        self.mouse_pos = ev.pos()
        if ev.buttons() == QtCore.Qt.MouseButton.LeftButton:
            self.interacting=True

        lpos = ev.position() if hasattr(ev, 'position') else ev.localPos()
        if not hasattr(self, 'mousePos'):
            self.mousePos = lpos
        diff = lpos - self.mousePos
        self.mousePos = lpos
        
        if ev.buttons() == QtCore.Qt.MouseButton.LeftButton:
            self.orbit(-diff.x(), diff.y())
        elif ev.buttons() == QtCore.Qt.MouseButton.MiddleButton:
            if (ev.modifiers() & QtCore.Qt.KeyboardModifier.ControlModifier):
                self.pan(diff.x(), 0, diff.y(), relative='view-upright')
            else:
                self.pan(diff.x(), diff.y(), 0, relative='view-upright')
    def addItem(self, item, *args, **kwargs):
        vbargs = {}
        added=False
        if 'ignoreBounds' in kwargs:
            vbargs['ignoreBounds'] = kwargs['ignoreBounds']
        
        if "viewBoxAdd" in kwargs:
            if kwargs["viewBoxAdd"]:
                self.vb.addItem(item, *args, **vbargs)
                self._internal_id_item_map[item.get_internal_id()] = item
            else:
                added=True
                del kwargs["viewBoxAdd"]
                super().addItem(item, *args, **kwargs)
        if not isinstance(item, AxisItem3D) and "viewBoxAdd" in kwargs:
            del kwargs["viewBoxAdd"]
            if not added:
                added=True
                super().addItem(item, *args, **kwargs)
        else:
            if not added and not isinstance(item, AxisItem3D):
                added=True
                super().addItem(item, *args, **kwargs)
        return item


    def orbit(self, azim, elev):    
        """
        if self.opts['azimuth'] + azim < -90 or 0 < self.opts['azimuth'] + azim:
            return 
        if fn.clip_scalar(self.opts['elevation'] + elev, -90., 90.)  < 0:
            return
        """
        super().orbit(azim, elev)
        print(f"\n\nnew_orb\n")
        self.viewChangedSignal.emit(self)
        return
        elevation = fn.clip_scalar(self.opts['elevation'] + elev, -90., 90.) 
        new_opts = {"elevation" : elevation,
                    "azimuth" : self.opts['azimuth'] + azim,
                    "distance" : self.opts["distance"]} 
        
        if not self._validAngle(self.opts['azimuth'] + azim, elevation):
            return
        
        else:
            if self._outsideBox(new_opts):
                cartesian_coords = self.cameraPostionVector(new_opts)
                self.opts.update(new_opts)
                self.update()
                self.viewChangedSignal.emit(self)
            else:
                dE = elevation - self.opts["elevation"]
                cartesian_coords = self.cameraPostionVector(self.opts)
                prev_axis_outside_cube = [self._bounds_cartesian[idx][1] < pos for idx, pos in enumerate(cartesian_coords)]
                azim/=2 
                azimuth = self.opts['azimuth'] + azim
                elevation = self.opts["elevation"] + dE/2
                
                if sum(prev_axis_outside_cube) > 0:
                    for axis, flag in zip("xyz", prev_axis_outside_cube):
                        if flag:
                            if axis == "x":
                                r_new = 1.00001 * self._bounds_cartesian[0][1] / (math.sin(math.radians(self._elevation_offset - elevation))
                                                                       *math.cos(math.radians(azimuth + self._azimuth_offset)))
                                
                            elif axis == "y":
                                r_new = 1.00001 * self._bounds_cartesian[1][1] / (math.sin(math.radians(self._elevation_offset - elevation))
                                                                    *math.sin(math.radians(azimuth + self._azimuth_offset)))
                                
                            else:
                                r_new = 1.00001 * self._bounds_cartesian[2][1] / math.cos(math.radians(self._elevation_offset - elevation))
                    
                    new_opts = {"elevation" : elevation,
                                "azimuth" : azimuth,
                                "distance" : r_new} 
                    self.opts.update(new_opts)

                    self.update()
                    self.viewChangedSignal.emit(self)


    def pan2(self, dx, dy, dz, relative='global'):
        if relative == 'view':
            elev = math.radians(self.opts['elevation'])
            azim = math.radians(self.opts['azimuth'])
            fov = math.radians(self.opts['fov'])
            dist = (self.opts['center'] - self.cameraPosition()).length()
            fov_factor = math.tan(fov / 2) * 2
            scale_factor = dist * fov_factor / self.width()
            z = scale_factor * math.cos(elev) * dy
            x = scale_factor * (math.sin(azim) * dx - math.sin(elev) * math.cos(azim) * dy)
            y = scale_factor * (math.cos(azim) * dx + math.sin(elev) * math.sin(azim) * dy)

            if self._validViewCartesian((x, -y, z)):
                self.opts['center'] += QtGui.QVector3D(x, -y, z)
                self.opts.update({"elevation" : elev,
                                  "azimuth" : azim,
                                  "distance" : dist})
                self.update()
        else:
            raise ValueError("relative argument must be global, view, or view-upright")

    def zoom(self, rMultiplier):
        distance = self.opts['distance'] * rMultiplier
        opts = {"distance" : distance,
                "elevation" : self.opts["elevation"],
                "azimuth" : self.opts["azimuth"]}
        
        if self._outsideBox(opts):
            self.opts["distance"] = distance
            self.update()
            self.viewChangedSignal.emit(self)
            return True
        else:
            return False
            
    
    def wheelEvent(self, ev):
        delta = ev.angleDelta().x()
        if delta == 0:
            delta = ev.angleDelta().y()
        for i in [1, 1/4]:
            zoomChanged=self.zoom(self._mouseZoomFactor**(i*delta))
            if zoomChanged:
                return 
        
    def cameraPostionVector(self,
                            opts=None) -> np.ndarray[float]:
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
        if any([self._bounds_cartesian[idx][1] <= pos for idx, pos in enumerate(self.cameraPostionVector(opts))]):
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
        cartesian = self.cameraPostionVector(opts)
        
        if any([pos < self._bounds_cartesian[idx][0] or pos > self._bounds_cartesian[idx][1] for idx, pos in enumerate(cartesian)]):
            return False
        else:
            return True
        
    
    @classmethod
    def distanceSphericalCoordinates(cls, r, r_p):
        t1 = r["distance"] **2 + r_p["distance"] ** 2
        
        t21 = (math.sin(math.radians(90 - r["elevation"]))
                *math.sin(math.radians(90 - r_p["elevation"]))
                *math.cos(math.radians(r["azimuth"] - r_p["azimuth"])))
        t22 = (math.cos(math.radians(90 - r["elevation"]))
              *math.cos(math.radians(90 - r_p["elevation"])))
        
        return math.sqrt(t1 - 2 * r["distance"] * r_p["distance"] * (t21 + t22))




class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle('Volatility Surface')
        self.widget_central = QtWidgets.QWidget()
        self.setCentralWidget(self.widget_central)
        self.layout_main = QtWidgets.QVBoxLayout()
        self.widget_central.setLayout(self.layout_main)
        self.showMaximized()

        self.view_widget = View()
        self.vw_layout = QtWidgets.QVBoxLayout()
        self.layout_main.addLayout(self.vw_layout)
        
        n_major_ticks = [5]* 3
        
        self.layout_main.addWidget(self.view_widget)
        
        self.grid_manager = GridManager(self.view_widget,
                                        n_major_ticks
                                        )
        
        # Show window then initialize axes with delay
        self.showMaximized()
        QtCore.QTimer.singleShot(100, self.init_axes_after_show)
        
    def init_axes_after_show(self):
        """Initialize axis system after window is shown and sized"""
        n_major_ticks = [5] * 3
        self.axis_manager = AxisManager(self.view_widget, n_major_ticks)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    sys.exit(app.exec())
    
