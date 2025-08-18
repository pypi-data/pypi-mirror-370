import sys
import numpy as np
from PySide6 import QtCore, QtGui
from PySide6.QtWidgets import QApplication
import pyqtgraph.opengl as gl
from pyvol_terminal.interfaces.volatility_surface.normalised_glviewwidget import NormaliseGLViewWidget
from pyvol_terminal.interfaces.volatility_surface import view_box
from pyvol_terminal.interfaces.volatility_surface.axis_3D_items import AxisItem3D
from pyvol_terminal.interfaces.volatility_surface.gl_plotitems import glScatter, glSurface
from pyvol_terminal import misc_widgets
class Counter:
    c=0


def main():
    app = QApplication(sys.argv)

    padding = {ax : 0 for ax in "xyz"}
    w = NormaliseGLViewWidget(padding=padding)
    labels = "XYZ"
    
    axis_items = {axis : AxisItem3D(axis, label, 6, "red", font=QtGui.QFont('Arial', 10)) for axis, label in zip("xyz", labels)}
    w.setAxisItems(axis_items)
    w.setWindowTitle("NormaliseGLViewWidget Test")
    w.opts['azimuth'] = -50
    w.opts["distance"] = 4
    w.opts['center'] = QtGui.QVector3D(0, 1, 0)  


    x = 5 * np.linspace(-2, 2, 25)
    y = 5 * np.linspace(-2, 2, 25)
    x_grid, y_grid = np.meshgrid(x, y)
    r = np.sqrt(x_grid ** 2 + y_grid ** 2) + 1e-6
    z_grid = 3 * np.sin(r) / r
    
    color=(1, 0, 0, 1)
    colormap=misc_widgets.CustomColorMap("virdis")
    
    surface_item = glSurface(x=x, y=y, z=z_grid, price_type="mid", color=color, colormap=colormap)
    surface_item.item_type="surface"
    w.addItem(surface_item, viewBoxAdd=True)
    
    print(f"\nsurface")
    print(f"x: {(surface_item._x.min(), surface_item._x.max())}")
    print(f"y: {(surface_item._y.min(), surface_item._y.max())}")
    print(f"z: {(surface_item._z.min(), surface_item._z.max())}")
    
    
    
    
    scatter_points = np.column_stack((x_grid.flatten(), y_grid.flatten(), z_grid.flatten()))

    scatter_item = glScatter(pos=scatter_points, price_type="mid", color=color)
    scatter_item.item_type="scatter"
    w.addItem(scatter_item, viewBoxAdd=True)

    
    #x_min = np.min((scatter_item.unnorm_pos[:,0].min(), surface_item.unnorm_x.min()))
    #x_max = np.max((scatter_item.unnorm_pos[:,0].max(), surface_item.unnorm_x.max()))

        
    
    for i in range(1, 11):
        pos=(i /10, 0, 0)
        text_item = gl.GLTextItem(pos=pos, text=f"{i+1}", color="white")
        text_item.type="axis"
        w.addItem(text_item, viewBoxAdd=False)
    for i in range(1,11):
        pos=(0, i/10, 0)
        text_item = gl.GLTextItem(pos=pos, text=f"{i+1}", color="yellow")
        text_item.type="axis"
        w.addItem(text_item, viewBoxAdd=False)
    for i in range(1,11):
        pos=(0, 0, i/10)
        text_item = gl.GLTextItem(pos=pos, text=f"{i+1}", color="cyan")
        text_item.type="axis"
        w.addItem(text_item, viewBoxAdd=False)  
    

    counter = Counter()
    
    
    def update_data():
        Counter.c+=1
        print("")
        x = surface_item.unnorm_x + Counter.c
        y = surface_item.unnorm_y + Counter.c
        z = surface_item.unnorm_z + Counter.c
        print("\nupdate_data")
        surface_item.setData(x=x, y=y, z=z)
        pos=scatter_item.unnorm_pos + Counter.c
        scatter_item.setData(pos=pos)
        
        #update_text("x", surface_item)
        #update_text("y", surface_item)
        #update_text("z", surface_item)
#        if Counter.c > 3:
#            sys.exit()
        
        
        
        
    timer = QtCore.QTimer()
    timer.timeout.connect(update_data)
    timer.start(2000)
    
    w.show()
    w.update()

    # Start the event loop
    sys.exit(app.exec())




if __name__ == "__main__":
    main()
