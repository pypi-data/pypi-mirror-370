#%% 

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
import math

class CubeVertex:
    def __init__(self, axis, point, perp_axis_edge, adj_axis_edge, perpendicular_size, adjacent_size):
        self.axis=axis
        self.point = point
        self.perp_axis_edge=perp_axis_edge
        self.adj_axis_edge = adj_axis_edge
        self.perpendicular_size = perpendicular_size
        self.adjacent_size = adjacent_size

        self.slope = self._slope()
      #  self.
    
    def _slope(self):
        dx = self.adj_axis_edge[0] - self.point[0]
        dy = self.adj_axis_edge[1] - self.point[1]
        slope = dy/dx if dx != 0 else float('inf')
        return round(slope, 1)


def anticlockwise_angle(p1, p2, k2):
    v1 = np.array(p2) - np.array(p1)
    v2 = np.array(k2) - np.array(p1)

    dot = np.dot(v1, v2)
    det = v1[0]*v2[1] - v1[1]*v2[0]  # 2D cross product

    angle_rad = np.arctan2(det, dot)  # signed angle (-π to π)
    anticlockwise_angle = angle_rad % (2 * np.pi)  # wrap to [0, 2π)
    return np.degrees(anticlockwise_angle)


def clockwise_angle(p1, p2, k2):
    v1 = np.array(p2) - np.array(p1)
    v2 = np.array(k2) - np.array(p1)

    dot = np.dot(v1, v2)
    det = v1[0]*v2[1] - v1[1]*v2[0]  

    angle_rad = np.arctan2(det, dot) 
    clockwise_angle = (-angle_rad) % (2 * np.pi)
    return np.degrees(clockwise_angle)

def offset_from_p1_viewed_from_p2(p1, p2, distance=5, side="left"):
    p1 = np.array(p1)
    p2 = np.array(p2)
    
    # Direction vector from p2 to p1
    direction = p1 - p2
    
    # Normalize direction vector
    norm = np.linalg.norm(direction)
    if norm == 0:
        raise ValueError("p1 and p2 cannot be the same point.")
    direction = direction / norm
    
    # Perpendicular direction
    if side == "left":
        perp = np.array([-direction[1], direction[0]])  # 90° CCW
    elif side == "right":
        perp = np.array([direction[1], -direction[0]])  # 90° CW
    else:
        raise ValueError("side must be 'left' or 'right'")
    
    return p1 + distance * perp  


