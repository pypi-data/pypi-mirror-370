from pyqtgraph.opengl import GLViewWidget, GLMeshItem, MeshData
import numpy as np

# Create a view
view = GLViewWidget()

# Define a cube mesh (or any custom shape)
cube = MeshData.cube()

# Positions: Nx3 array of points
positions = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]])

# Create instanced mesh item
mesh_item = GLMeshItem(
    meshdata=cube,
    smooth=False,
    shader="shaded",
    glOptions="additive",
)
mesh_item.setData(positions=positions)  # Set positions
view.addItem(mesh_item)

from pyqtgraph.opengl import GLScatterPlotItem

scatter = GLScatterPlotItem()
scatter.setData(pos=positions, size=0.5, pxMode=False)

# Use a custom shader (disable spherical discard)
scatter.__glOpts["shader"].shaders[0].frag = """
#version 150
in vec4 vColor;
out vec4 fragColor;
void main() {
    fragColor = vColor;  // Draws squares (no discard)
}
"""
scatter.update()  # Force shader update