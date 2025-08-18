import importlib

from OpenGL import GL
from OpenGL.GL import shaders
import numpy as np
from pyqtgraph.Qt import QT_LIB
from PySide6 import QtWidgets, QtCore, QtGui

if QT_LIB in ["PyQt5", "PySide2"]:
    QtOpenGL = QtGui
else:
    QtOpenGL = importlib.import_module(f"{QT_LIB}.QtOpenGL")



from pyqtgraph.Qt import QtGui, QT_LIB

from .GL3DGraphicsItemMixin import GL3DGraphicsItemMixin
from .GL3DPlotDataItemMixin import GL3DFlatMeshPlotDataItemMixin, GL3DMeshPlotDataItemMixin

from pyqtgraph.opengl.GLGraphicsItem import GLGraphicsItem

from pyqtgraph.opengl.items.GLGraphItem import GLGraphItem
from pyqtgraph.opengl.items.GLGridItem import GLGridItem
from pyqtgraph.opengl.items.GLSurfacePlotItem import GLSurfacePlotItem
from pyqtgraph.opengl.items.GLBarGraphItem import GLBarGraphItem
from pyqtgraph.opengl.items.GLMeshItem import GLMeshItem
from pyqtgraph.opengl.items.GLLinePlotItem import GLLinePlotItem
from pyqtgraph.opengl.items.GLBoxItem import GLBoxItem
from pyqtgraph.opengl.items.GLVolumeItem import GLVolumeItem
from pyqtgraph.opengl.items.GLScatterPlotItem import GLScatterPlotItem
from pyqtgraph.opengl.items.GLTextItem import GLTextItem
from pyqtgraph.opengl.items.GLImageItem import GLImageItem
from pyqtgraph.opengl.items.GLAxisItem import GLAxisItem
from pyqtgraph.opengl.items.GLGradientLegendItem import GLGradientLegendItem
from pyqtgraph.opengl.MeshData import MeshData
import types



class GL3DMeshData(MeshData):
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
    
    def vertexNormals(self, indexed=None):
        if self._vertexNormals is None:
            faceNorms = self.faceNormals()
            self._vertexNormals = np.zeros((self._vertexes.shape[0], 3), dtype=np.float32)
            
            # Vectorized scattering of face normals to vertices
            for i in range(3):  # Process each vertex in the triangle
                np.add.at(self._vertexNormals, self._faces[:, i], faceNorms)
            
            # Vectorized normalization
            mag = np.linalg.norm(self._vertexNormals, axis=1)
            non_zero_mask = mag > 0
            self._vertexNormals[non_zero_mask] /= mag[non_zero_mask, np.newaxis]

        if indexed is None:
            return self._vertexNormals
        elif indexed == 'faces':
            return self._vertexNormals[self.faces()]
        else:
            raise Exception("Invalid indexing mode. Accepts: None, 'faces'")




class GL3DMeshItem(GL3DGraphicsItemMixin, GLMeshItem):
    def __init__(self, parentItem=None, **kwds):
        super().__init__(parentItem=parentItem, **kwds)

        
        
        glopts = kwds.pop('glOptions', 'opaque')
        self.setGLOptions(glopts)
        shader = kwds.pop('shader', None)
        self.setShader(shader)
        
        self.setMeshData(**kwds)
        
        ## storage for data compiled from MeshData object
        self.vertexes = None
        self.normals = None
        self.colors = None
        self.faces = None

        self.m_vbo_position = QtOpenGL.QOpenGLBuffer(QtOpenGL.QOpenGLBuffer.Type.VertexBuffer)
        self.m_vbo_normal = QtOpenGL.QOpenGLBuffer(QtOpenGL.QOpenGLBuffer.Type.VertexBuffer)
        self.m_vbo_color = QtOpenGL.QOpenGLBuffer(QtOpenGL.QOpenGLBuffer.Type.VertexBuffer)
        self.m_ibo_faces = QtOpenGL.QOpenGLBuffer(QtOpenGL.QOpenGLBuffer.Type.IndexBuffer)
        self.m_vbo_edgeVerts = QtOpenGL.QOpenGLBuffer(QtOpenGL.QOpenGLBuffer.Type.VertexBuffer)
        self.m_ibo_edges = QtOpenGL.QOpenGLBuffer(QtOpenGL.QOpenGLBuffer.Type.IndexBuffer)
    
    def _childPaint(self): GLMeshItem.paint()

    def _paintHelper(self): super()._paintHelper()

    def setMeshData(self, **kwds):
        md = kwds.get('meshdata', None)
        if md is None:
            opts = {}
            for k in ['vertexes', 'faces', 'edges', 'vertexColors', 'faceColors']:
                try:
                    opts[k] = kwds.pop(k)
                except KeyError:
                    pass
            md = GL3DMeshData(**opts)
        
        self.opts['meshdata'] = md
        self.opts.update(kwds)
        self.meshDataChanged()
        self.update()
    



