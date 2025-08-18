from PySide6 import QtWidgets, QtGui
import numpy as np, sys
from pyqtgraph.opengl import GLLinePlotItem, GLViewWidget, GLTextItem
from pyqtgraph.opengl.GLGraphicsItem import GLGraphicsItem
from pyqtgraph import Vector

class BlockUpdateGLLinePlot(GLLinePlotItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)   

class NestedLineItem(GLLinePlotItem):
    def __init__(self, *args, **kwargs):
        self._otherNests=[]
        self._lineItems=[]
        self.blockUpdates=False
        self.blockPaint=False
        super().__init__(*args, **kwargs)   

    def addNest(self, nestedLineItem):
        self._otherNests.append(nestedLineItem)

    def addLineItem(self, lineItem):
        self._lineItems.append(lineItem)

    def _extract(self, combined_pos):
        T = (self.parentItem().transform() * self.transform()).inverted()[0]
        for nestedLineItem in self._otherNests:
            for lineItem in nestedLineItem._lineItems:
                pos = [T.map(QtGui.QVector3D(p[0], p[1], p[2])) for p in lineItem.pos]
                
                pos = [nestedLineItem.parentItem().transform().map(QtGui.QVector3D(p.x(), p.y(), p.z())) for p in pos]
                pos = [nestedLineItem.transform().map(QtGui.QVector3D(p.x(), p.y(), p.z())) for p in pos]
                pos = np.array([[p.x(), p.y(), p.z()] for p in pos])
                
                pos = self._mapLineItem(pos, lineItem.transform())
                combined_pos = pos if combined_pos is None else np.vstack((combined_pos, pos))
                
            self.last_child2pos = pos[-1]
        return combined_pos

    def paint(self):
        if not self.blockPaint:
            combined_pos = None
            for lineItem in self._lineItems:
                pos = self._mapLineItem(lineItem.pos.copy(), lineItem.transform())
                combined_pos = pos if combined_pos is None else np.vstack((combined_pos, pos))
            
            combined_pos = self._extract(combined_pos)

            self.blockUpdates=True
            self.setData(pos=combined_pos)
            self.blockUpdates=True
            super().paint()

    def _mapLineItem(self, pos, tr):        
        if not tr.isIdentity():
            points_h = np.hstack([pos, np.ones((pos.shape[0], 1))])
            tr_matrix = np.array(tr.data()).reshape(4, 4).T
            transformed_h = points_h @ tr_matrix.T
            pos = transformed_h[:, :3] / transformed_h[:, 3:4]  
        return pos
    
    def update(self):
        if not self.blockUpdates:
            super().update()    
    
class Window(QtWidgets.QMainWindow):
    def __init__(self, *args, app=None, **kwargs):
        super().__init__(*args, **kwargs)   
        self.gl_widget = GLViewWidget()
        self.setCentralWidget(self.gl_widget)
        
        self.gP1, self.gP2, self.gP22 = GLGraphicsItem(), GLGraphicsItem(), GLGraphicsItem()        
    #    self.gP1.translate(1, 1, 1), self.gP2.translate(1, 3, -1), self.gP22.translate(1, 3, -1)
       # self.gP2.scale(-1, 1, -1)
        #self.gP22.scale(-1, 1, -1)


        self.nestPar1, self.nestPar2, self.nestPar22 = NestedLineItem(color="red", mode="lines"), NestedLineItem(color="yellow", mode="lines"), NestedLineItem(color="orange", mode="lines")
        self.nestPar1.translate(0.2, 1, 1), self.nestPar2.translate(-0.2, 5, 0.2), self.nestPar22.translate(-0.2, 5, 0.2)
        
        self.nestPar2.scale(-1, 1, -1), self.nestPar22.scale(-1, 1, -1)
        
        self.nestPar1.setParentItem(self.gP1), self.nestPar2.setParentItem(self.gP2), self.nestPar22.setParentItem(self.gP22)
        
        lineLength = 1
        
        for z in np.linspace(0, 5, 6):
            pos1 = [[0, 0, z], [lineLength, 0, z]]
            pos2 = [[0, 1, z ], [lineLength, 1, z]]  
            pos22 = [[0, 1, z+0.1], [lineLength, 1,  z+0.1]] # small offset
            l1, l2, l22 = GLLinePlotItem(pos=pos1, mode="lines"), GLLinePlotItem(pos=pos2, mode="lines"), GLLinePlotItem(pos=pos22, mode="lines")
            
            translation = -0.5, -1, 0.5
          #  l2.scale(-1, 1, -1), l22.scale(-1, 1, -1)
         #   l1.translate(*translation, True), l2.translate(*translation, True), l22.translate(*translation, True)
            self.nestPar1.addLineItem(l1), self.nestPar2.addLineItem(l2), self.nestPar22.addLineItem(l22)
        
        self.nestPar2.blockPaint=True
        self.nestPar1.addNest(self.nestPar2)
        
        self.gl_widget.addItem(self.gP1)
        self.gl_widget.addItem(self.gP22)
        
        self.showMaximized()
        self.nestPar1.paint()
        
        text2 = GLTextItem(pos=self.nestPar1.last_child2pos, text="mapping of child2 (incorrect)", font=QtGui.QFont("Arial", 6))
        text2.setTransform(self.nestPar1.transform())
        text2.setParentItem(self.gP1)
        
        text22 = GLTextItem(pos=pos22[-1], text="Child2 should be here", font=QtGui.QFont("Arial", 6))
        text22.translate(*translation, True)
        text22.setParentItem(self.gP22)
        
        
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = Window()
    sys.exit(app.exec())