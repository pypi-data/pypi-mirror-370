from __future__ import annotations 
from typing import List, Optional, Tuple, Union, Dict, TYPE_CHECKING, Callable
if TYPE_CHECKING:
    from .interface import Interface
    from .main_view import MainView
    
from PySide6 import QtWidgets, QtGui, QtCore
from pyvol_terminal.settings import utils as settings_utils
from functools import partial
import math
from pprint import pprint
import uuid
from ...settings.widgets import CenteredPopupComboBox
from dataclasses import dataclass
from ...instruments.quantities import IVOLMetrics

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
          #  self.parentSettings.updateChildInteraction(self.id(), state)

class intenseCheckComboBox(settingsMixin, QtWidgets.QComboBox):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.activated.connect(lambda : self.processIntenseInteraction(False))

    def showPopup(self):
        self.processIntenseInteraction(True)
        return super().showPopup()
    

    
class intenseCheckMenu(settingsMixin, QtWidgets.QMenu):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.aboutToHide.connect(lambda : self.processIntenseInteraction(False))
        
    def popup(self):
        self.processIntenseInteraction(True)
        super().popup()
    
    def closeEvent2(self, event):
        super().closeEvent(event)
        self.processIntenseInteraction(False)
        return 

class RefSlotsMenu(QtWidgets.QMenu):
    def __init__(self, *args, **kwargs):
        self._connected_slots={}
        super().__init__(*args, **kwargs)
    
    def addAction(self, action: QtGui.QAction, slots: List[Callable], how) -> None:
        self._connected_slots[action.text()] = slots
        super().addAction(action)