def get_boundary_intersections(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    intersections = []
    
    if x1 == x2:
        return [(x1, -10), (x1, 10)]
    
    m = (y2 - y1)/(x2 - x1)
    b = y1 - m*x1
    
    y = m*(-10) + b
    if -10 <= y <= 10:
        intersections.append((-10, y))
        
    y = m*10 + b
    if -10 <= y <= 10:
        intersections.append((10, y))
        
    x = (-10 - b)/m
    if -10 <= x <= 10:
        intersections.append((x, -10))
        
    x = (10 - b)/m
    if -10 <= x <= 10:
        intersections.append((x, 10))
        
    return intersections

def intersection_from_point_slope(p1, m1, p2, m2):
    x1, y1 = p1
    x2, y2 = p2

    if m1 == m2:
        return None  # Lines are parallel, no intersection (or infinite if same line)

    # Handle vertical lines (infinite slope)
    if np.isinf(m1):
        x = x1
        y = m2 * (x - x2) + y2
    elif np.isinf(m2):
        x = x2
        y = m1 * (x - x1) + y1
    else:
        x = (m1 * x1 - m2 * x2 + y2 - y1) / (m1 - m2)
        y = m1 * (x - x1) + y1

    return x, y

def left_or_right(p1, p2, p3):
    p1 = np.array(p1)
    p2 = np.array(p2)
    p3 = np.array(p3)

    v1 = p2 - p1
    v2 = p3 - p1

    cross = v1[0] * v2[1] - v1[1] * v2[0]

    if cross > 0:
        return 'left'
    elif cross < 0:
        return 'right'
    else:
        return 'on the line'
    
    
def plot_vertex_lines(ax: Axes, p2: float, m: float, length: float = 0.3):
    cube_vertices = get_cube_coordinates()
    cube_vertices = [*cube_vertices[:3], cube_vertices[3]]
    degrees = []
    degrees_anti = []
    idx=0
    for vertex in cube_vertices:
      #  if vertex.point == (0, 1):
       #     continue
        x0, y0 = vertex.point
        if np.isinf(m):
            dx, dy = 0, length / 2
        else:
            dx = (length / 2) / np.sqrt(1 + m**2)
            dy = m * dx
            
        m1 = - 1 / m   # vertex slope
        m2 = m
        
        point_intersection = intersection_from_point_slope(vertex.point, m1, p2, m2)

            
        x_vals = [x0 - dx, x0 + dx]
        y_vals = [y0 - dy, y0 + dy]
        
        x1, y1 = offset_from_p1_viewed_from_p2(vertex.point, point_intersection, distance=length, side="left")
        axis_tick_origin = offset_from_p1_viewed_from_p2(vertex.adj_axis_edge, point_intersection, distance=length, side="left")
        
        axis_tick_pos = [(0, 0) for _ in range(5)]
      #  for idx, size in :
     #       axis_tick_pos[vertex.axis] = size
     
        start_tick_pos = [(0, 0) for _ in range(5)]


        ax_input = [ np.zeros(5).tolist(), np.zeros(5).tolist()]        

        ax_input[1 - vertex.axis] = 0.3
        end_tick_pos = []
        
        increments = (np.array(vertex.adj_axis_edge) - np.array(vertex.point)) / 5
        pos_s = list(vertex.point)
        for idx in range(6):
            
            pos_e = pos_s.copy()
            pos_e[1 - vertex.axis] += 0.3
            
            
            tick_x = [pos_s[0], pos_e[0]]
            tick_y = [pos_s[1], pos_e[1]]
            
            ax.plot(tick_x, tick_y, color='red')
            
            pos_s += increments
        print(increments)
        
        side = left_or_right(vertex.point, vertex.adj_axis_edge, p2)
            

            
        
        

        x_vals = [x0 , x1]
        y_vals = [y0 , y1]
        
        
        
        
      #  ax.plot(x_vals, y_vals, color='orange')
        
        
        
        ax.text(x0, y0,
                str(vertex.adj_axis_edge) ,#+ f"\n{idx}",
                #side,
                ha='center', va='center', color="k", size=7
                )
        
        
        deg = clockwise_angle(vertex.point, vertex.adj_axis_edge, p2)
        deg_rounded = deg % 90
        
        point_intersection_rounded = np.round(point_intersection, 1).tolist()
        
        
        string = str(round(deg, 1)) + f"     ({str(round(deg_rounded, 1))})"#f"     {str(tuple(point_intersection_rounded))}"
        degrees.append(string)
        idx+=1
    
    return degrees


def get_cube_coordinates():
    p1 = CubeVertex(0, (0, 0), (0, 1), (1, 0), 1, 1)
    p2 = CubeVertex(1, (0, 1), (0, 0), (0, 0), 1, 1)
    p3 = CubeVertex(1, (1, 0), (1, 0), (1, 1), 1, 1)
    p4 = CubeVertex(0, (1, 1), (1, 0), (0, 1), 1, 1)

    return p1, p2, p3, p4
    
def plot_rectangle(ax: Axes, p1, p2, p3, p4, color='k', linestyle='-'):
    points = [p.point for p in [p1, p2, p4, p3, p1]]
    x_coords = [pt[0] for pt in points]
    y_coords = [pt[1] for pt in points]
    ax.plot(x_coords, y_coords, color=color, linestyle=linestyle, linewidth=1.2)

def plot(ax: Axes, p1, p2, lim_ranges):
    intersections = get_boundary_intersections(p1, p2)
    
    if len(intersections) == 2:
        ax.plot([intersections[0][0], intersections[1][0]], 
                [intersections[0][1], intersections[1][1]], 'b-')
    
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    perp_slope_p1_p2 = -dx/dy if dy != 0 else float('inf')
    
    for point in [p1, p2]:
        x0, y0 = point
        intersections = []
        
        if np.isinf(perp_slope_p1_p2):  
            intersections.append((x0, -10))
            intersections.append((x0, 10))
        else:
            adj_b = y0 - perp_slope_p1_p2*x0
            
            y = perp_slope_p1_p2*(-10) + adj_b
            if -10 <= y <= 10:
                intersections.append((-10, y))
                
            y = perp_slope_p1_p2*10 + adj_b
            if -10 <= y <= 10:
                intersections.append((10, y))
                
            x = (-10 - adj_b)/perp_slope_p1_p2
            if -10 <= x <= 10:
                intersections.append((x, -10))
                
            x = (10 - adj_b)/perp_slope_p1_p2
            if -10 <= x <= 10:
                intersections.append((x, 10))
        
        if len(intersections) == 2:
            ax.plot([intersections[0][0], intersections[1][0]], 
                    [intersections[0][1], intersections[1][1]], 'r-')
    
    cube_coords = get_cube_coordinates()
    plot_rectangle(ax, *cube_coords)
    

    degrees = plot_vertex_lines(ax, p2, perp_slope_p1_p2, 1)
    
    
    text_str = "\n".join(degrees)
    ax.text(lim_ranges[0], lim_ranges[1], text_str, ha='left', va='top', color="k", size=10)


    ax.plot(p1[0], p1[1], 'go', markersize=5)
    ax.plot(p2[0], p2[1], 'go', markersize=5)
    ax.set_xlim(lim_ranges[0], lim_ranges[1])
    ax.set_ylim(lim_ranges[0], lim_ranges[1])
    
    shift = np.zeros(2) - p1
    
    p2_shift = shift + p2
    
    
    
    angle_point = math.degrees(math.atan2(p2[1], p2[0]))
    angle_shift = math.degrees(math.atan2(p2_shift[1], p2_shift[0]))
    
    ax.set_title(f"angle_point: {round(angle_point, 1)}\nangle_shift: {round(angle_shift, 1)}", fontsize=8)
    print(f"adj_slope: {perp_slope_p1_p2}")

    ax.grid(True)
    ax.set_aspect('equal', adjustable='box')

fig, axs = plt.subplots(nrows=2, ncols=2, figsize=(7, 7), layout="tight")

print(np.shape(axs.flatten()))
ax1, ax2, ax3, ax4 = axs.flatten()
#ax1, ax2, ax3, ax4, ax5, ax6 = axs.flatten()

lim_ranges = -1.5, 3

p1 = (-0.9, 1.1)
p2 = (0.8, -1.)



plot(ax1, p1, p2, lim_ranges)

p1 = (-0.2, 1.3)
p2 = (-0.7, -0.8)



plot(ax2, p1, p2, lim_ranges)

p1 = (-0.2, 1.05)
p2 = (1.8, 0.95)
plot(ax3, p1, p2, lim_ranges)

p1 = (-0.8, 0.6)
p2 = (1.8, 1.3)
plot(ax4, p1, p2, lim_ranges)

"""p1 = (-0.8, 0.6)
p2 = (1.5, 1.5)
plot(ax5, p1, p2, lim_ranges)

p1 = (-0.8, 0.6)
p2 = (0.8, 1.8)
plot(ax6, p1, p2, lim_ranges)
"""

plt.subplots_adjust(wspace=0, hspace=0)


plt.show()


#%%
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np

# Cube bounds
x_min, x_max = 0, 2
y_min, y_max = 0, 2
z_min, z_max = 0, 2

# Vertices
vertices = np.array([
    [x_min, y_min, z_min],
    [x_max, y_min, z_min],
    [x_max, y_max, z_min],
    [x_min, y_max, z_min],
    [x_min, y_min, z_max],
    [x_max, y_min, z_max],
    [x_max, y_max, z_max],
    [x_min, y_max, z_max],
])

# Faces
faces = [
    [vertices[i] for i in [0, 1, 2, 3]],
    [vertices[i] for i in [4, 5, 6, 7]],
    [vertices[i] for i in [0, 1, 5, 4]],
    [vertices[i] for i in [2, 3, 7, 6]],
    [vertices[i] for i in [1, 2, 6, 5]],
    [vertices[i] for i in [0, 3, 7, 4]],
]

# Define worldRange from cube bounds
worldRange = np.array([
    [x_min, x_max],
    [y_min, y_max],
    [z_min, z_max],
])

# Compute axis-aligned unit vectors scaled by cube dimension
axis_vectors = [
    np.array([worldRange[0][1] - worldRange[0][0], 0, 0]),
    np.array([0, worldRange[1][1] - worldRange[1][0], 0]),
    np.array([0, 0, worldRange[2][1] - worldRange[2][0]]),
]


scale = 0.25
scaled_vectors = [v * scale for v in axis_vectors]
# Previous code remains the same until the plotting section...
# Previous code remains the same until the plotting section...

fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(111, projection='3d')
prism = Poly3DCollection(faces, edgecolors='black', linewidths=1, alpha=0.25)
ax.add_collection3d(prism)

# Define colors for different cross products
cross_colors = ['red', 'purple']  # red for i×j, purple for j×i

for k in range(3):  # Main axis loop
    i, j = [d for d in range(3) if d != k]  # Get perpendicular axes
    
    
   # if i > 0:
    #    continue
   # if j != 2:
   #     continue
    
    
    for vertex in vertices:
        vec_i = scaled_vectors[i]
        vec_j = scaled_vectors[j]
        
        # Compute both cross products
        cross_ij = np.cross(vec_i, vec_j)
        cross_ji = np.cross(vec_j, vec_i)
        
        
        
        
        side_cube = vertex[k]
        
        k_range = worldRange[k]
        
        other_side = k_range[k_range != side_cube].item()
        center_direction = other_side - side_cube
        center_direction = center_direction / abs(center_direction)
        
        cross_ij_dir = cross_ij[k] / abs(cross_ij[k])
        cross_ji_dir = cross_ji[k] / abs(cross_ji[k])
        
        
        
        
        cross_ij = cross_ij / np.linalg.norm(cross_ij) * scale * 1.5
        cross_ji = cross_ji / np.linalg.norm(cross_ji) * scale * 1.5
        
        if cross_ij_dir != center_direction:
            cross_ij[k] *=-1
        if cross_ji_dir != center_direction:
            cross_ji[k] *=-1

            
        x_cross, y_cross, z_cross = zip(vertex, vertex + cross_ij)
        ax.plot(x_cross, y_cross, z_cross, color=cross_colors[0], linewidth=3, alpha=0.7)
            
        label_pos_ij = vertex + cross_ij * 1.1
        ax.text(label_pos_ij[0], label_pos_ij[1], label_pos_ij[2], 
            f"{['X','Y','Z'][i]}×{['X','Y','Z'][j]}", 
            color=cross_colors[0], fontsize=8)

        x_cross, y_cross, z_cross = zip(vertex, vertex + cross_ji)
        ax.plot(x_cross, y_cross, z_cross, color=cross_colors[1], linewidth=3, alpha=0.7)
        
        label_pos_ji = vertex + cross_ji * 1.1
        ax.text(label_pos_ji[0], label_pos_ji[1], label_pos_ji[2], 
            f"{['X','Y','Z'][j]}×{['X','Y','Z'][i]}", 
            color=cross_colors[1], fontsize=8)

# Axes config
ax.set_xlim([x_min, x_max])
ax.set_ylim([y_min, y_max])
ax.set_zlim([z_min, z_max])
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_box_aspect([x_max - x_min, y_max - y_min, z_max - z_min])
plt.tight_layout()
plt.title('Cross Products in Both Directions')
plt.show()