
from OpenGL.GL import *  # noqa
import numpy as np
import math
import importlib
from OpenGL import GL


from pyqtgraph.Qt import QtGui, QT_LIB
from OpenGL.GL import shaders
from pyqtgraph.opengl.GLGraphicsItem import GLGraphicsItem

QtOpenGL = importlib.import_module(f"{QT_LIB}.QtOpenGL")
__all__ = ['GLScatterPlotItem']


class CustomGLScatterPlotItem2(GLGraphicsItem):
    """Draws points at a list of 3D positions."""
    
    _shaderProgram = None

    def __init__(self, parentItem=None, **kwds):
        super().__init__()
        glopts = kwds.pop('glOptions', 'opaque')
        self.setGLOptions(glopts)
        self.vertices = None 
        if isinstance(kwds["color"], str):
            qcolor =  QtGui.QColor(kwds["color"])
            normalised_rgba = (qcolor.redF(), qcolor.greenF(), qcolor.blueF(), qcolor.alphaF())
            kwds["color"] = normalised_rgba
        self.color=normalised_rgba
        self.size = 10
        self.pxMode = True

        self.m_vbo_position = QtOpenGL.QOpenGLBuffer(QtOpenGL.QOpenGLBuffer.Type.VertexBuffer)
        self.m_vbo_color = QtOpenGL.QOpenGLBuffer(QtOpenGL.QOpenGLBuffer.Type.VertexBuffer)
        self.vbos_uploaded = False

        self.setParentItem(parentItem)
        self.setData(**kwds)

    def setData(self, **kwds):
        args = ['pos', 'color', 'size']
        for k in kwds.keys():
            if k not in args:
                raise Exception(f'Invalid keyword argument: {k} (allowed arguments are {str(args)})')
            
        if 'pos' in kwds:
            pos = kwds.pop('pos')
            # Convert positions to triangles (each point becomes a small triangle)
            self.vertices = self._create_triangle_vertices(pos)
            
        if 'color' in kwds:
            color = kwds.pop('color')
            if isinstance(color, np.ndarray):
                color = np.ascontiguousarray(color, dtype=np.float32)
            self.color = color
        if 'size' in kwds:
            size = kwds.pop('size')
            if isinstance(size, np.ndarray):
                size = np.ascontiguousarray(size, dtype=np.float32)
            self.size = size

            
        self.pxMode = kwds.get('pxMode', self.pxMode)

        self.vbos_uploaded = False
        self.update()

    def _create_triangle_vertices(self, centers):
        vertices = []
        base_size = 0.01  # This empirically matches GLScatterPlotItem's size
        
        for center in centers:
            # Create a small triangle in screen space
            v1 = center + np.array([-base_size, -base_size, 0])
            v2 = center + np.array([base_size, -base_size, 0])
            v3 = center + np.array([0, base_size, 0])
            
            vertices.extend([v1, v2, v3])
            
        return np.ascontiguousarray(vertices, dtype=np.float32)
    
    def paint(self):
        if self.vertices is None:
            return

        self.setupGLState()
        
        mat_mvp = self.mvpMatrix()
        mat_mvp = np.array(mat_mvp.data(), dtype=np.float32)
        mat_modelview = self.modelViewMatrix()
        mat_modelview = np.array(mat_modelview.data(), dtype=np.float32)

        program = self.getShaderProgram()
        
        # Calculate scaling factor
        scale = 0
        if self.pxMode:
            view = self.view()
            if view is not None:
                scale = 2.0 * math.tan(math.radians(0.5 * view.opts["fov"])) / view.height()

        if not self.vbos_uploaded:
            self.upload_vbo(self.m_vbo_position, self.vertices)
            if isinstance(self.color, np.ndarray):
                # Repeat colors for each vertex in the triangle
                colors = np.repeat(self.color, len(self.vertices)//len(self.color), axis=0)
                self.upload_vbo(self.m_vbo_color, colors)
            self.vbos_uploaded = True

        enabled_locs = []

        if (loc := GL.glGetAttribLocation(program, "a_position")) != -1:
            self.m_vbo_position.bind()
            GL.glVertexAttribPointer(loc, 3, GL.GL_FLOAT, False, 0, None)
            self.m_vbo_position.release()
            enabled_locs.append(loc)

        if (loc := GL.glGetAttribLocation(program, "a_color")) != -1:
            if isinstance(self.color, np.ndarray):
                self.m_vbo_color.bind()
                GL.glVertexAttribPointer(loc, 4, GL.GL_FLOAT, False, 0, None)
                self.m_vbo_color.release()
                enabled_locs.append(loc)
            else:
                color = self.color
                if isinstance(color, QtGui.QColor):
                    color = color.getRgbF()
                GL.glVertexAttrib4f(loc, *color)

        for loc in enabled_locs:
            GL.glEnableVertexAttribArray(loc)

        with program:
            # Set uniforms
            loc = GL.glGetUniformLocation(program, "u_mvp")
            GL.glUniformMatrix4fv(loc, 1, False, mat_mvp)
            loc = GL.glGetUniformLocation(program, "u_modelview")
            GL.glUniformMatrix4fv(loc, 1, False, mat_modelview)
            loc = GL.glGetUniformLocation(program, "u_scale")
            GL.glUniform1f(loc, scale)
            
            GL.glDrawArrays(GL.GL_TRIANGLES, 0, len(self.vertices))
            
        for loc in enabled_locs:
            GL.glDisableVertexAttribArray(loc)
            
    def upload_vbo(self, vbo, arr):
        if arr is None:
            vbo.destroy()
            return
        if not vbo.isCreated():
            vbo.create()
        vbo.bind()
        vbo.allocate(arr, arr.nbytes)
        vbo.release()

    @staticmethod
    def getShaderProgram():
        klass = CustomGLScatterPlotItem2

        if klass._shaderProgram is not None:
            return klass._shaderProgram

        ctx = QtGui.QOpenGLContext.currentContext()
        fmt = ctx.format()

        if ctx.isOpenGLES():
            if fmt.version() >= (3, 0):
                glsl_version = "#version 300 es\n"
                sources = SHADER_CORE
            else:
                glsl_version = "#version 100\n"
                sources = SHADER_LEGACY
        else:
            if fmt.version() >= (3, 1):
                glsl_version = "#version 140\n"
                sources = SHADER_CORE
            else:
                glsl_version = "#version 120\n"
                sources = SHADER_LEGACY

        compiled = [shaders.compileShader([glsl_version, v], k) for k, v in sources.items()]
        program = shaders.compileProgram(*compiled)

        # bind generic vertex attrib 0 to "a_position" so that
        # vertex attrib 0 definitely gets enabled later.
        GL.glBindAttribLocation(program, 0, "a_position")
        GL.glLinkProgram(program)

        klass._shaderProgram = program
        return program

    def setupGLState(self):
        glEnable(GL_DEPTH_TEST)  # Crucial for proper depth sorting
        glDisable(GL_BLEND)      # Disable blending
        glDepthFunc(GL_LESS)     # Standard depth comparison
        glDisable(GL_ALPHA_TEST) # Not needed for opaque objects
        
def _is_compatibility_profile(context):
    # https://stackoverflow.com/questions/73745603/detect-the-opengl-context-profile-before-version-3-2
    sformat = context.format()
    profile = sformat.profile()

    # >= 3.2 has {Compatibility,Core}Profile
    # <= 3.1 is NoProfile

    if profile == sformat.OpenGLContextProfile.CompatibilityProfile:
        compat = True
    elif profile == sformat.OpenGLContextProfile.CoreProfile:
        compat = False
    else:
        compat = False
        version = sformat.version()

        if version <= (2, 1):
            compat = True
        elif version == (3, 0):
            if sformat.testOption(sformat.FormatOption.DeprecatedFunctions):
                compat = True
        elif version == (3, 1):
            if context.hasExtension(b'GL_ARB_compatibility'):
                compat = True

    return compat


## See:
##
##  http://stackoverflow.com/questions/9609423/applying-part-of-a-texture-sprite-sheet-texture-map-to-a-point-sprite-in-ios
##  http://stackoverflow.com/questions/3497068/textured-points-in-opengl-es-2-0
##
##
SHADER_LEGACY = {
    GL.GL_VERTEX_SHADER : """
        uniform mat4 u_mvp;
        uniform mat4 u_modelview;
        uniform float u_scale;
        attribute vec4 a_position;
        attribute vec4 a_color;
        varying vec4 v_color;

        void main() {
            gl_Position = u_mvp * a_position;
            v_color = a_color;
            
            if (u_scale != 0.0) {
                vec4 cpos = u_modelview * a_position;
                float dist = length(cpos.xyz);
                gl_PointSize = %f * self.size / (dist * u_scale);
            }   
        }
    """% (0.01 * 100),
    GL.GL_FRAGMENT_SHADER : """
        #ifdef GL_ES
        precision mediump float;
        #endif

        varying vec4 v_color;
        void main() {
            gl_FragColor = v_color;
        }
    """
}

SHADER_CORE = {
    GL.GL_VERTEX_SHADER : """
        uniform mat4 u_mvp;
        in vec4 a_position;
        in vec4 a_color;
        out vec4 v_color;

        void main() {
            gl_Position = u_mvp * a_position;
            v_color = a_color;
        }
    """,
    GL.GL_FRAGMENT_SHADER : """
        #ifdef GL_ES
        precision mediump float;
        #endif

        in vec4 v_color;
        out vec4 fragColor;
        void main() {
            fragColor = v_color;
        }
    """
}