import sys
import numpy as np
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel
from PySide6.QtCore import Qt
import pyqtgraph as pg
import pyqtgraph.opengl as gl
from pyqtgraph.Qt import QtCore
from OpenGL import GL, GLU

def map_2D_coords_to_3D(widget, x: float, y: float):
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
    
    return pg.Vector(world_x, world_y, world_z)



class MeshPointIntersectionDemo(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Set up the main window
        self.setWindowTitle("Mesh-Point Intersection Demo")
        self.setGeometry(100, 100, 1000, 800)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create information label
        self.info_label = QLabel("Click anywhere in the 3D view to test for intersection with the mesh")
        self.info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.info_label)
        
        # Create the 3D view
        self.view = gl.GLViewWidget()
        layout.addWidget(self.view, 1)
        
        # Configure the view
        self.view.setCameraPosition(distance=20, elevation=30, azimuth=45)
        
        # Add coordinate system
        self.view.addItem(gl.GLAxisItem())
        
        # Create and add the mesh (a plane similar to GridItem)
        self.mesh_item = self.create_plane_mesh()
        self.view.addItem(self.mesh_item)
        
        # Create and add a point item to visualize the test point
        self.point_item = gl.GLScatterPlotItem(
            pos=np.array([[0, 0, 0]]), 
            color=(1, 0, 0, 1), 
            size=0.5, 
            pxMode=False
        )
        self.view.addItem(self.point_item)
        
        # Add a grid for reference
        grid = gl.GLGridItem()
        grid.setSize(10, 10, 10)
        grid.setSpacing(1, 1, 1)
        self.view.addItem(grid)
        
        # Connect mouse click event
        self.view.mousePressEvent = self.handle_mouse_click

    def create_plane_mesh(self):
        """Create a plane mesh similar to GridItem but with solid triangles"""
        # Create vertices for a plane
        x = np.linspace(-5, 5, 20)
        y = np.linspace(-5, 5, 20)
        z = np.zeros(20)
        
        verts = []
        faces = []
        
        # Create vertices and faces
        for i in range(len(x) - 1):
            for j in range(len(y) - 1):
                # Define four vertices for a quad
                v1 = [x[i], y[j], 0]
                v2 = [x[i+1], y[j], 0]
                v3 = [x[i+1], y[j+1], 0]
                v4 = [x[i], y[j+1], 0]
                
                # Add vertices to list
                start_idx = len(verts)
                verts.extend([v1, v2, v3, v4])
                
                # Create two triangles for each quad
                faces.append([start_idx, start_idx+1, start_idx+2])
                faces.append([start_idx, start_idx+2, start_idx+3])
        
        # Convert to numpy arrays
        verts = np.array(verts, dtype=np.float32)
        faces = np.array(faces, dtype=np.uint32)
        
        # Create mesh item
        mesh = gl.GLMeshItem(
            vertexes=verts, 
            faces=faces, 
            smooth=False,
            color=(0, 0.7, 1, 0.5),  # Semi-transparent blue
            drawEdges=True,
            edgeColor=(0, 0, 0, 1)    # Black edges
        )
        return mesh

    def handle_mouse_click(self, event):
        """Handle mouse clicks to test for intersection"""
        # Only handle left clicks
        if event.button() != QtCore.Qt.LeftButton:
            return
        
        # Get mouse position in view coordinates
        pos = event.pos()
        
        # Convert to 3D world coordinates
        
        
        
        world_pos = map_2D_coords_to_3D(self.view, pos.x(), pos.y())
        if world_pos is None:
            return
        
        # Create a QVector3D point
        point = pg.Vector(world_pos.x(), world_pos.y(), world_pos.z())
        
        # Update the test point visualization
        self.point_item.setData(pos=np.array([[point.x(), point.y(), point.z()]]))
        
        # Test for intersection
        intersection = self.ray_mesh_intersection(self.mesh_item, point)
        
        # Update the info label
        if intersection:
            self.info_label.setText(
                f"Intersection found at: ({intersection.x():.2f}, {intersection.y():.2f}, {intersection.z():.2f})"
            )
            self.info_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.info_label.setText("No intersection found")
            self.info_label.setStyleSheet("color: red; font-weight: bold;")
        
        # Update the view
        self.view.update()
        
        # Call the original mousePressEvent to handle camera rotation
        super(gl.GLViewWidget, self.view).mousePressEvent(event)

    def ray_mesh_intersection(self, mesh_item, point, direction=None):
        """
        Check if a ray from point in direction intersects with the mesh.
        Returns intersection point or None.
        """
        # Default direction is downward (negative Z)
        if direction is None:
            direction = pg.Vector(0, 0, -1)
        
        # Get mesh data
        md = mesh_item.meshData
        vertices = md.vertexes()
        faces = md.faces()
        
        closest_intersection = None
        min_distance = float('inf')
        
        # Check each triangle
        for face in faces:
            v0 = pg.Vector(*vertices[face[0]])
            v1 = pg.Vector(*vertices[face[1]])
            v2 = pg.Vector(*vertices[face[2]])
            
            # Apply mesh transformation to vertices
            transform = mesh_item.transform()
            v0 = transform.map(v0)
            v1 = transform.map(v1)
            v2 = transform.map(v2)
            
            # Ray-triangle intersection test
            intersection = self.ray_triangle_intersection(point, direction, v0, v1, v2)
            if intersection:
                # Calculate distance to the intersection point
                dist = (intersection - point).length()
                if dist < min_distance:
                    min_distance = dist
                    closest_intersection = intersection
                    
        return closest_intersection

    def ray_triangle_intersection(self, origin, direction, v0, v1, v2):
        """Möller–Trumbore ray-triangle intersection algorithm"""
        epsilon = 1e-6
        
        edge1 = v1 - v0
        edge2 = v2 - v0
        h = direction.cross(edge2)
        a = edge1.dot(h)
        
        if a > -epsilon and a < epsilon:
            return None  # Ray parallel to triangle
            
        f = 1.0 / a
        s = origin - v0
        u = f * s.dot(h)
        
        if u < 0.0 or u > 1.0:
            return None
            
        q = s.cross(edge1)
        v = f * direction.dot(q)
        
        if v < 0.0 or u + v > 1.0:
            return None
            
        t = f * edge2.dot(q)
        if t > epsilon:
            return origin + direction * t
        else:
            return None

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MeshPointIntersectionDemo()
    window.show()
    sys.exit(app.exec())