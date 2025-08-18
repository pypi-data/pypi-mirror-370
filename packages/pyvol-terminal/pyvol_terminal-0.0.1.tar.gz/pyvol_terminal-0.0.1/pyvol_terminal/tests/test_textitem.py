import numpy as np
import pyqtgraph as pg
import pyqtgraph.opengl as gl
from OpenGL import GL
from PySide6 import QtWidgets, QtGui, QtCore
import sys


def create_text_texture_atlas(texts, font_size=32):
    # Create a single QImage with all texts side by side
    font = QtGui.QFont("Arial", font_size)
    metrics = QtGui.QFontMetrics(font)

    paddings = 10
    widths = [metrics.horizontalAdvance(t) + paddings for t in texts]
    heights = [metrics.height() + paddings for _ in texts]
    total_width = sum(widths)
    max_height = max(heights)

    image = QtGui.QImage(total_width, max_height, QtGui.QImage.Format_RGBA8888)
    image.fill(QtCore.Qt.transparent)

    painter = QtGui.QPainter(image)
    painter.setFont(font)
    painter.setPen(QtGui.QColor(255, 255, 255))

    positions = []
    x_offset = 0
    for text, w in zip(texts, widths):
        painter.drawText(x_offset, metrics.ascent() + paddings // 2, text)
        positions.append((x_offset, w))
        x_offset += w
    painter.end()

    return image, positions, total_width, max_height


def build_label_mesh(text_positions, atlas_width, atlas_height, xyz_positions):
    # Create quads for each text label, mapped to texture atlas
    verts = []
    faces = []
    texcoords = []
    face_idx = 0

    for i, ((x_offset, width), pos) in enumerate(zip(text_positions, xyz_positions)):
        w_norm = width / atlas_width
        h_norm = 1.0

        u0 = x_offset / atlas_width
        u1 = (x_offset + width) / atlas_width
        v0 = 0.0
        v1 = 1.0

        size = 0.5  # physical size in 3D

        # Define quad in 3D (XY plane)
        verts.extend([
            pos + [0, 0, 0],
            pos + [size, 0, 0],
            pos + [size, size * 0.5, 0],
            pos + [0, size * 0.5, 0],
        ])
        faces.append([face_idx, face_idx+1, face_idx+2])
        faces.append([face_idx, face_idx+2, face_idx+3])
        texcoords.extend([
            [u0, v1],
            [u1, v1],
            [u1, v0],
            [u0, v0],
        ])
        face_idx += 4

    return np.array(verts), np.array(faces), np.array(texcoords)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.widget = gl.GLViewWidget()
        self.setCentralWidget(self.widget)
        self.widget.opts['distance'] = 10

        texts = ["AAPL", "GOOG", "SPY"]
        positions = [np.array([-2, 0, 0]), np.array([0, 0, 0]), np.array([2, 0, 0])]

        image, atlas_positions, w, h = create_text_texture_atlas(texts)
        verts, faces, texcoords = build_label_mesh(atlas_positions, w, h, positions)

        mesh_item = gl.GLMeshItem(vertexes=verts, faces=faces, smooth=False, drawEdges=False)
        mesh_item.shader()['texCoords'] = texcoords

        # Convert QImage to OpenGL texture
        image = image.convertToFormat(QtGui.QImage.Format_RGBA8888)
        ptr = image.bits()
        data = np.array(ptr).reshape((image.height(), image.width(), 4))
        tex = GL.GLTexture2D(data)
        mesh_item.setGLOptions('additive')
        mesh_item.texture = tex
        mesh_item.texcoords = texcoords
        mesh_item.glOptions = 'additive'

        # Monkey patch paint method to bind texture
        def paint_with_texture(self):
            self.texture.bind()
            gl.GLMeshItem.paint(self)

        mesh_item.paint = paint_with_texture.__get__(mesh_item, gl.GLMeshItem)

        self.widget.addItem(mesh_item)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