class Settings(QtWidgets.QToolBar):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._prevAxisSettingState = None
        self.dimension_actions = {}
        self.toggle_button_actions = {}
        self._vol_source_actions=[]
        self.current_vol_configs=[]
        self._price_type_action_container = []
        self._name_idx_map = {}
        self.title_axis_dict = {"Money": "x",
                                "Expiry": "y",
                                "Volatility": "z"
                                }
        self.prev_button = 1
        self.sub_window = None
        self.vol_src_title="Toggle Vol Sources"
        self.signal_container: Dict[str, QtCore.Signal] = {}
        
        self._intense_interaction_map = {}
        self._intense_interaction = False
        
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.setToolButtonStyle(QtCore.Qt.ToolButtonTextOnly)  # Consistent style for all buttons
    
    def addIntenseInteractingChild(self, id):
        self._intense_interaction_map[id] = False
        
    def updateChildInteraction(self, id, state):
        self._intense_interaction_map[id] = state
        current_state = any(self._intense_interaction_map.values())
        if current_state != self._intense_interaction:
            self._intense_interaction = current_state
            self.processIntenseInteraction("settings", current_state)
        
    def processIntenseInteraction(self): ...
    
    def remove_settings_menu(self, title, cls):
        submenu = self._find_widget(title, cls)
        self.removeWidget(submenu)
    
    def create_vol_src_menu(self,
                            options: List[str],
                            slots: Callable | List[Callable]=None,
                            slot_args=()
                            ):
        tool_button = QtWidgets.QToolButton()
        tool_button.setText(self.vol_src_title)
        tool_button.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        tool_button.setStyleSheet(settings_utils.get_settings_stylesheets("QToolButton"))
        
        menu = QtWidgets.QMenu(tool_button)
        menu.setStyleSheet(settings_utils.get_settings_stylesheets("QMenu"))
        
        action_group = QtGui.QActionGroup(menu)
        action_group.setExclusive(False)
        
        tool_button.setMenu(menu)
        tool_button.setObjectName(self.vol_src_title)
        self.addWidget(tool_button)

        for opt in options:
            action = QtGui.QAction(opt)
            action.setCheckable(True)
            action.setChecked(False)
            menu.addAction(action)
            action_group.addAction(action)
        if not slots is None:
            self.connect_vol_src_slots(action_group.actions(), slots, slot_args)
    
    def connect_vol_src_slots(self,
                              actions: List[QtGui.QAction]=None,
                              slots: List[Callable]=[],
                              slot_args=()
                              ):
        if actions is None:
            actions = self._find_widget(self.vol_src_title, QtWidgets.QToolButton).menu().actions()
        for action in actions:
            for slot in slots:
                print(f"slot_args: {slot_args}")
                action.triggered.connect(lambda checked, handler=slot, name=action.text(): handler(checked, name, *slot_args))

    def toggle_vol_src(self,
                       vol_src: str
                       ):
        tool_button = self._find_widget(self.vol_src_title, QtWidgets.QToolButton)
        for action in tool_button.menu().actions():
            if action.text() == vol_src:
                action.setChecked(True)
        
    def create_combobox_menu(self,
                             title: str,
                             options: List[str],
                             slots: Callable | List[Callable]=None,
                             slot_args=()
                             ):
        combobox = QtWidgets.QComboBox()
        combobox.setToolTip(title)
        options = options  + ["Select an option..."]
        combobox.addItems(options)
        self.addWidget(combobox)
        if not slots is None:
            self.connect_slots_to_combobox(combobox, slots, slot_args)
            
    def connect_slots_to_combobox(self,
                                  title_or_cbox: str | QtWidgets.QComboBox,
                                  slots: List[Callable|QtCore.Slot],
                                  slot_args=()
                                  ):
        if isinstance(title_or_cbox, str):
            combobox = self._find_widget(title_or_cbox, QtWidgets.QComboBox)
        else:
            combobox = title_or_cbox
            
        if combobox.count() == 0:
            combobox.setCurrentIndex(0)
        slots = [slots] if callable(slots) else slots        
        
        for s in slots:
            if not slot_args is None:
                combobox.currentTextChanged.connect(lambda text, args=slot_args, slot=s: slot(text, *args))
            else:
                combobox.currentIndexChanged.connect(s)
    
    def create_toggle_buttons(self,
                              title: str | QtWidgets.QComboBox,
                              options: List[str],
                              slots: Callable | List[Callable]=None,
                              slot_args=()
                              #toggles: List[bool]
                              ):
        tool_button = QtWidgets.QToolButton()
        tool_button.setText(title)
        tool_button.setStyleSheet(settings_utils.get_settings_stylesheets("QToolButton"))
        tool_button.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        
        menu = QtWidgets.QMenu(tool_button)
        menu.setStyleSheet(settings_utils.get_settings_stylesheets("QMenu"))

        tool_button.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        tool_button.setMenu(menu)
        tool_button.setObjectName(title)
        self.addWidget(tool_button)
        
        action_group = QtGui.QActionGroup(self)
        for options in options:
            action = QtGui.QAction(options, parent=self)
            action.setCheckable(True)
            action.setChecked(False)
            #action.setChecked(toggle)
            action_group.addAction(action)
            menu.addAction(action)
        
        if not slots is None:
            self.connect_toggle_button_slots(action_group.actions(), slots, slot_args)

    def connect_toggle_button_slots(self,
                                    label_or_actions: str | List[QtGui.QAction],
                                    slots: Callable | List[Callable]=None,
                                    slot_args=()
                                    ):
        if isinstance(label_or_actions, str):
            actions = self._find_widget(label_or_actions, QtWidgets.QToolButton).menu().actions()
        else:
            actions = label_or_actions
        for action in actions:
            for slot in slots:
                action.triggered.connect(lambda check, opt=action.text(), handler=slot: handler(check, opt, *slot_args))

    def add_window_menu(self, switch_axis_call: Callable):
        tool_button = QtWidgets.QToolButton() 
        tool_button.setText("Unit Settings")
        tool_button.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        
        cls_kwargs = {"options" : self._prevAxisSettingState,
                      "slots" : [switch_axis_call],
                      "close_slots": [self._setPrevAxisSettingState],
                      "parent" : self,
                      }
        tool_button.clicked.connect(lambda: self._open_submenu(AxisParameters, cls_kwargs))
        self.addWidget(tool_button)
    
    def add_vol_src_window_menu(self, all_price_types, slots: List[Callable]):
        tool_button = QtWidgets.QToolButton()
        tool_button.setText("Display Volatility") 
        tool_button.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        cls_kwargs = {"all_price_types" : all_price_types,
                      "slots" : slots + [self._setCurrentVolSrc],
                      "current_vol_configs" : self.current_vol_configs,
                      }
        tool_button.clicked.connect(lambda: self._open_submenu(VolSelection, cls_kwargs))
        self.addWidget(tool_button)
        
    def _setCurrentVolSrc(self, vol_configs: List[IVOLMetrics]):
        self.current_vol_configs=vol_configs
            
    def _find_widget(self, name, cls):
        for submenu in self.findChildren(cls):   
            if submenu.objectName() == name:
                return submenu

    def _open_submenu(self, cls, cls_kwargs):
        geometry = self.window().geometry()
        interface_center = geometry.center()
        geometry.setSize(geometry.size() / 2)
        geometry.moveCenter(interface_center)
        
        widget = cls(**cls_kwargs)
        self.sub_window = widget
        widget.show()
        
    def _setPrevAxisSettingState(self, state):
        self._prevAxisSettingState = state
        


