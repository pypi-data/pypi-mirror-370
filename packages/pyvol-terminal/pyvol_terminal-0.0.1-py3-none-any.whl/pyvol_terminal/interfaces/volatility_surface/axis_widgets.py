from __future__ import annotations
from typing import List, Optional, Tuple, Union, Dict, TYPE_CHECKING

from pyvol_terminal.gl_3D_graphing.graphics_items.GL3DAxisItem import GL3DAxisItem
if TYPE_CHECKING:
    from ...quantities.engines import TickEngine, TickEngineManager, MetricAxisEngine
    from ...gl_3D_graphing.graphics_items.GL3DAxisItem import GL3DAxisItem
    from pyvol_terminal.interfaces.volatility_surface.pyvol_GL3DViewWidget import SurfaceViewWidget
    
import pyqtgraph as pg
from pyqtgraph import opengl 
import numpy as np
from ...gl_3D_graphing.graphics_items import GL3DAxisItem
from PySide6 import QtCore, QtGui
from pyqtgraph import opengl

class CustomAxisItem(pg.AxisItem):
    def __init__(self, axis_direction=None, tick_engine: TickEngine=None, *args, **kwargs):
        self.axis_direction=axis_direction
        self.title=None
        self.tick_engine=tick_engine
        super().__init__(*args, **kwargs)
        self.enableAutoSIPrefix(False)

    def tickStrings(self, values, scale, spacing):
        return self.tick_engine.function(values)  
    
class AxisManager(QtCore.QObject):
    def __init__(self,
                 view_widget,
                 tick_engine_manager: TickEngineManager=None,
                 normaliser=None,
                 n_major_ticks=[6, 6, 6],
                 z_offset=0.3,
                 ):
        super().__init__()
        self.view_widget=view_widget
        self.tick_engine_manager=tick_engine_manager
        self.normaliser=normaliser
        self.str_int_map = {"x" : 0,
                            "y" : 1,
                            "z" : [2, 3],
                            }
        
        self.n_major_ticks=n_major_ticks
        
        self.int_str_map = {v: k for k, val in self.str_int_map.items() for v in (val if isinstance(val, list) else [val])}

        self.n_ticks_dict={0 : n_major_ticks[0],
                           1 : n_major_ticks[1],
                           2 : n_major_ticks[2],
                           3 : n_major_ticks[3]}
        self.axis_2D_items: dict[str, List[CustomAxisItem]] = {0 : [],
                                                               1 : [],
                                                               2 : [],
                                                               3 : []
                                                               }              
        self.axis_3D_items: dict[str, GL3DAxisItem] = []
        
        self.colours = {0 : "white",
                        1 : "white",
                        2 : "white",
                        3 : "white"
                        }
        self.num_dir_map = {0 : 0,
                            1 : 1,
                            2 : 2,
                            3 : 2
                            }
        self.axis_x = None  
        self.axis_y = None
        self.axis_z = None
        self.labels=["Strike", "Expiry", "Implied Volatility", "Implied Volatility"]        
        self.label_map = {0 : "Strike",
                          1 : "Expiry",
                          2 : "Implied Volatility"}
        self.offset_ticks = {0 : np.array([-0.2, 0, 0]),
                             1 : np.array([0, 0.2, 0]),
                             2 : np.array([0.2, 0.2, 0]),
                             3 : np.array([-0.2, 0, 0])
                             }
        self.base_ticknum_positions = {}
        self.tick_size_major=1/15
        
        self.axis_perp = {0 : 1, 
                          1 : 0, 
                          2 : 0,
                          3 : 1}
     
        
        self.anchor_map = {0 : True, 
                           1 : False,
                           2 : False,
                           3 : True
                           }
                
        self.axis_origin_container22 = {0 : (0, 0, 0),
                                      1 : (1, 0, 0),
                                      2 : (1, 1, 0),
                                      3 : (0, 0, 0), 
                                      }
        
        self.axis_origin_container = {0 : ("start", "start"),
                                      1 : ("end", "start"),
                                      2 : ("end", "end"),
                                      3 : ("start", "start"), 
                                      }
        self.z_offset=z_offset
        self.extra_offset = {0 : (0., 0., 0.),
                             1 : (0., 0., 0.),
                             2 : (0., z_offset, 0.),
                             3 : (-z_offset, 0., 0.)
                             }    
        self.padding={0 : 0,
                      1 : 0, 
                      2 : z_offset,
                      3 : z_offset
                      }
        self.axis_map = {
                         0 : [{"perpendicular" : 1,
                               "showTicks" : True,
                               "other_pos" : ("start", "start"),
                               },
                              {"perpendicular" : 2,
                               "showTicks" : False,
                               "other_pos" : ("end", "start"),
                               }
                              ],
                         1 : [{"perpendicular" : 0,
                               "showTicks" : True,
                               "other_pos" : ("end", "start"),
                               },
                              {"perpendicular" : 2,
                               "showTicks" : False,
                               "other_pos" : ("start", "end"),
                               }
                              ],
                         2 : [{"perpendicular" : 0,
                               "showTicks" : True,
                               "other_pos" : ("end", "end"),
                               },
                              {"perpendicular" : 1,
                               "showTicks" : True,
                               "other_pos" : ("start", "start"),
                               }
                              ]
                        }
        
        
        self.tick_direction_container = {0 : (0, -1, 0),
                                         1 : (1, 0, 0),
                                         2 : (1, 0, 0),
                                         3 : (0, -1, 0),
                                         }
        self.offset_labels = {0 : 0.1,
                              1 : 0.1,
                              2 : 0.1,
                              3 : 0.1,
                              }
        self._init_axis()
        self.initialised_default=True

    def _init_axis(self):
        
        anchor_right=False
        
        for ax_dir, ax_opt_list in self.axis_map.items():
            
            for ax_opt in ax_opt_list:
                padding = self.z_offset if ax_dir == 2 or ax_opt["other_pos"]==2 else 0
                if ax_opt["showTicks"]:
                    label = self.label_map[ax_dir]
                else:
                    label=None
                axis_item = GL3DAxisItem.CustomAxisItem3D(tick_engine=self.tick_engine_manager.get_engine(ax_dir),
                                                  direction=ax_dir, 
                                                  direction_perp=ax_opt["perpendicular"],
                                                  other_pos=ax_opt["other_pos"],
                                                  unit_size=1,
                                                  nticks=self.n_major_ticks[ax_dir],
                                                  colour=self.colours[ax_dir],
                                                  padding=padding,
                                                  label=label,
                                                  tick_size_major=self.tick_size_major,
                                                  offset_label=self.offset_labels[ax_dir],
                                                  anchor_right=anchor_right,
                                                  font=QtGui.QFont('Neue Haas Grotesk', 10),
                                                  includeGrid=True
                                                  )
                #self.axis_3D_items[axis] = axis_item
                self.axis_3D_items.append(axis_item)
                break
            break

    def _init_axis2(self):
        for axis_num, label in zip([0, 1, 2, 3], self.labels):
            axis_str = self.int_str_map[axis_num]
            axis_direction = self.num_dir_map[axis_num]
            anchor_right = self.anchor_map[axis_num]
            includeGrids=[True, False] if axis_num < 2 else [True,True]
            
            axis_item = GL3DAxisItem.CustomAxisItem3D(self.tick_engine_manager.get_engine(axis_str),
                                                axis_direction, 
                                                self.axis_perp[axis_num],
                                                other_pos=self.axis_origin_container[axis_num],
                                                unit_size=1,
                                                nticks=self.n_major_ticks[axis_num],
                                                colour=self.colours[axis_num],
                                                padding=self.padding[axis_num],
                                                label=label,

                                                tick_size_major=self.tick_size_major,
                                                
                                                offset_label=self.offset_labels[axis_num],
                                                anchor_right=anchor_right,
                                                font=QtGui.QFont('Neue Haas Grotesk', 10),
                                                includeGrids=includeGrids
                                                )
            self.axis_3D_items[axis_num] = axis_item

    def get_label(self,
                  axis_direction: str
                  ) -> str:
        return self.axis_3D_items[axis_direction].labelItem.getLabel()

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
            self._init_axis()
    
