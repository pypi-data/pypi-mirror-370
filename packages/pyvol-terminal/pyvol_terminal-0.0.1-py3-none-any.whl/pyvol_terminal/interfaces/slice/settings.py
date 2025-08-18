from PySide6 import QtCore, QtGui, QtWidgets
from pyvol_terminal.settings import utils as settings_utils



class Settings(QtWidgets.QWidget):
    def __init__(self, toggle_slots_map, parent=None):
        self.dimension_actions={}
        self.title_axis_dict = {"Money" : "x", "Expiry" : "y", "Volatility" : "z"}

        super().__init__(parent)
        self.create_settings_objects(toggle_slots_map)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        
    def create_settings_objects(self, toggle_slots_map):
        self.setStyleSheet("background-color: white;")
        self.setLayout(QtWidgets.QHBoxLayout(self))
        self.layout().setContentsMargins(0, 0, 0 ,0)
        
        self.prev_button=1         
        
        self.create_change_dimensions_menu("Change Dimensions", toggle_slots_map["Change Dimensions"])
        self.create_toggle_buttons22222("Toggle Price Types", toggle_slots_map["Toggle Price Types"], ["bid", "ask", "mid"])
        
    def create_change_dimensions_menu(self, axis_direction, *arg):
        tool_button = QtWidgets.QToolButton(self)
        tool_button.setText("Change Dimensions")
        tool_button.setStyleSheet(settings_utils.get_settings_stylesheets("QToolButton"))

        tool_button.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        main_menu = QtWidgets.QMenu(self)
        main_menu.setStyleSheet(settings_utils.get_settings_stylesheets("QMenu"))

        def _add_submenu(title, options, axis):
            submenu = QtWidgets.QMenu(title, main_menu)
            main_menu.addMenu(submenu)

            for option in options:
                action = submenu.addAction(option)
                action.triggered.connect(lambda checked=False, o=option: self.widget_data_display.switch_axis(axis, o))
        
        if axis_direction == 0:
            _add_submenu("Money", ["Strike", "Delta", "Moneyness", "Log-Moneyness", "Standardised-Moneyness"], "x")
        else:
            _add_submenu("Expiry", ["Expiry", "Years"], "y")
        
        _add_submenu("Volatility", ["Implied Volatility", "Implied Volatility (%)", "Total Volatility"], "y")

        tool_button.setMenu(main_menu)
        tool_button.setPopupMode(QtWidgets.QToolButton.InstantPopup)

        column_layout = QtWidgets.QVBoxLayout()
        column_layout.addWidget(tool_button)
        self.layout().addLayout(column_layout)
    
    def create_toggle_buttons(self, title, trigger_functions, option_list):
        
        btn_group=QtWidgets.QButtonGroup()
        btn_layout=QtWidgets.QVBoxLayout()
        main_button = QtWidgets.QPushButton(self)
        main_button.setText(title)
        main_button.setStyleSheet(settings_utils.get_settings_stylesheets("QPushButton"))
        main_button.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

        menu = QtWidgets.QMenu(self)
        menu.setStyleSheet(settings_utils.get_settings_stylesheets("QMenu"))

        buttons = []

        for idx, option in enumerate(option_list):
            btn = QtWidgets.QPushButton(option)
            btn.setCheckable(True)
            btn.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
            btn.setStyleSheet(settings_utils.get_settings_stylesheets("QPushButton"))
            buttons.append(btn)
            
            def on_click(btn=btn, opt=option):
                trigger_functions(opt)

            btn.clicked.connect(lambda _, b=btn, opt=option: on_click(b, opt))

            widget_action = QtWidgets.QWidgetAction(menu)
            widget_action.setDefaultWidget(btn)
            menu.addAction(widget_action)

            if option in "mid":
                btn.setChecked(True)
                #trigger_functions(option)

        main_button.clicked.connect(lambda: menu.exec_(main_button.mapToGlobal(QtCore.QPoint(0, main_button.height()))))

        column_layout = QtWidgets.QVBoxLayout()
        column_layout.addWidget(main_button)
        self.layout().addLayout(column_layout)    
             
    def create_toggle_buttons22222(self, title, trigger_functions, option_list):
        
        main_button = QtWidgets.QPushButton(self)
        main_button.setText(title)
        main_button.setStyleSheet(settings_utils.get_settings_stylesheets("QPushButton"))
        main_button.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

        menu = QtWidgets.QMenu(self)
        menu.setStyleSheet(settings_utils.get_settings_stylesheets("QMenu"))

        buttons = []

        for idx, option in enumerate(option_list):
            btn = QtWidgets.QPushButton(option)
            btn.setCheckable(True)
            btn.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
            btn.setStyleSheet(settings_utils.get_settings_stylesheets("QPushButton"))
            buttons.append(btn)
            
            def on_click(btn=btn, opt=option):
                trigger_functions(opt)

            btn.clicked.connect(lambda _, b=btn, opt=option: on_click(b, opt))

            widget_action = QtWidgets.QWidgetAction(menu)
            widget_action.setDefaultWidget(btn)
            menu.addAction(widget_action)

            if option in "mid":
                btn.setChecked(True)
                #trigger_functions(option)

        main_button.clicked.connect(lambda: menu.exec_(main_button.mapToGlobal(QtCore.QPoint(0, main_button.height()))))

        column_layout = QtWidgets.QVBoxLayout()
        column_layout.addWidget(main_button)
        self.layout().addLayout(column_layout)    
             

             

