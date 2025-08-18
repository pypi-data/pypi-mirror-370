#%%
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets, isQObjectAlive

from pyvol_terminal.gl_3D_graphing import meta

class AbstractGLGraphicsItem(QtCore.QObject, metaclass=meta.QABCMeta):
    _nextId = 0
    def __init__(self, parentItem: 'AbstractGLGraphicsItem' = None, **kwargs):
        super().__init__()
        self._id = AbstractGLGraphicsItem._nextId
        AbstractGLGraphicsItem._nextId += 1
        self.__blockUpdates: bool=False
        self.blockUpdates(False)
        
    def blockUpdates(self, flag):
        print(f"\nblockUpdates: {flag}")
        self.__blockUpdates=flag
        
        
    def updateBlocked(self):
        return self.__blockUpdates

    def AnotherFunc(self):
        print(f"AnotherFunc: {self.updateBlocked()}")

class ChildGLGraphicsItem(AbstractGLGraphicsItem):
    def __init__(self, parentItem: 'AbstractGLGraphicsItem' = None, **kwargs):
        super().__init__(parentItem=parentItem, **kwargs)

    def SomeFunc(self):
        self.blockUpdates(True)
        self.AnotherFunc()


child = ChildGLGraphicsItem()

child.SomeFunc()

print(f"child.updateBlocked: {child.updateBlocked()}")
