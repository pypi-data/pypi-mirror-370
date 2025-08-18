from __future__ import annotations
from typing import List, Optional, Tuple, Union, Dict, TYPE_CHECKING, Callable
if TYPE_CHECKING:
    from pyvol_terminal.windows import Window


from PySide6 import QtWidgets, QtCore
from . import utils



class ContextPushButton(QtWidgets.QPushButton):
    def __init__(self, label, parent=None):
        super().__init__(label, parent)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(lambda pos: parent._show_button_menu(self, pos))

    def mousePressEvent(self, ev):
        if ev.button() == QtCore.Qt.RightButton:
            ev.accept()
            self.customContextMenuRequested.emit(ev.pos())
        else:
            super().mousePressEvent(ev)


class WindowSettings(QtWidgets.QWidget):
    def __init__(self,
                 new_window_slots: List[Callable],
                 interface_name_slot_map: Dict[str, Callable]):
        super().__init__()
        self.new_window_slots=new_window_slots
        self.interface_name_slot_map=interface_name_slot_map
        self.idx_to_interface_name = {}
        self._interface_to_idx={}
        
        self.setLayout(QtWidgets.QHBoxLayout())
        self.layout().setContentsMargins(0, 0, 0 ,0)

        self.button_group = QtWidgets.QButtonGroup()
        btn=QtWidgets.QPushButton("Open New Window")
        btn.setCheckable(False)
        self.button_group.addButton(btn, 0)
        for slot in self.new_window_slots:
            btn.clicked.connect(slot)
        self.layout().addWidget(btn)
            
        self._create_interface_buttons()
        self.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        
    def _create_interface_buttons(self):        
        self.button_group.setExclusive(True)
        
        for idx, (name, slots) in enumerate(self.interface_name_slot_map.items(), start=1):
            self._interface_to_idx[name]=idx
            btn=QtWidgets.QPushButton(name)
            btn.setStyleSheet(utils.get_settings_stylesheets("QPushButton"))
            btn.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            btn.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
            
            btn.setCheckable(True)
            btn.setChecked(False)            
            
            self.button_group.addButton(btn, id=idx) 
            self.layout().addWidget(btn)
            
            for slot in slots:
                self.button_group.idToggled.connect(slot)
            
    def toggle_price_type(self,
                          idx: int=None,
                          name: str=None
                          ):
        if not idx is None:
            self.button_group.button(idx).toggle()
        else:
            if not name is None:
                print(self._interface_to_idx[name])
                print(self.button_group.button(self._interface_to_idx[name]))
                self.button_group.button(self._interface_to_idx[name]).toggle()
            
    @QtCore.Slot(QtWidgets.QPushButton)
    def left_click(self, button):
        btn_id = self.button_group.id(button)
        print(f"btn_id: {btn_id}")
        if btn_id == self.prev_btn_idx:
            return 
        else:
            self.prev_btn_idx = btn_id
        
        interface_name = self.idx_to_interface_name[btn_id]
        print(f"interface_name: {interface_name}")
        for callback in self.interface_name_callbacks_dict[interface_name]:
            callback(interface_name)
    
             
    def _popout_action(self, interface_name, btn_id):   
        interface = self.window_widget.interfaces[interface_name]
        if btn_id != self.prev_btn_idx:
            self.window_widget.price_process_worker.update_interface_signal.connect(interface.update_interface)
                 
        self.open_new_window(interface_name, interface, self.configs, self._collapse_action)
        btn = self.button_group.button(btn_id)
        self.button_group.removeButton(btn)
        self.layout().removeWidget(btn)
        self.buttons.remove(btn)
        btn.deleteLater()      
        other_interface_btn = self.buttons[0] 
        idx = self.button_group.id(other_interface_btn)
        other_interface = self.window_widget.interfaces[self.idx_to_interface_name[idx]]
        self.window_widget.price_process_worker.update_interface_signal.connect(other_interface.update_interface)
        self.left_click(other_interface_btn)
        
         
    
    def _collapse_action(self, interface_name, sub_window):
        print(f"\n_collapse_action")
        print(f"{self.main_window_flag}")
        print(f"self.idx_to_interface_name: {self.idx_to_interface_name}")
        self.window_widget.price_process_worker.update_interface_signal.disconnect(sub_window.interface.update_interface)
        sub_window.close()
        del sub_window
        btn = ContextPushButton(interface_name, parent=self)
        btn.setCheckable(True)
        btn.setStyleSheet(utils.get_settings_stylesheets("QPushButton"))
        btn.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.buttons.append(btn)
        self.layout().addWidget(btn)
        btn_id = self._interface_to_idx[interface_name]
        self.button_group.addButton(btn, id=btn_id) 
        btn.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
    
        
    def _show_button_menu(self, button, pos):
        menu = QtWidgets.QMenu(self)
        btn_id = self.button_group.id(button)
        iface = self.idx_to_interface_name[btn_id]
        menu.blockSignals(True)
        if self.main_window_flag:        
            menu.addAction("Pop-out Window", lambda: self._popout_action(iface, btn_id))
        else:
            menu.addAction("Collapse Window", lambda: self.main_window_collapse_func(iface, self.window_widget))
        menu.blockSignals(False)
        menu.exec(button.mapToGlobal(pos))
        



class CenteredPopupComboBox(QtWidgets.QComboBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def showPopup(self):
        super().showPopup()
        
        popup = self.view()
        current_index = self.currentIndex()

        if current_index >= 0:
            rect = popup.visualRect(popup.model().index(current_index, 0))
            scroll_position = rect.top() - (popup.viewport().height() - rect.height()) // 2
            popup.verticalScrollBar().setValue(scroll_position)

    def wheelEvent(self, event):
        if self.view().isVisible():
            super().wheelEvent(event)