class GridManager:
    def __init__(self,
                 widget: SurfaceViewWidget,
                 n_major_ticks: int,
                 z_offset: float,
                 ) -> GridManager:
        self.widget=widget
        self.size=[1] * 3
        self.n_major_ticks=n_major_ticks
        self.n_minor_ticks=[2 * t  for t in n_major_ticks]
        self.spacing= [size / minor_tick for size, minor_tick in zip(self.size, self.n_minor_ticks)]
        self._major_minor_scale = 0.5
        
   #     self.grid_xy = self._create_grid(QtGui.QVector3D(*self.size), self.spacing, translation=(0.5, 0.5, 0))
        
        offset_xz = z_offset
        offset_yz = -z_offset 
        
        #self.grid_yz = self._create_grid(QtGui.QVector3D(*self.size), self.spacing, rotation=(90, 0, 1, 0), translation=(0 + offset_yz, 0.5, 0.5))
    #    self.grid_xz = self._create_grid(QtGui.QVector3D(*self.size), self.spacing, rotation=(90, 1, 0, 0), translation=(0.5, 1 + offset_xz, 0.5))
        
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
     #   widget.addItem(self.grid_xy)
     #   widget.addItem(self.grid_yz)
      #  widget.addItem(self.grid_xz)

        self.widget=widget
        
    def _create_grid(self, size, spacing, rotation=None, translation=None):        
        grid = GL3DAxisItem.CustomGrid(self.n_major_ticks[0],
                               "",
                               size=size)
  #      grid.setSize(*size)
        grid.setSpacing(*spacing)
        if rotation:
            grid.rotate(*rotation)        
        if translation:
            grid.translate(*translation)
        return grid

