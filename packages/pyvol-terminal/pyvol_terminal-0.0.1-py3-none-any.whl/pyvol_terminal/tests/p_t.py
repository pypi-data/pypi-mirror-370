from PySide6 import QtWidgets, QtGui
import numpy as np, sys
from pyqtgraph.opengl import GLLinePlotItem, GLViewWidget, GLTextItem
from pyqtgraph.opengl.GLGraphicsItem import GLGraphicsItem

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
        
    def paint(self):
        if not self.blockPaint:
            combined_pos = None
            for lineItem in self._lineItems:
                pos = self._mapLineItem(lineItem.pos.copy(), lineItem.transform())
                combined_pos = pos if combined_pos is None else np.vstack((combined_pos, pos))
            
            for nestedLineItem in self._otherNests:
                for lineItem in nestedLineItem._lineItems:
                    pos = self._mapLineItem(lineItem.pos.copy(), lineItem.transform())
                    combined_pos = pos if combined_pos is None else np.vstack((combined_pos, pos))
            
                self.last_child2pos = pos[-1] # last position of the child2 GLLinePlotItem's
            
            self.blockUpdates=True
            self.setData(pos=combined_pos)
            self.blockUpdates=True
            super().paint()

    def _mapLineItem(self, pos, tr):        
        if not tr.isIdentity():
            points_h = np.hstack([pos, np.ones((pos.shape[0], 1))])
            tr_matrix = np.array(tr.data()).reshape(4, 4).T
            transformed_h = points_h @ tr_matrix.T
            pos = transformed_h[:, :3]
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
        #self.gP1.translate(0, 1, 1), self.gP2.translate(1, 0, -1), self.gP22.translate(1, 0, -1)

        self.nestPar1, self.nestPar2, self.nestPar22 = NestedLineItem(color="red", mode="lines"), NestedLineItem(color="yellow", mode="lines"), NestedLineItem(color="orange", mode="lines")
        #self.nestPar1.translate(0.2, 1, 1), self.nestPar2.translate(-0.2, 0, 0.2), self.nestPar22.translate(-0.2, 0, 0.2)
        
        self.nestPar1.setParentItem(self.gP1), self.nestPar2.setParentItem(self.gP2), self.nestPar22.setParentItem(self.gP22)
        self.nestPar1.translate(1, 1, 1)
        lineLength = 1
        
        for z in np.linspace(0, 10, 11):
            z /=10
            
            pos1 = [[1, 1, z], [1+lineLength, 1, z]]
            pos2 = [[1, 1, z + 0.03 ], [1+lineLength, 1, z + 0.03]]  
            
            pos22 = [[0, 1, z + 0.03], [lineLength, 1, z + 0.03]] # small offset
            l1, l2, l22 = GLLinePlotItem(pos=pos1, mode="lines", color="red"), GLLinePlotItem(pos=pos2, mode="lines"), GLLinePlotItem(pos=pos22, mode="lines")
            
            
            
            translation = -0.5, -1, 0
            
            l1.setParentItem(self.nestPar1)
            l2.setParentItem(l1)
            
            
          #  l1.translate(*translation, True), l2.translate(*translation, True), l22.translate(*translation, True)
     #       self.nestPar1.addLineItem(l1), self.nestPar2.addLineItem(l2), self.nestPar22.addLineItem(l22)
        
        self.nestPar2.blockPaint=True
      #  self.nestPar1.addNest(self.nestPar2)
        
        self.gl_widget.addItem(self.gP1)
     #   self.gl_widget.addItem(self.gP22)
        
        self.showMaximized()
        self.nestPar1.paint()
        
        for i in range(1, 11):
            txt = GLTextItem(pos=(i / 10, 0, 0), text=str(i))
            self.gl_widget.addItem(txt)
            txt = GLTextItem(pos=(0, i / 10, 0), text=str(i))
            self.gl_widget.addItem(txt)
            txt = GLTextItem(pos=( 0, 0, i / 10), text=str(i))
            self.gl_widget.addItem(txt)

        
        
    #    text2 = GLTextItem(pos=self.nestPar1.last_child2pos, text="mapping of child2 (incorrect)", font=QtGui.QFont("Arial", 6))
     #   text2.setTransform(self.nestPar1.transform())
     #   text2.setParentItem(self.gP1)
        
        text22 = GLTextItem(pos=pos22[-1], text="Child2 should be here", font=QtGui.QFont("Arial", 6))
        text22.translate(*translation, True)
      #  text22.setParentItem(self.gP22)
        
        
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = Window()
    sys.exit(app.exec())