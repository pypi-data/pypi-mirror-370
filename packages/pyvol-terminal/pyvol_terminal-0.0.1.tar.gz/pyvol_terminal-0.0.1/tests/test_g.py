from pyqtgraph.opengl.GLGraphicsItem import GLGraphicsItem
from pyqtgraph.opengl import GLLinePlotItem
import sys


from pyqtgraph import Transform3D

import numpy as np
from pyqtgraph.opengl import GLViewWidget

from PySide6 import QtCore, QtGui, QtWidgets
import numpy as np
from pyqtgraph.opengl import GLLinePlotItem, GLGraphicsItem
from pyqtgraph import Transform3D

class TransformedLineGroup(GLGraphicsItem):
    def __init__(self):
        super().__init__()
        self.lines = []  # Stores (vertices, color, transform)
        self.line_item = GLLinePlotItem()  # Single renderable item

    def addLine(self, vertices, color, transform=None):
        """Add a line with optional transform."""
        if transform is None:
            transform = Transform3D()  # Identity if no transform given
        self.lines.append((vertices, color, transform))
        self.updateLineData()  # Rebuild merged data

    def updateLineData(self):
        """Combine all lines into a single vertex array."""
        if not self.lines:
            return

        # Apply transforms and concatenate vertices
        all_vertices = []
        all_colors = []
        for vertices, color, transform in self.lines:
            # Apply transform to each vertex
            transformed_vertices = np.array([transform.map(v) for v in vertices])
            all_vertices.append(transformed_vertices)
            # Repeat color for each vertex
            all_colors.append(np.tile(color, (len(vertices), 1)))

        # Concatenate into single array
        merged_vertices = np.vstack(all_vertices)
        merged_colors = np.vstack(all_colors)

        # Update the line plot item
        self.line_item.setData(pos=merged_vertices, color=merged_colors)

    def paint(self):
        """Render all lines in one call."""
        self.line_item.paint()

class Window(QtWidgets.QMainWindow):
    def __init__(self, *args, app=None, **kwargs):
        super().__init__(*args, **kwargs)   

def main():
    
    app = QtWidgets.QApplication(sys.argv)
    win = Window()
    win.timer.start(500)
    sys.exit(app.exec())

if __name__ == "__main__":
    main()