class GL3DLinePlotDataItem(GL3DFlatMeshPlotDataItemMixin, GLLinePlotItem):
    _shaderProgram = None

    def __init__(self, parentItem=None, **kwds):
        """All keyword arguments are passed to setData()"""
        super().__init__(**kwds)
        glopts = kwds.pop('glOptions', 'additive')
        self.setGLOptions(glopts)
        self.pos = None
        self.mode = 'lines'
        self.width = 1.
        self.color = (1.0,1.0,1.0,1.0)
        self.antialias = False

        self.m_vbo_position = QtOpenGL.QOpenGLBuffer(QtOpenGL.QOpenGLBuffer.Type.VertexBuffer)
        self.m_vbo_color = QtOpenGL.QOpenGLBuffer(QtOpenGL.QOpenGLBuffer.Type.VertexBuffer)
        self.vbos_uploaded = False
        self.setParentItem(parentItem)
        self.setData(**kwds)

    @property
    def dataAttr(self):
        return self.pos

    def _childPaint(self):
        return GLLinePlotItem.paint(self)
    
    def _setDataChild(self, *args, **kwds):
        return GLLinePlotItem.setData(self, *args, **kwds)
    
    
class MixedGLLinePlotItem(GL3DGraphicsItemMixin, GLLinePlotItem):
    _shaderProgram = None

    def __init__(self, parentItem=None, **kwds):
        """All keyword arguments are passed to setData()"""
        super().__init__(**kwds)
        glopts = kwds.pop('glOptions', 'additive')
        self.setGLOptions(glopts)
        self.pos = None
        self.mode = 'line_strip'
        self.width = 1.
        self.color = (1.0,1.0,1.0,1.0)
        self.antialias = False

        self.m_vbo_position = QtOpenGL.QOpenGLBuffer(QtOpenGL.QOpenGLBuffer.Type.VertexBuffer)
        self.m_vbo_color = QtOpenGL.QOpenGLBuffer(QtOpenGL.QOpenGLBuffer.Type.VertexBuffer)
        self.vbos_uploaded = False
        self.setParentItem(parentItem)
        self.setData(**kwds)

    def _paintHelper(self):
        return super()._paintHelper()
    
    def _childPaint(self):
        return GLLinePlotItem.paint(self)

    
    def childrenBoundingRect(self):...
    
        
class MixedGLGraphItem(GL3DGraphicsItemMixin, GLGraphicsItem):
    def __init__(self, parentItem=None, **kwds):
        super().__init__(parentItem=parentItem)
        glopts = kwds.pop('glOptions', 'translucent')

        self.edges = None
        self.edgeColor = QtGui.QColor(QtCore.Qt.GlobalColor.white)
        self.edgeWidth = 1.0

        self.lineplot = GL3DLinePlotDataItem(parentItem=self, glOptions=glopts, mode='lines')
        self.scatter = GL3DLinePlotDataItem(parentItem=self, glOptions=glopts)
        self.setParentItem(parentItem)
        self.setData(**kwds)

class MixedGLGridItem(GL3DGraphicsItemMixin, GLGridItem):
    def __init__(self, size=None, color=(255, 255, 255, 76.5), antialias=True, glOptions='translucent', parentItem=None):
        super().__init__(parentItem=parentItem)

        self.lineplot = None    # mark that we are still initializing

        if size is None:
            size = QtGui.QVector3D(20,20,1)
        self.setSize(size=size)
        self.setSpacing(1, 1, 1)
        self.setColor(color)

        self.lineplot = GL3DLinePlotDataItem(parentItem=self, glOptions=glOptions, mode='lines', antialias=antialias)
        
        self.setParentItem(parentItem)
        self.updateLines()


def GL3DvertexNormals(self, indexed=None):
    if self._vertexNormals is None:
        faceNorms = self.faceNormals()
        self._vertexNormals = np.zeros((self._vertexes.shape[0], 3), dtype=np.float32)
        
        # Vectorized scattering of face normals to vertices
        for i in range(3):  # Process each vertex in the triangle
            np.add.at(self._vertexNormals, self._faces[:, i], faceNorms)
        
        # Vectorized normalization
        mag = np.linalg.norm(self._vertexNormals, axis=1)
        non_zero_mask = mag > 0
        self._vertexNormals[non_zero_mask] /= mag[non_zero_mask, np.newaxis]

    if indexed is None:
        return self._vertexNormals
    elif indexed == 'faces':
        return self._vertexNormals[self.faces()]
    else:
        raise Exception("Invalid indexing mode. Accepts: None, 'faces'")



    

