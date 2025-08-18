import sys
import numpy as np
from PySide6 import QtWidgets, QtCore, QtGui
import pyqtgraph.opengl as gl
from OpenGL import GL


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.widget1 = QtWidgets.QWidget()  
        self.setCentralWidget(self.widget1)
        self.widget1.setLayout(QtWidgets.QVBoxLayout())
        self.widget2 = QtWidgets.QWidget()
        self.lw2 = QtWidgets.QHBoxLayout(self.widget2)
        
        self.gl_widget = gl.GLViewWidget()
        self.lw2.addWidget(self.gl_widget)
        print(self.gl_widget.layout())
        
        self.widget1.layout().addWidget(self.widget2)
   #     self.widget1.layout().addWidget(self.gl_widget)
        self.show()

        print(self.gl_widget.isValid())

def main():
    """Main function to run the application."""
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
