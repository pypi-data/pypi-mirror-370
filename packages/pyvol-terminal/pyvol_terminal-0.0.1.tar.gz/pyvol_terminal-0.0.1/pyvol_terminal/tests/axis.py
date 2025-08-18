#%%%

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
    
    if len(extremums) != 0:
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


def verifyCoplanarDirection(direction, coplanarDirection):
    if coplanarDirection is not None and direction == coplanarDirection:
        raise ValueError(f"coplanarDirection must be different to direction")

    if not coplanarDirection in AxisGeometry.axesIndex() + AxisGeometry.axesString():
        raise ValueError(f"coplanarDirection must be either one of (0, 1, 2) or ('x', 'y', 'z')")
    
    if isinstance(coplanarDirection, str):
        coplanarDirection = AxisGeometry.getIndex(coplanarDirection)
        
    return coplanarDirection


def verifyVertexPointsDirection(viewRange, direction, vertexPoints) -> int:
    diff_ortho_vertices = np.array(vertexPoints["coplanar"]) - np.array(vertexPoints["perpendicular"])
    
    if  np.sum(diff_ortho_vertices == 0) > 1:
        raise ValueError(f"Coplanar and perpendicular points: {vertexPoints} are not orthogonal to each other")
    
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
                
                


def fromViewBoxRange(viewRange: list[list[float]] | Dict[str, list[float]],
                     direction: str | int=None,
                     axisVertexPoints: Dict[str, float] = None,
                     extremums: Tuple[int, int, int]|Dict[str, int]=None, #    extremum values must be either 0 or 1, and orients the axis origin in world coordinates. {"x" : int, "y" : int ,..} or (int, int ,int)
                     coplanarDirection: str | int | None = None,
                     ) -> Tuple[Tuple[float, float, float],
                                Tuple[float, float, float],
                                Tuple[float, float, float]
                                ]:
    
    if direction is None and axisVertexPoints is None:
        raise ValueError(".fromViewBoxRange requires either axisVertexPoints or direction and extremum") 
    
    if direction is not None:
        direction = verifyDirection(direction)
    
    if axisVertexPoints is not None:
        direction = verifyVertexPointsDirection(axisVertexPoints)
        axisOrigin = axisOrthoPoints["direction"].copy()
        axisOrigin[direction] = [vr for vr in worldRange[direction] if vr != axisVertexPoints["direction"][direction]][0]
        
        coplanarDirection = np.array(axisVertexPoints["coplanar"]) - np.array(axisOrigin) 
    
    else:
        
        if coplanarDirection is None or extremums is None:
            raise ValueError(f"If axisVertexPoints is None, coplanarDirection and extremums needs to be provided")
        else:
            coplanarDirection = verifyCoplanarDirection(coplanarDirection)
            extremums = verifyExtrumums(extremums)
            perpendicularDirection = np.delete([0, 1, 2], [direction, coplanarDirection]).item()
            
            
            axisOrigin = [None, None, None]
            
            for idx, ext in enumerate(extremums):
                axisOrigin[idx] = worldRange[idx][ext]

            directionVertex = axisOrigin.copy()
            worldRangeIdx = (extremums[idx] - i) // 2 
            directionVertex[direction] = worldRange[direction][worldRangeIdx]

            coplanarVertex = axisOrigin.copy()
            worldRangeIdx = (extremums[coplanarDirection] - i) // 2 
            coplanarVertex[coplanarDirection] = worldRange[coplanarDirection][worldRangeIdx]
            
            perpendicularVertex = axisOrigin.copy()
            worldRangeIdx = (extremums[perpendicularDirection] - i) // 2 
            perpendicularVertex[perpendicularDirection] = worldRange[perpendicularDirection][worldRangeIdx]

            axisVertexPoints = {"direction" : directionVertex,
                                "coplanarDirection" : coplanarVertex,
                                "perpendicularDirection" : perpendicularVertex
                                }
            
            return axisVertexPoints    
        
        

    if axisVertexPoints is not None:
        
        verifyAxisOrthoPoints(viewRange, axisVertexPoints)
        
        
        directionOriginValue = viewRange["direction"][0] if axisVertexPoints["direction"] == viewRange[direction][1] else viewRange["direction"][1]
        
        directionOrigin = axisVertexPoints["direction"].copy()
        directionOrigin[direction] = directionOriginValue
        
        if axisOrigin is not None:
            if tuple(axisOrigin) != tuple(directionOrigin):
                raise ValueError('the origin from axisOrthoPoints does not match the axisOrigin. Either set axisOrigin==None or set axisOrthoPoints==None and provide coplanarOrientation and perpendicularOrientation')
        
        
        coplanarDirection = [idx for idx, value in enumerate(directionOrigin) if value - axisVertexPoints["coplanar"][idx] != 0][0]
        perpendicularDirection = [idx for idx, value in enumerate(directionOrigin) if value - axisVertexPoints["perpendicular"][idx] != 0][0]

        
        
            
            
        
        axisOrigin = axisVertexPoints["direction"].copy()
        axisOrigin["direction"] = axisOrigin[:]
        
        
        
    
    if isinstance(viewRange, dict):
        viewRange = [viewRange['x'], viewRange['y'], viewRange['z']]
        
    if isinstance(coplanarDirection, str):
        if coplanarDirection not in AxisGeometry.axesIndex():
            raise ValueError("The coplanarDirection is not one of x, y or z")
        else:
            coplanarDirection = AxisGeometry.__ax_to_index(coplanarDirection)
    
    if isinstance(perpendicularDirection, str):
        if perpendicularDirection not in AxisGeometry.axesIndex():
            raise ValueError("The perpendicularDirection is not one of x, y or z")
        else:
            perpendicularDirection = AxisGeometry.__ax_to_index(perpendicularDirection)
    
    if coplanarDirection is None:
        coplanarDirection = [i for i in AxisGeometry.axesIndex() if i != direction and i != perpendicularDirection][0]
    
    elif perpendicularDirection is None:
        perpendicularDirection = [i for i in AxisGeometry.axesIndex() if i != direction and i != coplanarDirection][0]
    
    
    if all((coplanarDirection is None, perpendicularDirection is None)):
        raise ValueError("A coplanarDirection or perpendicularDirection is required")
    else:
        if len((direction, coplanarDirection, perpendicularDirection)) != len (set((direction, coplanarDirection, perpendicularDirection))):
            raise ValueError(f"direction, coplanarDirection and perpendicularDirection must all be different, given {(direction, coplanarDirection, perpendicularDirection)}")

    if axisOrigin is None:
        if all((coplanarDirection is None, perpendicularDirection is None)):
            raise ValueError("A coplanarDirection or perpendicularDirection is required")

        if any((coplanarOrientation is None, perpendicularOrientation is None)):
            raise ValueError("A coplanarOrientation and perpendicularOrientation must be provided when axisOrigin is not provided")

        
        perpendicularRange = viewRange[perpendicularDirection][1] - viewRange[perpendicularDirection][0]
    
    
        if perpendicularRange / abs(perpendicularRange) != perpendicularOrientation:
            ValueError("A perpendicularOrientation does not match the viewRange dimensions")
        
        coplanarRange = viewRange[coplanarDirection][1] - viewRange[coplanarDirection][0]
        
        if coplanarRange / abs(coplanarRange) != coplanarOrientation:
            ValueError("A coplanarOrientation does not match the viewRange dimensions")

        

        axisOrigin = [0, 0, 0]
        axisOrigin[direction] = viewRange[direction][0]
        
        perpViewRange = viewRange[perpendicularDirection]
        
        idx = (perpendicularOrientation - 1) // 2
        perpendicularAtOrigin = perpViewRange[idx]
        
        axisOrigin[perpendicularDirection] = perpendicularAtOrigin
        
        coplanarViewRange = viewRange[coplanarDirection]
        
        idx = (coplanarOrientation - 1) // 2
        coplanarAtOrigin = coplanarViewRange[idx]
        axisOrigin[coplanarDirection] = coplanarAtOrigin
    else:
        
        for idx, coord_value in enumerate(axisOrigin):
            if coord_value not in viewRange[idx]:
                raise ValueError(f"axisOrigin component {idx} ({coord_value}) not in viewRange {viewRange[idx]}")

    coplanarEdge = axisOrigin.copy()
    idx = (coplanarOrientation + 1) // 2        
    coplanarEdge[coplanarDirection] = viewRange[coplanarDirection][idx]
    
    idx = (perpendicularOrientation + 1) // 2
    perpendicularEdge = axisOrigin.copy()
    perpendicularEdge[perpendicularDirection] = viewRange[perpendicularDirection][idx]
    
    axisEdge = axisOrigin.copy()
    
    directionMaxValue = viewRange[direction][0] if viewRange[direction][1] == axisOrigin[direction] else viewRange[direction][1]
    
    axisEdge[direction] = directionMaxValue

            
    points = {"direction_0" : np.round(tuple(axisOrigin), 1).tolist(),
              "dir" : np.round(axisEdge, 1).tolist(),
              "coplanar" : np.round(tuple(coplanarEdge), 1).tolist(),
              "perp" : np.round(tuple(perpendicularEdge), 1).tolist(),
              
              }
    
    
    return points