class GL3DSurfacePlotItem(GL3DMeshPlotDataItemMixin, GLSurfacePlotItem):
    def __init__(self, x=None, y=None, z=None, colors=None, parentItem=None, **kwds):
        
        self._GL3DMeshData=None
        
        super().__init__(x=x, y=y, z=z, colors=colors, parentItem=parentItem, **kwds)
    
    @property
    def _meshdata(self):
        return self._GL3DMeshData
    
    @_meshdata.setter
    def _meshdata(self, value):
        
        if not hasattr(value, "GL3DOptimization"):
            value.vertexNormals = types.MethodType(GL3DvertexNormals, value)
            setattr(value, "GL3DOptimization", True)
        
        self._GL3DMeshData = value
    
    
    @property
    def dataAttr(self):
        return self._x, self._y, self._z

    def _childPaint(self):
        return GLSurfacePlotItem.paint(self)
    
    def _setDataChild(self, *args, **kwds):
        return GLSurfacePlotItem.setData(self, *args, **kwds)
    
    def setMeshData(self, **kwds):
        """
        Set mesh data for this item. This can be invoked two ways:
        
        1. Specify *meshdata* argument with a new MeshData object
        2. Specify keyword arguments to be passed to MeshData(..) to create a new instance.
        """
        md = kwds.get('meshdata', None)
        if md is None:
            opts = {}
            for k in ['vertexes', 'faces', 'edges', 'vertexColors', 'faceColors']:
                try:
                    opts[k] = kwds.pop(k)
                except KeyError:
                    pass
            md = MeshData(**opts)
        
        if not hasattr(md, "GL3DOptimization"):
            md.vertexNormals = types.MethodType(GL3DvertexNormals, md)
            setattr(md, "GL3DOptimization", True)
        
        self.opts['meshdata'] = md
        self.opts.update(kwds)
        self.meshDataChanged()
        self.update()
        
    

        
        
class MixedGLBarGraphItem(GL3DGraphicsItemMixin, GLBarGraphItem):
    def __init__(self, pos, size, parentItem=None):
        super().__init__(pos, size, parentItem=parentItem)


class MixedGLBoxItem(GL3DGraphicsItemMixin, GLBoxItem):
    def __init__(self, size=None, color=None, glOptions='translucent', parentItem=None):
        super().__init__(size=size, color=color, glOptions=glOptions, parentItem=parentItem)

        self.lineplot = None 

        if size is None:
            size = QtGui.QVector3D(1,1,1)
        self.setSize(size=size)
        if color is None:
            color = (255,255,255,80)
        self.setColor(color)

        self.lineplot = GL3DLinePlotDataItem(parentItem=self, glOptions=glOptions, mode='lines')
        self.setParentItem(parentItem)
        self.updateLines()

class MixedGLVolumeItem(GLVolumeItem):
    _shaderProgram = None
    
    def __init__(self, data, sliceDensity=1, smooth=True, glOptions='translucent', parentItem=None):
        super().__init__(data, sliceDensity=sliceDensity, smooth=smooth, glOptions=glOptions, parentItem=parentItem)


class GL3DScatterPlotItem(GL3DFlatMeshPlotDataItemMixin, GLScatterPlotItem):
    def __init__(self, parentItem=None, **kwds):
        super().__init__(parentItem=parentItem, **kwds)
        
    @property
    def dataAttr(self):
        return self.pos

    def _childPaint(self):
        return GLScatterPlotItem.paint(self)
    
    def _setDataChild(self, *args, **kwds):
        return GLScatterPlotItem.setData(self, *args, **kwds)


class MixedGL3DTextItem(GL3DGraphicsItemMixin, GLTextItem):
    def __init__(self, parentItem=None, **kwds):
        super().__init__(parentItem=parentItem, **kwds)
        
    def _childPaint(self):return GL3DGraphicsItemMixin.paint(self)


class MixedGLImageItem(GL3DGraphicsItemMixin, GLImageItem):
    def __init__(self, data, smooth=False, glOptions='translucent', parentItem=None):
        super().__init__(data, smooth=smooth, glOptions=glOptions, parentItem=parentItem)


class MixedGLAxisItem(GL3DGraphicsItemMixin, GLAxisItem):
    def __init__(self, size=None, antialias=True, glOptions='translucent', parentItem=None):
        super().__init__(size=size, antialias=antialias, glOptions=glOptions, parentItem=parentItem)
        self.lineplot = None    # mark that we are still initializing

        if size is None:
            size = QtGui.QVector3D(1,1,1)
        self.setSize(size=size)

        self.lineplot = GL3DLinePlotDataItem(parentItem=self, glOptions=glOptions, mode='lines', antialias=antialias)
        self.setParentItem(parentItem)
        self.updateLines()

class MixedGLGradientLegendItem(GL3DGraphicsItemMixin, GLGradientLegendItem):
    def __init__(self, parentItem=None, **kwds):
        super().__init__(parentItem=parentItem, **kwds)