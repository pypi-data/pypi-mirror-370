import numpy as np
import pyqtgraph as pg
import pyqtgraph.opengl as gl
from PySide6.QtWidgets import QApplication
import sys

def main():
    pg.setConfigOptions(antialias=True)
    app = QApplication(sys.argv)

    view = gl.GLViewWidget()
    view.setWindowTitle('Manual 3D Graph with PySide6')
    view.setGeometry(100, 100, 800, 600)
    view.show()

    # Node positions
    num_nodes = 10
    pos = np.random.rand(num_nodes, 3) * 10

    # Adjacency list (edges)
    edges = np.array([
        [0, 1], [1, 2], [2, 3], [3, 4], [4, 0],
        [5, 6], [6, 7], [7, 8], [8, 9], [9, 5]
    ])

    # Plot nodes
    colors = np.ones((num_nodes, 4), dtype=float)
    colors[:, 0] = np.linspace(0.2, 1, num_nodes)
    sizes = np.linspace(5, 15, num_nodes)

    scatter = gl.GLScatterPlotItem(pos=pos, color=colors, size=sizes, pxMode=True)
    view.addItem(scatter)

    # Plot edges
    for edge in edges:
        p1 = pos[edge[0]]
        p2 = pos[edge[1]]
        pts = np.array([p1, p2])
        line = gl.GLLinePlotItem(pos=pts, color=(1, 1, 1, 0.6), width=1, antialias=True)
        view.addItem(line)

    # Add grid
    grid = gl.GLGridItem()
    grid.scale(2, 2, 1)
    view.addItem(grid)

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
