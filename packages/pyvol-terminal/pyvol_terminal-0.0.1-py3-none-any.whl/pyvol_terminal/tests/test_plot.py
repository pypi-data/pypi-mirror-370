import sys
import numpy as np
import pyqtgraph as pg
from PySide6.QtWidgets import QApplication
from pyqtgraph import Point
from PySide6 import QtGui, QtCore
from math import ceil, floor, frexp, isfinite, log10, sqrt
from pyqtgraph import debug
from pyqtgraph import functions as fn
import sys
import numpy as np
from PySide6 import QtWidgets, QtCore, QtGui
import pyqtgraph.opengl as gl
from OpenGL import GL
import enum
from pprint import pprint



class CustomItemGroup(pg.ItemGroup):
    def __init__(self, name):
        self.name=name
        pg.ItemGroup.__init__(self)

class CustomGraphicsObject(QtWidgets.QGraphicsObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.__flags = QtWidgets.QGraphicsItem.GraphicsItemFlag()
    
    def itemChange(self, change, value):

        res = super().itemChange(change, value)
        return res
    
    def setFlag(self, flag, enable):
        
        res = super().setFlag(flag, enable)
        
    
    def setFlag2(self, flag: enum.Flag, enabled=True):
        self.itemChange(self.GraphicsItemChange.ItemFlagsChange, enabled)
        flag_int = flag.value if hasattr(flag, 'value') else flag
        
        if enabled:
            new_flags = self.flags() | flag
        else:
            new_flags = self.flags() & ~flag
        
        if self.__flags != new_flags:
            self.__flags = new_flags
        self.itemChange(self.GraphicsItemChange.ItemFlagsHaveChanged, enabled)
        
    def flags2(self):
        return self.__flags
    
class CustomPlotDataItem(pg.PlotDataItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        
    def itemChange(self, change, value):
        res = super().itemChange(change, value)
        return res



class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.plot_item = pg.PlotItem()

        
    #    self.plot_item.setAutoVisible(True, True)

    #    self.legendItem =pg.LegendItem((80,60), offset=(70,20))
      #  self.legendItem.setParentItem(self.plot_item)
        
        

        """
        plot_item.setAxisItems({"left": pg.AxisItem(orientation="left"),
                                "bottom": pg.AxisItem(orientation="bottom")
                                }
                               )
        """
        

        
        ax1 = self.plot_item.getAxis("left")
        ax1.enableAutoSIPrefix(True)
      #  ax1.setStyle(tickLength=20)
        
        ax1.setLabel("abc")
        
        
        ax2 = self.plot_item.getAxis("bottom")
        ax2.enableAutoSIPrefix(True)

     #   ax2.setStyle(tickLength=20)
        
        
        x = np.linspace(0, 1, 20)
        y = 20*x
        
        self.plot_data = pg.PlotDataItem(x=x, y=y, pen='r', name="abcde")
        self.plot_item.addItem(self.plot_data)
        self.plot_data.setClipToView(True)
        self.plot_data.setDownsampling(None, True, "subsample")
        self.plot_data.setDynamicRangeLimit(1e5)
        self.plot_data.setSymbol("x")
    
        

        self.plot_data.update()

        self.timer = QtCore.QTimer()
        
      #  self.plot_item.setScale(100)
        
      
        self.timer.timeout.connect(self.set)
       # import sys
       # sys.exit()

        
         

        plot_widget = pg.PlotWidget(plotItem=self.plot_item)
        self.setCentralWidget(plot_widget)
        self.show()
  
        y*=2

        self.plot_data.setData(x, y)
        self.count=1
        #self.plot_data.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemHasNoContents, False)
        

        
        
        
        

        # Run the Qt application
    def set(self):

        xdata= self.plot_data.xData
        xr = xdata.max() - xdata.min()
        
        xnew = np.linspace(xdata.min() - 0.1 * xr, xdata.max() + 0.1 * xr, xdata.size + 1)
        ynew_pre = self.plot_data.yData
        ynew = np.linspace(ynew_pre.min(), ynew_pre.max(), xnew.size)
        #self.plot_data.setData(xnew, ynew)
        self.plot_data.setData(y=1000 * self.plot_data.yData)
       # self.update()
        print(f"self.plot_data.scale: {self.plot_data.scale()}")
        
        #self.plot_item.update()
        self.count+=1

def main():
    """Main function to run the application."""
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.timer.start(1000)
    sys.exit(app.exec())

if __name__ == "__main__":
    main()