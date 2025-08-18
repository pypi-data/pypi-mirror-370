import numpy as np
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
from pyqtgraph import Transform3D
from pyqtgraph.opengl import GLLinePlotItem, GLViewWidget, GLTextItem
from pyqtgraph import SRTTransform3D

# Create parent lines (4 parallel lines)
# Create parent lines (4 parallel lines)
line_length = 1
y_offsets = np.linspace(-1, 1, 4)  # 4 horizontal lines

lines = []
for y in y_offsets:
    lines.append([0, y, 0])   # start point
    lines.append([1, y, 0])   # end point

parent_positions = np.array(lines)  # shape: (8, 3)


app = QtWidgets.QApplication([])
view = GLViewWidget()
view.show()

# Parent lines (white)
parent_lines = GLLinePlotItem(
    pos=parent_positions,
    color="white",
    width=2,
    mode='lines',
    antialias=True
)
view.addItem(parent_lines)

# Child lines (red, starts same as parent)

child_positions = parent_positions.copy()

#child_positions[:,0]/=5
child_lines = GLLinePlotItem(
    pos=child_positions,
    color="cyan",
    width=2,
    mode='lines',
    antialias=True
)
view.addItem(child_lines)

# Parent transform (rotate over time)
parent_transform = SRTTransform3D()
parent_lines.setTransform(parent_transform)

print(parent_lines.transform())
#parent_transform.rotate(30, (0, 0, 1))  # Initial rotation
print(child_lines.pos)
# Child transform (offset + scale)
child_transform = SRTTransform3D()
child_lines.setTransform(child_transform)
#child_lines.translate(-1.5, 0, 0, local=True) 
child_lines.translate(-1.5, 0, 0, local=False) 


child_transform.update()
#child_lines.setData(pos=child_lines.mapToParent(parent_lines.pos.T).T)

#child_transform.scale(0.5, 0.5, 0.5)  # Scale down

pos = np.array([0, 0, 0])
colors=["white", "yellow", "cyan"]
for k in range(3):
    
    pos = np.zeros(3)
    pos[k] = 1 

    
    for i in range(21):
        if i % 2 == 0:
            gl_item = GLTextItem(pos=pos * i / 10, text=f"{i}", color=colors[k])
            view.addItem(gl_item), #ignoreBounds=True)
        pos = np.zeros(3)
        pos[k] = 1 
        



def update():

    # Rotate parent
    parent_lines.transform().translate(0.5, 0, 0)
    parent_lines.setData(pos=parent_lines.transform().map(parent_positions.T).T)
    
    # Apply parent + child transforms to child
    #combined_transform = SRTTransform3D(parent_transform)
    #combined_transform.translate(*child_transform.getTranslation())
    #combined_transform.scale(*child_transform.getScale())
    
    
    #combined_transform = Transform3D(parent_lines.transform())
   # combined_transform * child_lines.transform()
    child_lines.transform().translate(0.5, 0, 0)
    transformed_child_positions = child_lines.mapToParent(child_positions.T ).T
    child_lines.setData(pos=transformed_child_positions)
# Animation timer
timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(500)

if __name__ == '__main__':
    QtWidgets.QApplication.instance().exec()