class BlockQLineEdit(QtWidgets.QLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    @QtCore.Slot(str)
    def setDisableState(self, state):
        if state == "Automatic":
            self.setDisabled(True)
        else:
            self.setDisabled(False)



class ContainerWidget(QtWidgets.QWidget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    def resizeEvent(self, event):
        if self.parent() and hasattr(self.window(), 'frameSize'):
            window = self.window()
            frame_size = window.frameSize()
            content_size = window.size()
            
            width_diff = frame_size.width() - content_size.width()
            height_diff = frame_size.height() - content_size.height()
            
            print(f"\ncurrent window width: {window.width()}")
            print(f"target width: {self.width() + width_diff}")
            window.resize(self.width() + width_diff,
                          self.height() + height_diff
                          )
            print(f"new width: {window.width()}")
        super().resizeEvent(event)

    
class AxisParameters(QtWidgets.QDialog):
    
    _slots = []
    
    _default_options = {"unit" : {ax : "1" for ax in "xyz"},
                        "range" : {ax : ["", ""] for ax in "xyz"},
                        "control" : {ax : "automatic" for ax in "xyz"},
                        }
        
    def __init__(self,
                 options=None,
                 slots=[],
                 close_slots=[],
                 parentSettings=None,
                 **kwargs
                 ):
        super().__init__(**kwargs)
        self.table: QtWidgets.QTableWidget = None
        self._pending_signal_args = {"unit" : {ax : None for ax in "xyz"},
                                     "range" : {ax : None for ax in "xyz"},
                                     "control" : {ax : None for ax in "xyz"}
                                     }
        if options is None:
            self._current_opt = AxisParameters._default_options
        else:
            self._current_opt = options            
        self.close_slots=close_slots
        self.parentSettings=parentSettings
        
        self._initLayout()
        self._create_unit_settings(slots)
        self._create_axis_limits_settings()
        self._create_save_exit()

        self.table.resizeRowsToContents()
        self.table.resizeColumnsToContents()
        self.adjustSize()

    def showEvent(self, arg__1):
       # self.processIntenseInteraction(True)
        return super().showEvent(arg__1)
        
    def closeEvent(self, arg__1):
        super().closeEvent(arg__1) 
       # self.processIntenseInteraction(False)
                
    def _initLayout(self):
        container = self._setupMainContainer()
        self.table = self._setupTableWidget()
        self._setupColumnSync()
        
        self.save_close_widget = QtWidgets.QWidget()
        self.save_close_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        container.layout().addWidget(self.table)
        container.layout().addWidget(self.save_close_widget)
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(container)

        self.setLayout(layout)
        

    def _setupMainContainer(self) -> ContainerWidget:
        container = ContainerWidget()
        container.setLayout(QtWidgets.QVBoxLayout())
        container.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        container.layout().setContentsMargins(0, 0, 0, 0)
        return container


    def _setupTableWidget(self) -> QtWidgets.QTableWidget:
        table = QtWidgets.QTableWidget()
        
        table.setRowCount(3)
        table.setColumnCount(2)
        
        table.setVerticalHeaderLabels([f"{ax}-axis" for ax in "xyz"])
        table.setHorizontalHeaderLabels(["Axes Units", "Axes Limits"])
        table.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        
        table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        table.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        table.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        return table

    def _setupColumnSync(self):
        def _sync_column_widths(logicalIndex, oldSize, newSize):
            self.table.horizontalHeader().sectionResized.disconnect(_sync_column_widths)
            other_column = 1 if logicalIndex == 0 else 0
            self.table.setColumnWidth(other_column, newSize)
            self.table.horizontalHeader().sectionResized.connect(_sync_column_widths)
        self.table.horizontalHeader().sectionResized.connect(_sync_column_widths)
        
    def _setDarkPalette(self):
        palette = self.palette()
        palette.setColor(QtGui.QPalette.Window, QtGui.QColor(53, 53, 53))
        palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
        palette.setColor(QtGui.QPalette.Base, QtGui.QColor(25, 25, 25))
        palette.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
        palette.setColor(QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))
        palette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
        self.setPalette(palette)
        
    def _create_unit_settings(self, slots):
        self._slots = slots
        
        for idx, axis in enumerate("xyz"):
            combobox = CenteredPopupComboBox()
    
            for i in range(-5,6):
                value = 10**i
                if i<0:
                    text = "0." + "0"*(-1*i - 1) + "1"
                else:
                    text =  "1" + "0"*(i)
                combobox.addItem(text)
            
            combobox.setCurrentText(self._current_opt["unit"][axis])
            
            for _ in slots:
                combobox.currentTextChanged.connect(lambda text, ax=axis: self._queue_signal(text, "unit", ax))
            self.table.setCellWidget(idx, 0, combobox)
        self.table.horizontalHeader().setStretchLastSection(True)
        
    def _queue_signal(self, value, col, axis):
        self._pending_signal_args[col].update({axis : value})
    
    def _create_save_exit(self):
        button_layout = QtWidgets.QHBoxLayout(self.save_close_widget)
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        save_exit = QtWidgets.QPushButton("Save & Exit")
        exit = QtWidgets.QPushButton("Exit")
        
        save_exit.clicked.connect(self._on_save_exit)
        exit.clicked.connect(self._on_exit)
        
        button_layout.addWidget(save_exit)
        button_layout.addWidget(exit)
        
    def _on_save_exit(self):
        for col, data in self._pending_signal_args.items():
            for axis, value in data.items():
                if not value is None:
                    if value != self._current_opt[col][axis]:
                        for slot in self._slots:
                            slot(float(value), axis)
                        self._current_opt[col][axis] = value
        
        for slot in self.close_slots:
            slot(self._current_opt)
        self.window().close()
    
    def _on_exit(self):
        self.window().close()

    def _create_axis_limits_settings(self):
        for idx, axis in enumerate("xyz"):
            central_widget = QtWidgets.QWidget()
            layout = QtWidgets.QVBoxLayout(central_widget)
            
            combobox = QtWidgets.QComboBox()
            combobox.setFixedSize(combobox.sizeHint())
            
            combobox.addItems(["Automatic", "Set"])
            layout.addWidget(combobox)
            
            range_widget = QtWidgets.QWidget()
            range_layout = QtWidgets.QHBoxLayout(range_widget)
            range_layout.setContentsMargins(0, 0, 0, 0) 

            qlinedit_min = BlockQLineEdit(self._current_opt["range"][axis][0])
            if len(qlinedit_min.text()) == 0:
                qlinedit_min.setDisabled(True)
            else:
                qlinedit_min.setDisabled(False)
                
            qlinedit_max = BlockQLineEdit(self._current_opt["range"][axis][1])
            if len(qlinedit_max.text()) == 0:
                qlinedit_max.setDisabled(True)
            else:
                qlinedit_max.setDisabled(False)

            range_layout.addWidget(qlinedit_min)
            range_layout.addWidget(qlinedit_max)
            
            layout.addWidget(range_widget)
            
            combobox.setCurrentIndex(0)
            combobox.currentTextChanged.connect(qlinedit_min.setDisableState)
            combobox.currentTextChanged.connect(qlinedit_max.setDisableState)
            
            #self._queue_signal()
            
            self.table.setCellWidget(idx, 1, central_widget)
            
        self.table.horizontalHeader().setStretchLastSection(True)

class DynamicClickablePushButton(QtWidgets.QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setEnabled(False)
        self.setStyleSheet("""
                            QPushButton:disabled {background-color: #d0d0d0;  
                            color: #666666;
                            border: 1px solid #bbbbbb;}
                            """
                            )

    def setEnabledState(self, enabled):
        self.setEnabled(enabled)
        if enabled:
            self.setStyleSheet("")
        else:
            self.setStyleSheet("""
                                QPushButton:disabled {background-color: #d0d0d0;  
                                color: #666666;
                                border: 1px solid #bbbbbb;}
                                """
                                )

class VolSelection(QtWidgets.QDialog):
    def __init__(self,
                 all_price_types: List[str],
                 current_vol_configs: List[IVOLMetrics],
                 slots,
                 *args,
                 **kwargs
                 ):
        super().__init__(*args, **kwargs)
        self.all_price_types=all_price_types
        self.current_vol_configs=current_vol_configs
        self.slots=slots
        
        self._initLayout()
        self._initOptionSelection()
        self._initCurrentVolTypes()
        self._initCommandExecution()
        
        self.show()
        self.adjustSize()
        
    def _initLayout(self):
        self.table = QtWidgets.QTableWidget()
        self.table.setRowCount(3)
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Display Vol", "Remove Vol"])
        self.table.setVerticalHeaderLabels(["Option Price Type", "Underlying Price Type"])
        
        self.table.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        self.table.setSpan(0, 1, self.table.rowCount(), 1)
        
        self.setLayout(QtWidgets.QVBoxLayout()) 
        self.layout().addWidget(self.table)
        
    def _initOptionSelection(self):
        selections = ["Make a Selection..."] + self.all_price_types
        for idx in range(2):
            combobox = CenteredPopupComboBox()
            combobox.addItems(selections)
            combobox.currentIndexChanged.connect(self._update_buttons_enable_state)
            self.table.setCellWidget(idx, 0, combobox)
            
        
         
    
    
    def _initCurrentVolTypes(self):
        """
        container_widget = QtWidgets.QWidget()
        container_layout = QtWidgets.QVBoxLayout(container_widget)
        
        for vol_selection in self.current_vol_selections:
            label = QtWidgets.QLabel(vol_selection)
            label.setSelection()
            label.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.ResizeToContents)
            container_layout.addWidget(label)
        """
        
        list_widget = QtWidgets.QListWidget()
        list_widget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        
        def toggle_item(item):
            if item.isSelected():
                if list_widget.selectedItems() == [item]:
                    item.setSelected(False)

        list_widget.itemClicked.connect(toggle_item)
        
        self.table.setCellWidget(0, 1, list_widget)
        for vol_selection in self.current_vol_configs:
            self._addVolSelection(vol_selection)
    
    def _addVolSelection(self, vol_selection):
        QtWidgets.QListWidgetItem(vol_selection, self.table.itemAt(0, 1))
    
    def _initCommandExecution(self):
        self.create_remove = QtWidgets.QWidget()
        self.create_remove.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)

        button_layout = QtWidgets.QHBoxLayout(self.create_remove)
        button_layout.setContentsMargins(0, 0, 0, 0)
        for btn_text in ["Create", "Remove"]:
            button = DynamicClickablePushButton()
            button.setText(btn_text)
            button.clicked.connect(self._update_vol_types)
            button.clicked.connect(self._update_buttons_enable_state)
            for slot in self.slots:
                button.clicked.connect(slot)
            button_layout.addWidget(button)

    def _update_vol_types(self, text):
        if text == "Create":
            vol_config = IVOLMetrics(self.table.cellWidget(0, 0).currentText(), self.table.cellWidget(1, 0).currentText())
            self.current_vol_configs.append(vol_config)
            self.table.cellWidget(0, 0).setCurrentIndex(0), self.table.cellWidget(1, 0).setCurrentIndex(0)
            
        else:
            selected_vol_config = self.table.cellWidget(0, 1).selectedItems()
            for config in selected_vol_config.copy():
                selected_vol_config.remove(config)

    def _update_buttons_enable_state(self, text):
        button_create = self.create_remove.layout().cellWidget(0).widget()
        enable = all([self.table.cellWidget(idx, 0).currentIndex() > 0 for idx in range(2)])
        if enable != button_create.isEnabled():
            button_create.setEnabled(enable)
            
        button_remove = self.create_remove.layout().cellWidget(1).widget()
        enable = len(self.table.cellWidget(0, 1).listWidget().items()) != 0
        if enable != button_create.isEnabled():
            button_remove.setEnabled(enable)




















    def update_selection_state(self, btn_text):
        if btn_text == "Create":
            button = self.create_remove.layout().cellWidget(0).widget()
            if all([self.table.cellWidget(idx, 0).currentIndex() > 0 for idx in range(2)]):
                button.setStyleSheet("")
            else:
                button.setStyleSheet("""
                                     QPushButton:disabled {background-color: #d0d0d0;  
                                     color: #666666;
                                     border: 1px solid #bbbbbb;}
                                     """
                                     )
        elif btn_text == "Remove":
            current_selections = self.table.cellWidget(0, 1).selectedItems()
            if len(current_selections) == 0:
                button.setStyleSheet("""
                                     QPushButton:disabled {background-color: #d0d0d0;  
                                     color: #666666;
                                     border: 1px solid #bbbbbb;}
                                     """
                                     )
            else:
                self.create_remove.layout().cellWidget(0).widget()

        