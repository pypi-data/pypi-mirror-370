from PySide6 import QtWidgets
from . import extra_widgets
from . import stylesheets


class Settings(QtWidgets.QWidget):
    def __init__(self, widget_data_display, tick_engine_manager, metric_axis_engine, spot_qlabel=None, parent=None):
        super().__init__(parent)
        self.widget_data_display=widget_data_display
        self.setLayout(QtWidgets.QHBoxLayout(self))
        self.layout().setContentsMargins(0, 0, 0 ,0)
        self.combobox=None

        action_handlers = [tick_engine_manager.change_function, metric_axis_engine.change_function, widget_data_display.data_view.switch_column_metric]
        self.create_moneyness_combobox(["Strike", "Moneyness (%)", "Log-Moneyness", "Standardised-Moneyness", "Delta"], "x", action_handlers)
        self.create_price_type_combobox(["bid", "ask", "mid"], [widget_data_display.data_view.switch_price_type])
        
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        
        if spot_qlabel is not None:
            spot_qlabel.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
            self.layout().addWidget(spot_qlabel)
            
    def create_col_filter(self):
        self.line_edit = QtWidgets.QLineEdit()
        self.line_edit.setText("10")
        self.line_edit.setStyleSheet("""
                                    QLineEdit {
                                        background-color: white;
                                        color: black;
                                    }
                                    QLineEdit:focus {
                                        background-color: #ffffcc;  
                                        border: 2px solid #3366ff;
                                    }
                                    """)
        self.line_edit.editingFinished.connect(self.handle_line_edit)
        self.layout().addWidget(self.line_edit)
    
    def create_moneyness_combobox(self, options, axis_direction, action_handlers):
        combobox = extra_widgets.StrikeOptionsComboBox()
        combobox.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        combobox.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
        combobox.setStyleSheet(stylesheets.get_settings_stylesheets("StrikeOptionsComboBox"))
        combobox.blockSignals(True)
        combobox.addItems(options)
        
        for action_handler in action_handlers:
            combobox.currentTextChanged.connect(lambda text, ax=axis_direction, handler=action_handler: handler(ax, text))
        
        self.layout().addWidget(combobox)
        combobox.blockSignals(False)
        self.combobox=combobox

    def create_price_type_combobox(self, options, action_handlers):
        combobox = extra_widgets.StrikeOptionsComboBox()
        combobox.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        combobox.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
        combobox.setStyleSheet(stylesheets.get_settings_stylesheets("StrikeOptionsComboBox"))
        combobox.blockSignals(True)
        
        combobox.addItems(options)
        
        for action_handler in action_handlers:
            combobox.currentTextChanged.connect(lambda text, handler=action_handler:  handler(text))
        
        self.layout().addWidget(combobox)
        combobox.blockSignals(False)
        self.combobox=combobox

    
    def handle_line_edit(self):
        text = self.line_edit.text()
        try:
            value = int(text)
        except ValueError:
            self.line_edit.setText("10")
            value = 10

        if self.widget_data_display:
            self.widget_data_display.handle_line_edit_value(value)
        else:
            print(f"Line edit value: {value}")