class ToggleButton(QtWidgets.QPushButton):
    def __init__(self, text, value, widget_data_display, parent=None):
        super().__init__(text, parent)
        self.setCheckable(True)
        self.widget_data_display=widget_data_display
        
        #self.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.setStyleSheet("""
                            QPushButton {
                                border: 1px solid #8f8f91;
                                border-radius: 4px;
                                color: black;
                                padding: 5px;
                                background-color: white;
                                text-align: left;
                            }
                            QPushButton:checked {
                                background-color: #0078d7;
                                color: black;
                            }
                            """)
        self.setIconSize(QtCore.QSize(16, 16))
        self.toggled.connect(lambda checked, val=value: self.update_icon(checked, val))

    def update_icon(self, checked, value):
        
        if checked:
            pixmap = QtGui.QPixmap(16, 16)
            pixmap.fill(QtCore.Qt.transparent)
            painter = QtGui.QPainter(pixmap)
            painter.setPen(QtGui.QColor("white"))
            painter.drawLine(4, 8, 7, 12)
            painter.drawLine(7, 12, 12, 4)
            painter.end()
            self.setIcon(QtGui.QIcon(pixmap))
            self.adjustSize()  
            self.widget_data_display.add_line(value)
        else:
            self.setIcon(QtGui.QIcon())
            self.adjustSize()  
            self.widget_data_display.remove_line(value)


class ScrollableToggleButtons(QtWidgets.QWidget):
    def __init__(self, slot, domain_vec, tick_engine):  
        super().__init__()
        self.slot = slot
        self.domain_vec=domain_vec
        self.tick_engine = tick_engine
        self.setLayout(QtWidgets.QVBoxLayout(self))
        self.layout().setAlignment(QtCore.Qt.AlignTop)
        self.create_buttons()
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        
    def create_buttons(self):
        self.button_group = QtWidgets.QButtonGroup() 
        self.button_group.setExclusive(False)
        self.button_layout=QtWidgets.QVBoxLayout()
        
        for idx, value in enumerate(self.domain_vec):
            text = self.tick_engine.function([value])[0]
            
            button = ToggleButton(str(text), value, self.slot)
            

            self.button_group.addButton(button, idx)
            self.layout().addWidget(button)            
                
        self.update_min_width()
        

    def update_min_width(self):
        return 
        max_width = 0
        for btn in self.buttons:
            was_checked = btn.isChecked()
            btn.click()
            btn.updateGeometry()
            width = btn.width()
            if width > max_width:
                max_width = width
            btn.click()
        
        self.setMinimumWidth(max_width)
        self.setFixedWidth(max_width)
