import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6 import QtWidgets
from pyvol_terminal.settings.widgets import WindowSettings, SurfaceSettings
from PySide6.QtCore import Slot



class SettingsManager:
    def __init__(self, widget_main=None, widget_layout_v_main=None):
        self.widget_main=widget_main
        self.settings_main = WindowSettings(self)
        self.settings_surface = SurfaceSettings(widget_main=self.widget_main)
        
        
        widget_layout_v_main.addWidget(self.settings_main)
        widget_layout_v_main.addWidget(self.settings_surface)
        
        widget_layout_v_main.setStretchFactor(self.settings_main, 1)
        widget_layout_v_main.setStretchFactor(self.settings_surface, 1)

    @Slot(QtWidgets.QPushButton)
    def on_button_clicked(self, button):
        btn_id = self.settings_main.button_group.id(button)
        self.widget_main.switch_view(self.settings_main.button_name_maps[btn_id])
        self._reset_hide_viewable_widgets()
        match btn_id:
            case 0:
                self.omon_clicked()
            case 1:
                self.vol_table_clicked()
            case 2:
                self.suface_clicked()
            case 3:
                self.smirk_clicked()
            case 4:
                self.term_clicked()
    
    def omon_clicked(self):
        self.splitter_omon.show()
        self.prev_splitter=self.splitter_omon
        
    def vol_table_clicked(self):
        self.splitter_vol_table.show()
        self.prev_splitter=self.splitter_vol_table
                
    def suface_clicked(self):
        
        self.splitter_surface.show()
        
        self.prev_splitter=self.splitter_surface
        
    def smirk_clicked(self):
        pass

    def term_clicked(self):
        pass
    
    def _reset_hide_viewable_widgets(self):
        self.prev_splitter.hide()


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle('Volatility Surface')
        self.widget_central = QtWidgets.QWidget()
        self.setCentralWidget(self.widget_central)
        
        self.widget_layout_v_main = QtWidgets.QVBoxLayout(self.widget_central)
        self.settings_surface = SettingsManager(self, self.widget_layout_v_main)
        print(self.widget_layout_v_main.stretch(0))
        print(self.widget_layout_v_main.stretch(1))
        print(self.widget_layout_v_main.stretch(2))

        
    def toggle_subplots(self):
        pass
    def toggle_crosshairs(self):
        pass
    
    def toggle_price_type(self):
        pass
    def toggle_3D_objects(self):
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec())
    
