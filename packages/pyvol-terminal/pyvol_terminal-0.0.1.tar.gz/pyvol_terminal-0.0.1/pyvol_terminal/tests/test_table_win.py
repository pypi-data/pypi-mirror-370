from PySide6 import QtWidgets, QtCore, QtGui
import sys
import numpy as np

class OptionMetricCellItem(QtWidgets.QTableWidgetItem):
    def __init__(self, text=""):
        super().__init__(text)
        self.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        self.setBackground(QtGui.QColor("black"))
        self.setForeground(QtGui.QColor("white"))
        self.setTextAlignment(QtCore.Qt.AlignRight)

class OptionMetrics(QtWidgets.QTableWidget):
    def __init__(self, instrument_name, ins_ob, price_types, parent=None):
        super().__init__(parent)
        self.instrument_name = instrument_name
        self.price_types = price_types
        self.popped=False
        
        
        self.setRowCount(2)
        self.setColumnCount(2)
        
        self.setHorizontalHeaderLabels(price_types)
        self.setVerticalHeaderLabels([instrument_name, "Value"])
        counter=0
        for i in range(2):
            for j in range(2):
                value = ins_ob.values[counter]
                counter+=1
                self.setItem(i, j, OptionMetricCellItem(f"{value:.2f}"))
    def set_on_view(self, flag):
        self._on_view=flag
        
    def update(self, item):
        
        if self._on_view:
            counter=0
            for i in range(2):
                for j in range(2):
                    value = item.values[counter]
                    counter+=1
                    cell_item = self.item(i,j)
                    cell_item.setText(f"{value:.2f}")

    
    
class OptionMetricsWithTabs(QtWidgets.QWidget):
    def __init__(self, instruments, instrument_container, parent=None):
        super().__init__(parent)
        self.name_tab_idx_map={}
        self.instruments=instruments
        
        self.setup_ui(instrument_container)
        
    def _popout_table(self, pos, button):
        instrument_name = button.text()
        idx = self.name_tab_idx_map[instrument_name]
        table = self.stack.itemAt(idx).widget()
        table.set_on_view(True)
        
        app = QtWidgets.QApplication.instance()
        table.popped=True
        
        self.button_layout.removeWidget(button)
        button.deleteLater()  
        del self.name_tab_idx_map[instrument_name]
        self.button_group.removeButton(button)
        
            
        for name, i in list(self.name_tab_idx_map.items()):
            if idx < i:
                button = self.button_group.buttons()[i-1]
                new_i = self.name_tab_idx_map[name] - 1
                self.button_group.setId(button, new_i)
                self.name_tab_idx_map[name]=new_i
 
        self.stack.removeWidget(table)
        table.show()
        app.open_sub_window(pos, table)

        for col in range(table.columnCount()):
            for row in range(table.rowCount()):
                item = table.item(row, col)
                print(f"\n{item.text()}")
        
    def _open_button_context(self, pos):
        button = self.sender()
        
        menu = QtWidgets.QMenu(self)
        
        print_action = menu.addAction("Open in New Window")
        print_action.triggered.connect(lambda: self._popout_table([pos.x(), pos.y()], button))
        menu.exec(button.mapToGlobal(pos))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.adjust_button_layout()
        
    def adjust_button_layout(self):
        if not hasattr(self, 'button_group') or not self.button_group.buttons():
            return
        
        table = self.stack.currentWidget()
        for btn in self.button_group.buttons():
            btn.hide()
        table.adjustSize()
        available_width = table.sizeHint().width()
        
        
        test_button = self.button_group.buttons()[0]
        button_width = test_button.sizeHint().width()

        print(f"button_width: {button_width}")
        print(f"available_width: {available_width}")
        print(f"test_button.size().width(): {test_button.size().width()}")
        spacing = self.button_layout.spacing()
        
        total_button_width = button_width + spacing
        for btn in self.button_group.buttons():
            btn.show()

        
        
        max_buttons = max(1, int(available_width / total_button_width))
        
        current_buttons_per_row = self.button_layout.count()
        
        if max_buttons != current_buttons_per_row:
            self.rearrange_buttons(max_buttons)
            
    def rearrange_buttons(self, buttons_per_row):
        while self.button_layout.count():
            item = self.button_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
        
        grid_layout = QtWidgets.QGridLayout()
        grid_layout.setSpacing(self.button_layout.spacing())
        
        buttons = self.button_group.buttons()
        for i, button in enumerate(buttons):
            row = i // buttons_per_row
            col = i % buttons_per_row
            grid_layout.addWidget(button, row, col)
        
        self.main_layout.removeItem(self.button_layout)
        self.button_layout = grid_layout
        self.main_layout.insertLayout(0, self.button_layout)
        self.button_layout.setSpacing(0)

        
    def setup_ui(self, instrument_container):
        self.main_layout=QtWidgets.QVBoxLayout(self)
        self.setLayout(self.main_layout)
        
        self.button_group = QtWidgets.QButtonGroup()
        self.button_layout = QtWidgets.QHBoxLayout()
        
        for i, (name, _) in enumerate(self.instruments.items()):
            self.name_tab_idx_map[name]=i
            btn = QtWidgets.QPushButton(name)
            btn.setCheckable(True)
            btn.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)  
            btn.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
            btn.customContextMenuRequested.connect(self._open_button_context)
            self.button_group.addButton(btn, i)
            self.button_layout.addWidget(btn)
        
        self.stack = QtWidgets.QStackedLayout()
        for ins_ob in instrument_container:
            name = ins_ob.instrument_name
            data = self.instruments[name]

            table = OptionMetrics(name, ins_ob, data["price_types"])
            print(f"table: {table}")
            ins_ob.add_callback(table.update)
            table.set_on_view(False)
            instrument_container
            self.stack.addWidget(table)
            self.stack.currentWidget().width()
    
        self.button_group.idClicked.connect(self.stack.setCurrentIndex)
        
        
        
        self.main_layout.addLayout(self.stack)
        
        
        if self.button_group.buttons():
            self.button_group.buttons()[0].setChecked(True)
        
        self.stack.itemAt(0).widget().set_on_view(True)
        self.subwindow_width = self.stack.itemAt(0).widget().width()
        self.main_layout.insertLayout(0, self.button_layout)


