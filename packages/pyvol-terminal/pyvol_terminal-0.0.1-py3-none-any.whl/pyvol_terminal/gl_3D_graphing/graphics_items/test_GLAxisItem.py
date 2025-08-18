#%%
#from pyvol_terminal.gl_3D_graphing.graphics_items.GLAxisItem import AxisGeometry
import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass, field
from pprint import pprint
from typing import Dict, Tuple, List
import math
from pprint import pprint
from matplotlib.axes import Axes



@dataclass(slots=True)
class AxisGeometry:
    axis: int
    origin: np.ndarray[float]
    planeRectSize: np.ndarray[float]
    graphPlaneOffset: np.ndarray[float] | float = field(default=0.) 
    tickLength: float = field(default=0.07)
    planeTickOffset: float = field(default=0.) 
    tickTextOffset: float = field(default=0.)
    tickValuesMinWidth: float = field(default=0.25)
    labelOffset: float  = field(default=0.)
    
    _planeAxis: int = field(init=False, default=None)
    _perpendicular_plane_axis: int = field(init=False, default=None)
    _Orientation: int = field(init=False, default=False)
    _cachedData: Dict[str, float|np.ndarray] = field(default=dict)
    _bounds: List[Tuple[float, float]] = field(default=list)
    
    def __post_init__(self):
        self._cachedData = {"planeBoundingRect" : None,
                            "tickBoundingRect" : None,
                            "tickValuesBoundingRect" : None,
                            "labelPosition" : None,
                            "tickValuesPosition" : None,
                           } 
        
        self._planeAxis = [i for i, val in enumerate(self.planeRectSize) if val != 0 and i != self.axis].pop(0)
        self._Orientation = int(-1 * self.planeRectSize[self._planeAxis] / abs(self.planeRectSize[self._planeAxis]))
        
        if isinstance(self.graphPlaneOffset, float):
            _perpendicular_plane_axis = [i for i in range(3) if i != self.axis and i != self._planeAxis].pop(0)
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
        
        position[self._planeAxis] += self.compute_offset(1 * self.planeTickOffset)

        size = [0., 0., 0.]
        size[self.axis] = self.planeRectSize[self.axis]
        size[self._planeAxis] = self.compute_offset(self.tickLength)            
        

        self._cachedData["tickBoundingRect"]=np.append(position, size)
        return self._cachedData["tickBoundingRect"]
    
    def tickValuesPosition(self):
        if not self._cachedData["tickValuesPosition"] is None:
            return self._cachedData["tickValuesPosition"]
        
        boundingRect = self.tickBoundingRect().copy()
        boundingRect[self._planeAxis] += boundingRect[3 + self._planeAxis] + self.compute_offset(self.tickTextOffset)
        self._cachedData["tickValuesPosition"] = boundingRect[:3]
        return self._cachedData["tickValuesPosition"]
    
    def tickValuesBoundingRect(self):
        if not self._cachedData["tickValuesBoundingRect"] is None:
            return self._cachedData["tickValuesBoundingRect"]
        
        size = [0., 0., 0.]
        size[self.axis] = self.planeRectSize[self.axis]
        size[self._planeAxis] = self.compute_offset(self.tickValuesMinWidth)
        self._cachedData["tickValuesBoundingRect"] = np.append(self.tickValuesPosition(), size)
        return self._cachedData["tickValuesBoundingRect"]
        
    def labelPosition(self):
        if not self._cachedData["labelPosition"] is None:
            return self._cachedData["labelPosition"]

        parentBoundingRect = self.tickValuesBoundingRect()
        position = parentBoundingRect.copy()[:3]
        
        position[self.axis] += 0.5 * self.planeRectSize[self.axis]
        position[self._planeAxis] += self.compute_offset(self.labelOffset)
        
        self.getRangeNoLabel()
        
        if any(lo <= val <= hi for val, (lo, hi) in zip(position, self._bounds)):
            lim_idx = (self.Orientation() + 1) // 2
            lim = self._bounds[self._planeAxis][lim_idx]
            position = parentBoundingRect.copy()[:3]
            position[self.axis] += 0.5 * self.planeRectSize[self.axis]
            position[self._planeAxis] = self.compute_offset(self.labelOffset) + lim
        self._cachedData["labelPosition"]=position
        return position
    
    def compute_offset(self, offset):
        return self.Orientation() * offset
    
    def getRangeNoLabel(self):
        axis_data_keys = ["planeBoundingRect", "tickBoundingRect", "tickValuesBoundingRect"]
        
        lims = [[],[],[]]
        
        for key in axis_data_keys:
            boundingRect = self._cachedData[key]
            for i in range(3):
                lims[i].append(boundingRect[i])
                lims[i].append(boundingRect[i] + boundingRect[3 + i])

        
        self._bounds = [(min(data), max(data)) for data in lims]
        


    
