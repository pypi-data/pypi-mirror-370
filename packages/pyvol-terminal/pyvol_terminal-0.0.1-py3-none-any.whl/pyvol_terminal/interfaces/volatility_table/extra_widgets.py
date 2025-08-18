from PySide6 import QtGui, QtWidgets, QtCore
from . import stylesheets


class OptionMetricCellItem(QtWidgets.QTableWidgetItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFlags(self.flags() | QtCore.Qt.ItemIsSelectable)
        self.setFlags(self.flags() & ~QtCore.Qt.ItemIsEditable)
        self.setBackground(QtGui.QBrush("black"))
        self.setForeground(QtGui.QBrush("#fb8b1e"))
        self.setTextAlignment(QtCore.Qt.AlignRight)
        font = QtGui.QFont("Neue Haas Grotesk", 12)
        self.setFont(font)


class Option(QtWidgets.QTableWidgetItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFlags(self.flags() | QtCore.Qt.ItemIsSelectable)
        self.setFlags(self.flags() & ~QtCore.Qt.ItemIsEditable)
        self.setBackground(QtGui.QBrush("black"))
        self.setForeground(QtGui.QBrush("#fb8b1e"))
        self.setTextAlignment(QtCore.Qt.AlignRight)
        font = QtGui.QFont("Neue Haas Grotesk", 12)
        self.setFont(font)


class OptionExpiryCellItem(QtWidgets.QTableWidgetItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        self.setBackground(QtGui.QBrush("black"))
        self.setForeground(QtGui.QBrush("#fb8b1e"))
        self.setTextAlignment(QtCore.Qt.AlignLeft)
        font = QtGui.QFont("Neue Haas Grotesk", 12)
        self.setFont(font)

class TableColumnItem(QtWidgets.QTableWidgetItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        self.setBackground(QtGui.QBrush("#232323"))
        self.setForeground(QtGui.QBrush("white"))
        self.setTextAlignment(QtCore.Qt.AlignRight)
        font = QtGui.QFont("Neue Haas Grotesk", 12)
        self.setFont(font)



class StrikeOptionsComboBox(QtWidgets.QComboBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.view().setAutoScroll(False)
        self.setStyleSheet(stylesheets.get_settings_stylesheets("StrikeOptionsComboBox"))        
        font = QtGui.QFont("Neue Haas Grotesk", 12)
        self.setFont(font)

    def wheelEvent(self, event):
        if self.view().isVisible():
            super().wheelEvent(event)
            

