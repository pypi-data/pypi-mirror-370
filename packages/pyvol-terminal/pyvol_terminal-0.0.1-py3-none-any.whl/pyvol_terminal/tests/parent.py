
from PySide6 import QtCore, QtGui, QtWidgets    
app = QtWidgets.QApplication([])


def close():
    parent.close()
    import time
    time.sleep(2)
    import sys
    sys.exit()




parent = QtWidgets.QWidget()
parent.setWindowTitle("Parent Widget")
parent.resize(300, 200)
layout = QtWidgets.QVBoxLayout(parent)
label_parent = QtWidgets.QLabel("This is the parent widget")
layout.addWidget(label_parent)


timer = QtCore.QTimer()
timer.timeout.connect(close)
timer.start(2000)


child = QtWidgets.QWidget(parent)
child.setWindowTitle("Child Widget")
child.resize(150, 100)
child.move(50, 50)
label_child = QtWidgets.QLabel("This is the child widget", child)
child.show()



parent.show()
app.exec()
