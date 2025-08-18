import numpy as np
from OpenGL import GL as opengl
from OpenGL import GLU

def map_2D_coords_to_3D(widget, x, y):
    widget_width = widget.width()
    widget_height = widget.height()
    device_pixel_ratio = widget.window().screen().devicePixelRatio()

    x_norm = x / widget_width
    y_norm = y / widget_height

    viewport = opengl.glGetIntegerv(opengl.GL_VIEWPORT)
    _, _, viewport_width, viewport_height = viewport
    
    mouse_x_physical = x_norm * viewport_width
    mouse_y_physical = y_norm * viewport_height
    mouse_y_physical = viewport_height - mouse_y_physical 
    
    depth = opengl.glReadPixels(int(mouse_x_physical), int(mouse_y_physical), 1, 1, opengl.GL_DEPTH_COMPONENT, opengl.GL_FLOAT)[0][0]

    modelview = np.array(widget.viewMatrix().data()).reshape(4, 4)
    projection = np.array(widget.projectionMatrix(viewport,
                                                  (0, 0, device_pixel_ratio * widget_width,
                                                   device_pixel_ratio* widget_height)
                                                  ).data()).reshape(4, 4)
    
    world_x, world_y, world_z = GLU.gluUnProject(mouse_x_physical, mouse_y_physical, depth, modelview, projection, viewport)

    return world_x, world_y, world_z

def map_3D_coords_to_2D(widget, world_x, world_y, world_z):
    device_pixel_ratio = widget.window().screen().devicePixelRatio()
    widget_height = widget.height()
    widget_width = widget.width()
    
    viewport = opengl.glGetIntegerv(opengl.GL_VIEWPORT)
    _, _, viewport_width, viewport_height = viewport
    
    modelview = np.array(widget.viewMatrix().data()).reshape(4, 4)
    projection = np.array(widget.projectionMatrix(viewport,
                                                  (0, 0, device_pixel_ratio * widget_width, device_pixel_ratio * widget_height)).data()).reshape(4, 4)
    
    px_x, px_y, px_z = GLU.gluProject(world_x, world_y, world_z, modelview, projection, viewport)
    px_x = viewport_width - px_x
    px_y = viewport_height - px_y
    
    return px_x, px_y, px_z

