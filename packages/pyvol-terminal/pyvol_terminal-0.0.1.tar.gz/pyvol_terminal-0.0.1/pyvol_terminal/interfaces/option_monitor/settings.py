from __future__ import annotations 
from typing import List, Optional, Tuple, Union, Dict, TYPE_CHECKING, Callable
if TYPE_CHECKING:
    from .tables import StrikeTableColumn
    from ...instruments.instruments import ABCInstrument
    from .main_view import MainView
    from .interface import Interface

from PySide6 import QtWidgets
from . import stylesheets as stylesheets
from pyvol_terminal.misc_classes import PriceText
import uuid

class SpotLabel(QtWidgets.QLabel):
    def __init__(self, spot_object, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.spot_object: ABCInstrument = spot_object
        self.setStyleSheet(stylesheets.get_settings_stylesheets("SpotQLabel"))
        self.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        
    def update_text(self):
        self.spot_object.mid
        self.setText(str(self.spot_object))


class Settings(QtWidgets.QWidget):
    def __init__(self, strike_table_column, spot_objects=None, buttonLabels=[], columnCollection=None):
        super().__init__()
        
        self.setLayout(QtWidgets.QVBoxLayout())
        self._initTopSettings(buttonLabels)
        self._initBottomSettings(strike_table_column, spot_objects)
        
    def _initTopSettings(self, buttonLabels):
        
        self.button_group_top = QtWidgets.QButtonGroup()
        self.layout_top = QtWidgets.QHBoxLayout()
        for idx, btnLabel in enumerate(buttonLabels):
            btn = QtWidgets.QPushButton("kfewfkedaa")
            btn.setStyle("background-color: white;")
            self.layout_top.addWidget(btn)  
            self.button_group_top.addButton(btn, idx) 
        
        widget = QtWidgets.QWidget()
        widget.setLayout(self.layout_top)
        
        self.layout().addWidget(widget)
        self.layout_top.addStretch()
        
        
    def _initBottomSettings(self, strike_table_column, spot_objects):
        self.layout_bottom = QtWidgets.QHBoxLayout()
        self.layout().addLayout(self.layout_bottom)
        self.strike_center(strike_table_column)

        if not spot_objects is None:
            self.create_spot_label(spot_objects)
            
        self.layout_bottom.setContentsMargins(0, 0, 0 ,0)

        self.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.setStyleSheet(""" 
                           background-color: black;
                           """)
        
        title = QtWidgets.QLabel("Strikes")
        
        title.setStyleSheet("""
                            QLabel {background-color: black;
                                    color: #fb8b1e;}
                            """)
        self.n_strikes_line = QtWidgets.QLineEdit()
        self.n_strikes_line.blockSignals(True)
        self.n_strikes_line.setText(str(5))
        self.n_strikes_line.setStyleSheet(stylesheets.get_settings_stylesheets("QLineEdit"))
        self.n_strikes_line.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.n_strikes_line.editingFinished.connect(lambda: self.n_strike_edit(self.n_strikes_line.text(), strike_table_column))
        self.n_strikes_line.blockSignals(False)
        self.layout_bottom.addWidget(title)
        self.layout_bottom.addWidget(self.n_strikes_line)
        
    def n_strike_edit(self,
                      text: str,
                      strike_table_column: StrikeTableColumn,
                      ):
        n_strikes = int(round(float(text)))
        strike_table_column.bulk_change_strike_num(n_strikes)
        self.n_strikes_line.clearFocus()

    def strike_center(self, strike_table_column):
        title = QtWidgets.QLabel("Center")
        title.setStyleSheet("""
                            QLabel {
                                    background-color: black;
                                    color: #fb8b1e;
                            }
                            """)
        self.strike_center_line = QtWidgets.QLineEdit()
        self.strike_center_line.setText(str(strike_table_column.strike_center))
        self.strike_center_line.setStyleSheet(stylesheets.get_settings_stylesheets("QLineEdit"))
        self.strike_center_line.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.strike_center_line.editingFinished.connect(lambda: self.strike_center_edit(self.strike_center_line.text(), strike_table_column))
        self.layout_bottom.addWidget(title)
        self.layout_bottom.addWidget(self.strike_center_line)
        
    def strike_center_edit(self,
                           text: str,
                           strike_table_column: StrikeTableColumn
                           ):
        strike_table_column.change_center(text)
        self.strike_center_line.clearFocus()

    def create_spot_label(self, spot_objects):
        spot_label = SpotLabel(spot_objects)
        self.layout_bottom.addWidget(spot_label)
    
    def add_window_menu(self, interface: Interface):
        
        btn=self.button_group_top.button(0)
        btn.clicked.connect(lambda _ : self._open_axis_settings_window(interface.main_view))

    def _open_axis_settings_window(self, main_view: MainView):
        geometry = self.window().geometry()
        
        interface_center = geometry.center()
        
        geometry.setSize(geometry.size() / 2)
        geometry.moveCenter(interface_center)
        
        widget = ColumnParameters(main_view,
                                options=main_view.currentColumns(),
                                slots=[main_view.setColumns],
                            #    close_slots=[self._setPrevAxisSettingState],
                                parentSettings=self,
                                )
        geometry=None
        self.sub_window=widget
        widget.show()
        
    def _setPrevAxisSettingState(self, state):
        self._prevAxisSettingState=state




class settingsMixin:
    def __init__(self, *args, parentSettings=None, **kwargs):
        self.parentSettings = parentSettings  
        self._intense_interacting=False
        self._id = uuid.uuid4() 
        self.parentSettings.addIntenseInteractingChild(self.id())
        super().__init__(*args, **kwargs)
        
    
    def id(self): return self._id
    
    def processIntenseInteraction(self, state):
        if state != self._intense_interacting:
            self._intense_interacting=state
            self.parentSettings.updateChildInteraction(self.id(), state)


    
class ColumnParameters(settingsMixin, QtWidgets.QDialog):
    
    _slots = []
    
    _default_options = {"bid" : None, "ask" : None, "IVM" : None}

        
    def __init__(self, main_view: MainView, options=None, slots=[], close_slots=[], parentSettings=None, **kwargs):
        super().__init__(parentSettings=parentSettings, **kwargs)
        self.main_view=main_view
        self._pending_signal_args = {"columns" : []
                                    }
        if options is None:
            self._current_opt = ColumnParameters._default_options
        else:
            self._current_opt = options            
        self.close_slots=close_slots
        self.parentSettings=parentSettings
        
        self._initLayout()
        self.show()
        
    def _initLayout(self):
        group = QtWidgets.QButtonGroup()
        group.setExclusive(False)
        button_layout = QtWidgets.QVBoxLayout()
        
        for opt_name, flag in self._current_opt.items():
            button = QtWidgets.QPushButton(opt_name)
            button.isCheckable(True)
            button.setChecked(flag)
            group.addButton(button)
            button_layout.addWidget(button)
        self.setLayout(button_layout)
        

        