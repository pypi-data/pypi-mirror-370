from __future__ import annotations
from typing import List, Dict, Union, Tuple, Callable, TYPE_CHECKING
if TYPE_CHECKING:
    from instruments.utils import InstrumentManager

from PySide6 import QtCore, QtWidgets, QtGui
from .. import windows
from pyvol_terminal import workers
from pyvol_terminal.data_classes import builders as builders_data_classes
from PySide6.QtMultimedia import QSoundEffect
class WarningClose(QtWidgets.QDialog):
    def __init__(self, geometry: QtCore.QRect, app_widget: Frontend, parent=None):
        super().__init__(parent=parent)
        self.app_widget = app_widget
        self._quitting = False
        
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setContentsMargins(20, 20, 20, 20)  # Add some margins
        
        label = QtWidgets.QLabel("Close PyVol Surface?")
        label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        
        self.layout().addWidget(label)
        button_layout = QtWidgets.QHBoxLayout()
        
        self.button_yes = QtWidgets.QPushButton("Yes")
        self.button_no = QtWidgets.QPushButton("No")
        
        self.button_yes.clicked.connect(self._closeAppSlot)
        self.button_no.clicked.connect(self._keepAppOpenSlot)
        
        button_layout.addWidget(self.button_yes)
        button_layout.addWidget(self.button_no)
        self.layout().addLayout(button_layout)
        
        self.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.hide()
    
    def show(self):
        parent_geometry = self.app_widget.geometry()
        half_width = parent_geometry.width() // 2
        
        self.adjustSize()
        natural_height = self.sizeHint().height()
        
        new_geometry = QtCore.QRect(parent_geometry.x() + (parent_geometry.width() - half_width) // 2,
                                    parent_geometry.y() + (parent_geometry.height() - natural_height) // 2,
                                    half_width,
                                    natural_height
                                    )
        
        self.setGeometry(new_geometry)
        super().show()
        
        self.setFixedSize(self.size())
    
    def _initLayout(self, geometry: QtCore.QRectF):
        self.setLayout(QtWidgets.QVBoxLayout())
        
        interface_center = geometry.center()
        geometry.setSize(geometry.size())
        geometry.moveCenter(interface_center)
        print(geometry)
            
        self.setGeometry(geometry)

    @QtCore.Slot()
    def _keepAppOpenSlot(self, *args, **kwargs):
        self.hide()
        self.app_widget._warned_user = False
        
    @QtCore.Slot()
    def _closeAppSlot(self, *args, **kwargs):
        QtWidgets.QApplication.instance().exit()
    
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key.Key_Escape:
            self._keepAppOpenSlot()
        elif event.key() == QtCore.Qt.Key.Key_Shift:
            pass
        return super().keyPressEvent(event)
    
                
    def closeEvent(self, event):
        if self._quitting:
            super().closeEvent(event)
        else:
            event.ignore()
            self._keepAppOpenSlot()


class Frontend(QtWidgets.QMainWindow):
    def __init__(self,
                 open_window_signal: QtCore.Slot,
                 instruments: List[str],
                 interfaces: List[str],
                 parent=None
                 ) -> Frontend:
        super().__init__(parent)
        self.open_window_signal=open_window_signal
        self.instruments=instruments
        self.interfaces=interfaces
        
        self._warned_user=False
        self.warning_close_win = WarningClose(self.geometry(), app_widget=self)
        main_layout = QtWidgets.QVBoxLayout()
        
        self.buttons: List[QtWidgets.QPushButton] = []
        
        self.setCentralWidget(QtWidgets.QWidget())
        self.centralWidget().setLayout(main_layout)
        self._initLayoutContents()
        
        self.setMouseTracking(True)
        self.centralWidget().setMouseTracking(True)
        self._enableMouseTrackingForChildren(self.centralWidget())
            
    def _initLayoutContents(self):
        button_layout = QtWidgets.QHBoxLayout()
        
        for interface in self.interfaces:
            button = QtWidgets.QPushButton(interface)
            button.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed) 
            button.clicked.connect(self.create_button_handler(interface))
            button_width = 200  
            button_height = 100  
            button.setFixedSize(button_width, button_height)
            
            font = button.font()
            target_font_width = button_width // 1.5  
            target_font_height = button_height // 2  
            
            self.button_font_size(font, interface, button, target_font_width, target_font_height)
            
            self.buttons.append(button)
            button_layout.addWidget(button)
        
        self.combo_box = QtWidgets.QComboBox()
        self.combo_box.addItems(["No Option Chain Selected"] + self.instruments)
        self.combo_box.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Maximum)
        self.combo_box.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
        self.combo_box.currentIndexChanged.connect(self.update_button_state)
        combo_font = self.combo_box.font()

        self.combo_box.setFont(combo_font)
        self.centralWidget().layout().addWidget(self.combo_box)
        self.centralWidget().layout().addLayout(button_layout)
        self.setStyleSheet("""
                           QPushButton { font-size: 28px; }
                           QComboBox { font-size: 14px; }
                           """
                           )
        
        self.update_button_state(0)
        self.adjustSize()              
        self.setFixedSize(self.size()) 
            
    def update_button_state(self, index):
        state = index != 0
        for button in self.buttons:
            button.setEnabled(state)
        if index == 0:
            for button in self.buttons:
                button.setStyleSheet("""
                                     QPushButton:disabled {background-color: #d0d0d0;  
                                     color: #666666;
                                     border: 1px solid #bbbbbb;}
                                     """
                                     )
        else:
            for button in self.buttons:
                button.setStyleSheet("")
        
    def closeEvent(self, event):
        return super().closeEvent(event)
        if self.warning_close_win.isVisible():
            event.ignore()
            self._warningCloseAttention()
            return 
        else:
            if not self._warned_user:
                event.ignore()
                self.warning_close_win.show()
                self.update()
                self._warned_user = True
            else:
                super().closeEvent(event)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key.Key_Escape:
            self.close()
        return super().keyPressEvent(event)
    
    def button_font_size(self,
                         font: QtGui.QFont,
                         button_string: str,
                         button_object: QtWidgets.QPushButton,
                         target_font_width,
                         target_font_height
                         ) -> None:
        font_size = 1
        while True:
            font.setPointSize(font_size)
            button_object.setFont(font)
            new_metrics = button_object.fontMetrics()
            if (new_metrics.horizontalAdvance(button_string) > target_font_width or 
                new_metrics.height() > target_font_height):
                font.setPointSize(font_size - 1) 
                button_object.setFont(font)
                break
            font_size += 1
    
    def create_button_handler(self, interface: str):
        captured_interface = interface
        @QtCore.Slot()
        def handler():
            selected_option = self.combo_box.currentText()
            return self.open_window_signal(selected_option, captured_interface)
        return handler

    def _enableMouseTrackingForChildren(self, widget):
        for child in widget.findChildren(QtWidgets.QWidget):
            child.setMouseTracking(True)
            self._enableMouseTrackingForChildren(child)

    def eventFilter(self, obj, event):
        if (event.type() in (QtCore.QEvent.MouseButtonPress, QtCore.QEvent.MouseButtonDblClick) and 
            self.warning_close_win.isVisible()):
            self._warningCloseAttention()
            return True
        return super().eventFilter(obj, event)

    def showEvent(self, event):
        super().showEvent(event)
        self.centralWidget().installEventFilter(self)
        for child in self.centralWidget().findChildren(QtWidgets.QWidget):
            child.installEventFilter(self)

    def _warningCloseAttention(self):
        self.warning_close_win.activateWindow()
        self.warning_close_win.setFocus()
