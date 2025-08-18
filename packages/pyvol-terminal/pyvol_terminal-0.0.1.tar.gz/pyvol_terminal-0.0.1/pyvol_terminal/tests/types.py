from PySide6 import QtWidgets
import sys
app = QtWidgets.QApplication(sys.argv)


s = QtWidgets.QSplitter()
w = QtWidgets.QWidget()
l = QtWidgets.QHBoxLayout()


print(issubclass(QtWidgets.QSplitter, QtWidgets.QWidget))

print(issubclass(QtWidgets.QSplitter, QtWidgets.QHBoxLayout))