window_container=[]

class Application(QtWidgets.QApplication):
    create_window_signal = QtCore.Signal(dict, str, tuple)
    window_titles_signal = QtCore.Signal(list)
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def get_instance(cls):
        return cls._instance
    
    def __init__(self,
                 argv
                 ):
        super().__init__(argv)
        
    def open_main_window(self):
        for i in range(1, 9999):
            window_title = f"Main Window {i}"
        win = QtWidgets.QMainWindow()

        window_container.append(win)
        win.showMaximized()
    
    def open_sub_window(self, geometry, widget):
        for i in range(1, 9999):
            window_title = f"Sub Window {i}"
        win = SubWindow(geometry, widget)
        window_container.append(win)

class SubWindow(QtWidgets.QMainWindow):
    def __init__(self, geometry, widget):
        super().__init__()
        self.widget_main = widget
        self.setCentralWidget(self.widget_main)
        
        self.layout_main = QtWidgets.QVBoxLayout(self.widget_main)
        self.setLayout(self.layout_main)
        frame = self.frameGeometry()
        frame_size = frame.size()
        widget_size = self.widget_main.sizeHint()
        
        width_diff = frame_size.width() - self.centralWidget().sizeHint().width()
        height_diff = frame_size.height() - self.centralWidget().sizeHint().height()
        
        self.resize(widget_size.width() + width_diff, 
                    widget_size.height() + height_diff)
        
        self.move(geometry[0], geometry[1])
        self.show()       
        
        

            
        
class Updater(QtCore.QThread):
    def __init__(self, instruments):
        self.instruments=instruments
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(1000)

    def update(self):
        for instrument in self.instruments:
            instrument.update()
             

class InsObj:
    def __init__(self, instrument_name, S_0):
        self.instrument_name=instrument_name
        self.S_0=S_0
        self.values = self.S_0 + np.random.normal(0, 0.3, size=4)
        self.callbacks=[]
        
    def add_callback(self, callback):
        self.callbacks.append(callback)
    
    def update(self):
        self.values = self.values + np.random.normal(0, .3, size=4)
        for c in self.callbacks:
            c(self)
        
if __name__ == "__main__":
    app = Application(sys.argv)
    
    window = QtWidgets.QMainWindow()
    instruments = {
            "BTC-25JUN-70000-C": {
                "object": None,  
                "price_types": ["Bid", "Ask"]
            },
            "BTC-25JUN-75000-C": {
                "object": None,
                "price_types": ["Mid", "Mark"]
            },
            "BTC-25JUN-80000-C": {
                "object": None,
                "price_types": ["Bid", "Ask"]
            }
        }

    
    S_0 = 10
    K = [70000 + i*5000 for i in range(1,8)]
    instrument_container=[]
    instruments={}
    for i in range(1, 8):
        k = K[i-1]
        instruments[f"BTC-25JUN-{k}-C"] = {"object": None,
                                            "price_types": ["Bid", "Ask"]}
        S_0 = S_0 + 10 
        
        o = InsObj(f"BTC-25JUN-{k}-C", S_0)
        instrument_container.append(o)
    
    workers = Updater(instrument_container)
    
    central_widget = OptionMetricsWithTabs(instruments, instrument_container)
    window.setCentralWidget(central_widget)
    window.resize(400, 300)
    window.show()
    
    sys.exit(app.exec())