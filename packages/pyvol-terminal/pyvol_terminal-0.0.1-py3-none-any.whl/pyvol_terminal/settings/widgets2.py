from PySide6 import QtWidgets, QtCore
from . import utils


class MainSettings(QtWidgets.QWidget):
    def __init__(self, widget_main=None, interfaces=None):
        super().__init__()
        self.widget_main=widget_main
        self.idx_to_interface_name = {}
        
        self.starting_button=0
        self.prev_btn_idx=0

        for idx, interface_name in enumerate(interfaces):            
            self.idx_to_interface_name[idx] = interface_name
            
        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0 ,0)
        self._create_interface(interfaces)
        self.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        
        
    @QtCore.Slot(QtWidgets.QPushButton)
    def on_button_clicked(self, button):
        btn_id = self.button_group.id(button)
        if btn_id == self.prev_btn_idx:
            return 
        else:
            self.prev_btn_idx = btn_id
        
        interface_name = self.idx_to_interface_name[btn_id]
        
        
        self.widget_main.switch_view(interface_name)
        
    
    def _create_interface(self, interface_widgets):        
        self.button_group = QtWidgets.QButtonGroup()
        self.button_group.setExclusive(True)

        self.buttons = []
        self.selection_labels = list(interface_widgets.keys())
        self.button_name_maps = {i : interface_name for i, interface_name in enumerate(self.selection_labels)}
        
        for i, label in enumerate(self.selection_labels):
            btn = QtWidgets.QPushButton(label)
            btn.setCheckable(True)
            btn.setStyleSheet(utils.get_settings_stylesheets("QPushButton"))
            self.buttons.append(btn)
            self.layout.addWidget(btn)
            self.button_group.addButton(btn, id=i) 
            btn.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)

        self.button_group.buttonClicked.connect(self.on_button_clicked)
        self.button_group.blockSignals(True)  
        self.buttons[self.starting_button].setChecked(True)     
        self.button_group.blockSignals(False)       
        
