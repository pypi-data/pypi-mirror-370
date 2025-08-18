


import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Tuple, Union, ClassVar
from pprint import pprint
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from collections import defaultdict

@dataclass(frozen=True, slots=True)
class AxisGeometry:
    __ax_to_index: ClassVar[Dict[str, int]] = {"x": 0, "y": 1, "z": 2}
    __index_to_ax: ClassVar[Dict[int, str]] = {0: "x", 1: "y", 2: "z"}
    
    @classmethod
    def getIndex(self, ax: str | int) -> int:
        return AxisGeometry.__ax_to_index.get(ax, None)
    
    @classmethod
    def getAxis(self, idx: int) -> str:
        return AxisGeometry.__index_to_ax.get(idx, None)
    
    @classmethod
    def axesIndex(cls):
        return list(AxisGeometry.__index_to_ax.keys())
    
    @classmethod
    def axesString(cls):
        return list(AxisGeometry.__ax_to_index.keys())



def verifyDirection(direction: str|int) -> int:
    if isinstance(direction, str):
        if direction not in AxisGeometry.axesIndex():
            raise ValueError("The direction is not one of x, y or z")
        else:
            direction = AxisGeometry.__ax_to_index(direction)            
    elif isinstance(direction, (int, float)) and not isinstance(direction, bool):
        if not direction in (0, 1, 2):
            raise ValueError("The direction is not one of axes indexes 0, 1, 2 (corresponds to: x, y, z)")            
    else:
        raise ValueError("The direction is not one of axes. Use one of 0, 1, 2 or x, y, z")
    return direction


def verifyAxisOrthoPoints(viewRange, axisVertexPoints):
    required_keys = {"direction", "coplanar", "perpendicular"}
    if set(axisVertexPoints) != required_keys:
        raise ValueError(f"axisOrthoPoints requires keys {required_keys}")
    
    value_to_keys = defaultdict(list)
    for key, val in axisVertexPoints.items():
        value_to_keys[val].append(key)
    
    value_to_rows = defaultdict(list)
    for i, row in enumerate(viewRange):
        for val in row:
            value_to_rows[val].append(i)
    
    overused_values = []
    for val, keys in value_to_keys.items():
        needed = len(keys)
        available = len(value_to_rows[val])
        if needed > available:
            overused_values.append((val, keys, needed, available))
    
    if overused_values:
        msgs = []
        for val, keys, needed, available in overused_values:
            keys_str = ", ".join(keys)
            msgs.append(f"value {val} used by [{keys_str}] requires {needed} distinct matches but only found {available}")
        raise ValueError("Invalid axisOrthoPoints mapping: " + " and ".join(msgs))


def verifyExtrumums(extremums):
    
    if len(extremums) != 3:
        raise ValueError(f"3 extremums are required, currently {len(extremums)}")
    
    if isinstance(extremums, dict):
        extremums_str = extremums.copy()
        extremums = 3*[None]
        for ax_str, ext in extremums_str.items():
            ax_idx = AxisGeometry.getIndex(ax_str)
            extremums[ax_idx] = ext
    
    if not all([ext in [0, 1] for ext in extremums]):
        raise ValueError("extremum values must be either 0 or 1")
    return extremums


def verifyPlaneDirection(direction, planeDirection):
    if planeDirection is not None and direction == planeDirection:
        raise ValueError(f"planeDirection must be different to direction")

    if not planeDirection in AxisGeometry.axesIndex() + AxisGeometry.axesString():
        raise ValueError(f"planeDirection must be either one of (0, 1, 2) or ('x', 'y', 'z')")
    
    if isinstance(planeDirection, str):
        planeDirection = AxisGeometry.getIndex(planeDirection)
        
    return planeDirection


def verifyVertexPointsDirection(viewRange, direction, vertexPoints) -> int:
    diff_ortho_vertices = np.array(vertexPoints["planeDirection"]) - np.array(vertexPoints["perpendicularDirection"])
    
    if  np.sum(diff_ortho_vertices == 0) > 1:
        raise ValueError(f"planeDirection and perpendicularDirection: {vertexPoints} are not orthogonal to each other")
    
    directionFromVertices = diff_ortho_vertices[diff_ortho_vertices == 0].astype(int)
    
    if direction is not None and direction != directionFromVertices:
        raise ValueError(f"The given axis-direction {direction} is not the axis for the axisVertexPoints")
    
    if direction is None:
        direction = directionFromVertices
    
    for ax, point in vertexPoints.items():
        for idx, p in enumerate(point):
            lim = viewRange[idx]
            if not p in lim:
                raise ValueError(f"Vertex direction: {ax} with point {point} is not in viewRange {lim}")
    
    return direction
                
                