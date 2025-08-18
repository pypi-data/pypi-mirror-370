#%% 

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes

class CubeVertex:
    def __init__(self, point, perp_axis_edge):
        self.point = point
        self.perp_axis_edge = perp_axis_edge

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

def plot_vertex_lines(ax: Axes, m: float, length: float = 0.3):
    cube_vertices = get_cube_coordinates()
    cube_vertices = [*cube_vertices[:3], cube_vertices[3]]

    for vertex in cube_vertices:
        x0, y0 = vertex.point
        if np.isinf(m):
            dx, dy = 0, length / 2
        else:
            dx = (length / 2) / np.sqrt(1 + m**2)
            dy = m * dx
        x_vals = [x0 - dx, x0 + dx]
        y_vals = [y0 - dy, y0 + dy]
        ax.plot(x_vals, y_vals, color='orange')

def get_cube_coordinates():
    p1 = CubeVertex((0, 0), (0, 1))
    p2 = CubeVertex((0, 1), (1, 0))
    p3 = CubeVertex((1, 0), (1, 1))
    p4 = CubeVertex((1, 1), (1, 0))
    
    return p1, p2, p3, p4
    
def plot_rectangle(ax: Axes, p1, p2, p3, p4, color='k', linestyle='-'):
    points = [p.point for p in [p1, p2, p4, p3, p1]]
    x_coords = [pt[0] for pt in points]
    y_coords = [pt[1] for pt in points]
    ax.plot(x_coords, y_coords, color=color, linestyle=linestyle, linewidth=1.2)

def plot_line_with_perpendiculars(ax: Axes, p1, p2, lim_ranges):
    intersections = get_boundary_intersections(p1, p2)
    
    if len(intersections) == 2:
        ax.plot([intersections[0][0], intersections[1][0]], 
                [intersections[0][1], intersections[1][1]], 'b-')
    
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    perp_slope = -dx/dy if dy != 0 else float('inf')
    
    for point in [p1, p2]:
        x0, y0 = point
        intersections = []
        
        if np.isinf(perp_slope):  
            intersections.append((x0, -10))
            intersections.append((x0, 10))
        else:
            perp_b = y0 - perp_slope*x0
            
            y = perp_slope*(-10) + perp_b
            if -10 <= y <= 10:
                intersections.append((-10, y))
                
            y = perp_slope*10 + perp_b
            if -10 <= y <= 10:
                intersections.append((10, y))
                
            x = (-10 - perp_b)/perp_slope
            if -10 <= x <= 10:
                intersections.append((x, -10))
                
            x = (10 - perp_b)/perp_slope
            if -10 <= x <= 10:
                intersections.append((x, 10))
        
        if len(intersections) == 2:
            ax.plot([intersections[0][0], intersections[1][0]], 
                    [intersections[0][1], intersections[1][1]], 'r-')
    
    cube_coords = get_cube_coordinates()
    plot_rectangle(ax, *cube_coords)
    
    plot_vertex_lines(ax, perp_slope, 1)
    
    ax.plot(p1[0], p1[1], 'go', markersize=5)
    ax.plot(p2[0], p2[1], 'go', markersize=5)
    ax.set_xlim(lim_ranges[0], lim_ranges[1])
    ax.set_ylim(lim_ranges[0], lim_ranges[1])

    ax.grid(True)
    ax.set_aspect('equal', adjustable='box')

fig, axs = plt.subplots(ncols=2, nrows=2, layout='constrained')
ax1, ax2, ax3, ax4 = axs.flatten()

lim_ranges = -2, 4

p1 = (0, 1)
p2 = (1.5, -0.3)
plot_line_with_perpendiculars(ax1, p1, p2, lim_ranges)

p1 = (0, 2)
p2 = (1.5, .7)
plot_line_with_perpendiculars(ax2, p1, p2, lim_ranges)

p1 = (-0.2, 1.05)
p2 = (1.8, 0.95)
plot_line_with_perpendiculars(ax3, p1, p2, lim_ranges)

plt.show()