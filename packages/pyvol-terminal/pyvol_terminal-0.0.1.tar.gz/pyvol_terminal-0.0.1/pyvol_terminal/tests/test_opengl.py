import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6 import QtOpenGLWidgets
from PySide6.QtCore import Qt
from OpenGL import GL


class DotItem:
    def __init__(self, *coordinate):
        
        self.coordinate=list(coordinate)
    
    def paint(self):
        GL.glColor3f(1.0, 1.0, 1.0)
        
        GL.glBegin(GL.GL_POINTS)
        print(f"self.coordinate: {self.coordinate}")
        GL.glVertex2f(*(self.coordinate))  
        GL.glEnd()



class OpenGLWidget(QtOpenGLWidgets.QOpenGLWidget):
    def __init__(self, items):
        self.items=items
        super().__init__()

    def initializeGL(self):
        GL.glClearColor(0.1, 0.1, 0.1, 1.0)  # Dark gray background
        GL.glPointSize(10)  # Set point size to 10 pixels

    def paintGL(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        
        # Set up orthographic projection (pixel coordinates)
        width, height = self.width(), self.height()
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(0, width, height, 0, -1, 1)  # (left, right, bottom, top, near, far)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()
        
        for item in self.items:
            item.paint()
            
    def resizeGL(self, width, height):
        GL.glViewport(0, 0, width, height)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("OpenGL Point Example")
        self.setGeometry(100, 100, 800, 600)
        
        dots = [
            DotItem(100, 100),  # Top-left
            DotItem(400, 300),  # Center
            DotItem(700, 500),   # Bottom-right
        ]
           #     dots = [DotItem((0.1 * i, 0.0)) for i in range(-5, 5)]
        
        self.opengl_widget = OpenGLWidget(dots)
        self.setCentralWidget(self.opengl_widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())