def plot_axis_geometry_2d(ax: plt.Axes, geometry: AxisGeometry, non_zero_dims, view_name: str):
    def extract_2d(arr):
        return [arr[non_zero_dims[0]], arr[non_zero_dims[1]]]
    
    def extract_2d_rect(arr6):
        pos = extract_2d(arr6[:3])
        size = extract_2d(arr6[3:])
        return pos + size
    
    plane_rect_2d = extract_2d_rect(geometry.planeBoundingRect())
    plane_pos = plane_rect_2d[:2]
    plane_size = plane_rect_2d[2:]
    
    tick_rect_2d = extract_2d_rect(geometry.tickBoundingRect())
    tick_pos = tick_rect_2d[:2]
    tick_size = tick_rect_2d[2:]
    
    tv_rect_2d = extract_2d_rect(geometry.tickValuesBoundingRect())
    tv_pos = tv_rect_2d[:2]
    tv_size = tv_rect_2d[2:]
    
    label_pos_2d = extract_2d(geometry.labelPosition())
    
    is_horizontal = (geometry.axis == non_zero_dims[0])
    
    
    dim1, dim2 = non_zero_dims
    bounds = {
        0: geometry._bounds[0],
        1: geometry._bounds[1],
        2: geometry._bounds[2],
    }
    
    x_min, x_max = bounds[dim1]
    y_min, y_max = bounds[dim2]
    bound_pos = (x_min, y_min)
    bound_size = (x_max - x_min, y_max - y_min)
    
    bound_rect = plt.Rectangle(bound_pos, bound_size[0], bound_size[1], 
                               fill=False, edgecolor='orange', linestyle='--', linewidth=1.5, label="plane")
    ax.add_patch(bound_rect)
    
    if is_horizontal:
        ax.plot([plane_pos[0], plane_pos[0] + plane_size[0]], 
                [plane_pos[1], plane_pos[1]], 'k-', linewidth=1, label="plane")
    else:
        ax.plot([plane_pos[0], plane_pos[0]], 
                [plane_pos[1], plane_pos[1] + plane_size[1]], 'k-', linewidth=1, label="plane")
    
    rect = plt.Rectangle(plane_pos, plane_size[0], plane_size[1], 
                         fill=False, edgecolor='blue', linestyle='--', label="plane")
    ax.add_patch(rect)
    
    if is_horizontal:
        for pos in np.linspace(tick_pos[0], tick_pos[0] + tick_size[0], 5):
            ax.plot([pos, pos], 
                    [tick_pos[1], tick_pos[1] + tick_size[1]], 'k-', linewidth=0.5)
    else:
        for pos in np.linspace(tick_pos[1], tick_pos[1] + tick_size[1], 5):
            ax.plot([tick_pos[0], tick_pos[0] + tick_size[0]], 
                    [pos, pos], 'k-', linewidth=0.5)
    
    tv_rect = plt.Rectangle(tv_pos, tv_size[0], tv_size[1], 
                            fill=False, edgecolor='green', linestyle='--', linewidth=1)
    ax.add_patch(tv_rect)
    
    ax.plot(label_pos_2d[0], label_pos_2d[1], 'ro', markersize=3)
    
    ax.set_aspect('equal')
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.set_xlabel(['X', 'Y', 'Z'][non_zero_dims[0]])
    ax.set_ylabel(['X', 'Y', 'Z'][non_zero_dims[1]])
    
    padding = 0.2  # Add some padding around the bounds
    ax.set_xlim(-2, 3)
    ax.set_ylim(-0.5, 3)
    ax.legend()
    
    ax.set_title(f"Axis {geometry.axis} Geometry ({view_name} View)")

# Create figure with 3 subplots


# Define the views to show
views = [
    ("XY", [0, 1]),  # X and Y dimensions
    ("XZ", [0, 2]),  # X and Z dimensions
    ("YZ", [1, 2])   # Y and Z dimensions
]






def get_nrows_ncols(n):
    nrows = math.floor(math.sqrt(n))
    ncols = math.floor(n / nrows)
    return nrows, ncols

figsize=(18, 5)




axis_geometry = AxisGeometry(
    axis=2,
    origin=np.array([0, 0, 0]),
    planeRectSize=np.array([0, 2., 2]),
    graphPlaneOffset=np.array([0., 0., 0]),
    tickLength=-0.3,
    planeTickOffset=0.4,
    tickTextOffset=0.05,
    tickValuesMinWidth=0.3
)

print(axis_geometry.origin)
print(axis_geometry.axis)


fig, axes = plt.subplots(*get_nrows_ncols(len(views)), figsize=figsize)
if isinstance(axes, np.ndarray):
    axes = axes.flatten()
else:
    axes = [axes]

for ax, (view_name, non_zero_dims) in zip(axes, views):
    plot_axis_geometry_2d(ax, axis_geometry, non_zero_dims, view_name)

plt.tight_layout()
plt.show()



#%%


AxisGeometry(axis=direction,
                                           origin=np.array(origin),
                                           planeRectSize=np.array(planeRectSize),
                                           graphPlaneOffset=planeOffset,
                                           tickLength=tickLength,
                                           planeTickOffset=planeTickOffset,
                                           tickTextOffset=tickValuesOffset,
                                           labelOffset=labelOffset,
                                           )