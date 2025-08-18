import sys
from PySide6 import QtWidgets, QtGui, QtCore

windows = []

def open_new_window(title):
    w = QtWidgets.QMainWindow()
    w.setWindowTitle(title)
    w.setCentralWidget(QtWidgets.QLabel(f"This is {title}"))
    w.resize(400, 300)
    w.show()
    windows.append(w)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        container = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(container)
        btn1 = QtWidgets.QPushButton("Button 1")
        btn2 = QtWidgets.QPushButton("Button 2")
        btn3 = QtWidgets.QPushButton("Button 3")
        layout.addWidget(btn1)
        layout.addWidget(btn2)
        layout.addWidget(btn3)
        btn1.clicked.connect(lambda: open_new_window("Window from Button 1"))
        btn2.clicked.connect(lambda: open_new_window("Window from Button 2"))
        btn3.clicked.connect(lambda: open_new_window("Window from Button 3"))
        self.setCentralWidget(container)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setFont(QtGui.QFont("Neue Haas Grotesk"))

    mainWin = MainWindow()
    mainWin.show()
    windows.append(mainWin)

    sys.exit(app.exec())
