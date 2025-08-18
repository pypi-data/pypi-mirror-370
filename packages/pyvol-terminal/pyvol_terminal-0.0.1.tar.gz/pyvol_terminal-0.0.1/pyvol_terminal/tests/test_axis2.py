from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
import pyqtgraph.opengl as gl
import pyqtgraph as pg
import OpenGL.GL as ogl
import numpy as np
import sys

class CustomTextItem(gl.GLGraphicsItem.GLGraphicsItem):
    def __init__(self, X, Y, Z, text):
        self.color = QtCore.Qt.GlobalColor.white
        gl.GLGraphicsItem.GLGraphicsItem.__init__(self)
        self.text = text
        self.X = X
        self.Y = Y
        self.Z = Z
        self.color = QtCore.Qt.GlobalColor.white
        self.font = QtGui.QFont('Helvetica', 16)

        self._setPos()
    
    def _setPos(self):
        self.pos=(self.X, self.Y, self.Z)

    def setGLViewWidget(self, GLViewWidget):
        self.GLViewWidget = GLViewWidget

    def setText(self, text):
        self.text = text
        self.update()

    def setX(self, X):
        self.X = X
        self._setPos()
        self.update()

    def setY(self, Y):
        self.Y = Y
        self._setPos()
        self.update()

    def setZ(self, Z):
        self.Z = Z
        self._setPos()
        self.update()

    def paint(self):
      #  self.GLViewWidget.qglColor(QtCore.Qt.black)
        if len(self.text) < 1:
            return
        self.setupGLState()

        project = self.compute_projection()
        vec3 = QtGui.QVector3D(*self.pos)
        text_pos = project.map(vec3).toPointF()

        painter = QtGui.QPainter(self.view())
        painter.setPen(self.color)
        painter.setFont(self.font)
        painter.setRenderHints(QtGui.QPainter.RenderHint.Antialiasing | QtGui.QPainter.RenderHint.TextAntialiasing)
        painter.drawText(text_pos, self.text)
        painter.end()
        
    def compute_projection(self):
        # note that QRectF.bottom() != QRect.bottom()
        rect = QtCore.QRectF(self.view().rect())
        ndc_to_viewport = QtGui.QMatrix4x4()
        ndc_to_viewport.viewport(rect.left(), rect.bottom(), rect.width(), -rect.height())
        return ndc_to_viewport * self.mvpMatrix()

class Custom3DAxis(gl.GLAxisItem):
    """Class defined to extend 'gl.GLAxisItem'."""
    def __init__(self, parent, color=(0,0,0,.6)):
        self.antialias=False
        gl.GLAxisItem.__init__(self)
        self.parent = parent
        self.color = color
        

    def add_labels(self):
        """Adds axes labels."""
        x,y,z = self.size()
        #X label
        self.xLabel = CustomTextItem(X=x/2, Y=-y/20, Z=-z/20, text="X")
        self.xLabel.setGLViewWidget(self.parent)
        self.parent.addItem(self.xLabel)
        #Y label
        self.yLabel = CustomTextItem(X=-x/20, Y=y/2, Z=-z/20, text="Y")
        self.yLabel.setGLViewWidget(self.parent)
        self.parent.addItem(self.yLabel)
        #Z label
        self.zLabel = CustomTextItem(X=-x/20, Y=-y/20, Z=z/2, text="Z")
        self.zLabel.setGLViewWidget(self.parent)
        self.parent.addItem(self.zLabel)

    def add_tick_values(self, xticks=[], yticks=[], zticks=[]):
        """Adds ticks values."""
        x,y,z = self.size()
        xtpos = np.linspace(0, x, len(xticks))
        ytpos = np.linspace(0, y, len(yticks))
        ztpos = np.linspace(0, z, len(zticks))
        #X label
        for i, xt in enumerate(xticks):
            val = CustomTextItem(X=xtpos[i], Y=-y/20, Z=-z/20, text=str(xt))
            val.setGLViewWidget(self.parent)
            self.parent.addItem(val)
        #Y label
        for i, yt in enumerate(yticks):
            val = CustomTextItem(X=-x/20, Y=ytpos[i], Z=-z/20, text=str(yt))
            val.setGLViewWidget(self.parent)
            self.parent.addItem(val)
        #Z label
        for i, zt in enumerate(zticks):
            val = CustomTextItem(X=-x/20, Y=-y/20, Z=ztpos[i], text=str(zt))
            val.setGLViewWidget(self.parent)
            self.parent.addItem(val)

    def paint(self):
        self.setupGLState()
        if self.antialias:
            ogl.glEnable(ogl.GL_LINE_SMOOTH)
            ogl.glHint(ogl.GL_LINE_SMOOTH_HINT, ogl.GL_NICEST)
        ogl.glBegin(ogl.GL_LINES)

        x,y,z = self.size()
        #Draw Z
        ogl.glColor4f(*self.color)
        ogl.glVertex3f(0, 0, 0)
        ogl.glVertex3f(0, 0, z)
        #Draw Y
        ogl.glColor4f(*self.color)
        ogl.glVertex3f(0, 0, 0)
        ogl.glVertex3f(0, y, 0)
        #Draw X
        ogl.glColor4f(*self.color)
        ogl.glVertex3f(0, 0, 0)
        ogl.glVertex3f(x, 0, 0)
        ogl.glEnd()

def main():
    app = QtWidgets.QApplication(sys.argv)
    fig1 = gl.GLViewWidget()
    n = 51
    y = np.linspace(-10,10,n)
    x = np.linspace(-10,10,100)
    for i in range(n):
        yi = np.array([y[i]]*100)
        d = (x**2 + yi**2)**0.5
        z = 10 * np.cos(d) / (d+1)
        pts = np.vstack([x,yi,z]).transpose()
        plt = gl.GLLinePlotItem(pos=pts, color=pg.glColor((i,n*1.3)), width=(i+1)/10., antialias=True)
        fig1.addItem(plt)


    axis = Custom3DAxis(fig1, color=(0.2,0.2,0.2,.6))
    axis.setSize(x=12, y=12, z=12)
    # Add axes labels
    axis.add_labels()
    # Add axes tick values
    axis.add_tick_values(xticks=[0,4,8,12], yticks=[0,6,12], zticks=[0,3,6,9,12])
    fig1.addItem(axis)
    fig1.opts['distance'] = 40

    fig1.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()