def plot_points(points):

    origin = np.array(points["direction_0"])

    # Setup plot
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Plot origin
    ax.scatter(*origin, color='k')#   , label="direction_0 (origin)")

    # Define colors for each point
    colors = {
        "dir": "r",
        "coplanar": "g",
        "perp": "b"
    }

    # Plot other points and lines from origin
    for name, point in points.items():
        point = np.array(point)
        if name != "direction_0":
            ax.scatter(*point, color=colors[name], label=name)
            ax.plot([origin[0], point[0]], [origin[1], point[1]], [origin[2], point[2]], color=colors[name])

    # Axes labels and legend
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.legend()

    #ax.set_box_aspect([1, 1, 1])  # Optional: Equal aspect ratio

    plt.tight_layout()
    plt.show()


worldRange=[[-0.2, 1.5],
            [-0.7, 1.],
            [-0.1,1.5]
            ]



direction = 1
coplanarDirection = 0
coplanarOrientation = 1


perpendicularDirection = 2
perpendicularOrientation = -1
axisOrthoPoints = {
    "direction": 1.,
    "coplanar": 1.0,
    "perpendicular": 1.  # <-- this is a duplicate
}

points = fromViewBoxRange(worldRange,
                          direction, 
                      #    axisOrigin=axisOrigin,
                          coplanarDirection=coplanarDirection,
                          coplanarOrientation=coplanarOrientation,
                          perpendicularDirection=perpendicularDirection,
                          perpendicularOrientation=perpendicularOrientation
                          )


plot_points(points)



pprint(worldRange, width=15)
print(f"\norientation:\ncoplanar: {coplanarOrientation}\nperp: {perpendicularOrientation}")

pprint(points)


# %%
