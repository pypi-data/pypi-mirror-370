from __future__ import annotations
from typing import List, Optional, Tuple, Union, Dict, TYPE_CHECKING, Callable
if TYPE_CHECKING:
    from pyvol_terminal.windows import InterfaceWindow
    from ...instruments.utils import InstrumentManager
    from ...instruments.instruments import ABCInstrument, Option
    from .utils import ExpiryAttributes
    
    

from PySide6 import QtWidgets, QtCore, QtGui
import numpy as np
from . import stylesheets as stylesheets, table_builder, extra_widgets, settings
from datetime import datetime
from .extra_widgets import OptionExpiryCellItem, OptionNameCellItem, OptionMetricsWithTabs
from . import extra_widgets
from ...quantities import engines
from . import utils as utils_omon
from .. import custom_widgets
from ...metric_attributes import get_metric_category

class OptionTableWidget(QtWidgets.QTableWidget):
    focusOutSig = QtCore.Signal()
    
    def __init__(self,
                 instrument_manager: InstrumentManager,
                 metricLabels: List[str],
                 expiry_attributes: ExpiryAttributes,
                 n_rows,
                 option_type,
                 expiry_underlying_map=None,
                 tick_label_engine=None,
                 **kwargs
                 ):
        super().__init__(**kwargs)
        self.options_container: Dict[str, Option]=instrument_manager.options_instrument_container.objects
        self.options_maps = instrument_manager.options_instrument_container.maps
        self.name=option_type
        self._right_clicked=False
        self.metrics = [metric.lower() for metric in metricLabels]
        self.expiry_attributes: Dict[float, ExpiryAttributes] = expiry_attributes
        self.option_type=option_type
        self.visible_instruments: List[str]=[]
        self.subtable_instruments: Dict[str, List[QtWidgets.QTableWidget]]={}
        self.subtable_widget_container: List[extra_widgets.OptionMetricsWithTabs]=[]
        self.idx_instrument_map={}
        self.right_click_menu = extra_widgets.RightClickMenu(parent=self)
        self.expiry_underlying_map: Dict[float, ABCInstrument]=expiry_underlying_map
        self._expiry_cells: set = set()
        self._cell_expiry_map: Dict[int, float] = {}
        
        self.focusOutSig.connect(self.clearSelection)
        self.focusOutSig.connect(self.right_click_menu.close)
        
        if tick_label_engine is None:
            self.tick_label_engine = engines.TickEngineManager("Strike", "Expiry", "Implied Volatility")
        
        column_labels = ['Instrument Name'] + metricLabels        
        
        self.block_update=False
        self.last_values={ticker : {metric : None for metric in self.metrics} for ticker in self.options_container}
        
        self.initTableDimensions(n_rows, column_labels)        
        self.initTableContents()
        self.initTableStyle()
        self.initTableLayout()
    
    def add_expiry_underlying_map(self, expiry_underlying_map):
        self.expiry_underlying_map=expiry_underlying_map
        self.update_expiry_cell_item=True
    
    def initTableLayout(self):        
        for jdx in range(self.columnCount()):
            if jdx == 0:
                self.horizontalHeader().setSectionResizeMode(jdx, QtWidgets.QHeaderView.Stretch)  
            else:
                self.horizontalHeader().setSectionResizeMode(jdx, QtWidgets.QHeaderView.ResizeToContents)
                
        self.autoFillBackground()
        self.horizontalHeader().setHighlightSections(False)
        self.horizontalHeader().setSectionsMovable(False)
        self.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        
        expiry_cells=[]
        self._cell_expiry_map={}
        for expiry_attribute in self.expiry_attributes.values():
            expiry_cells.append(expiry_attribute.expiry_idx)
            self._cell_expiry_map[expiry_attribute.expiry_idx] = expiry_attribute.expiry
        
        self._expiry_cells = set(expiry_cells)
        
    def currentColumns(self):
        return [self.horizontalHeaderItem(c).text() for c in range(self.columnCount())]

    def initTableDimensions(self, n_rows, column_labels):
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setVisible(True)
        
        self.setRowCount(n_rows)
        self.setColumnCount(len(column_labels))
        
        for idx, col in enumerate(column_labels):
            col_item = extra_widgets.TableColumnItem(col)
            if idx == 0:
                col_item.setTextAlignment(QtCore.Qt.AlignLeft)
                font = QtGui.QFont("Neue Haas Grotesk", 12)
                col_item.setFont(font)
            self.setHorizontalHeaderItem(idx, col_item)
    
    def initTableStyle(self):
        self.setShowGrid(True)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        
        self.setItemDelegate(extra_widgets.CustomDelegate(self))
        self.setStyleSheet(stylesheets.get_settings_stylesheets("QTableWidget"))   
        self.horizontalHeader().setSectionsClickable(True)   
        
        self.itemSelectionChanged.connect(self._select_subtable)    
                
    def initTableContents(self):
        table_widget_items=[]
        self.exp_container = extra_widgets.CellItemContainer()
        for expiry, expiry_attribute in self.expiry_attributes.items():
            instrument_names = list(self.options_maps.type_expiry_strike_instrument_map[self.option_type][expiry].values())

            for strike, ticker in self.options_maps.type_expiry_strike_instrument_map[self.option_type][expiry].items():
                self.idx_instrument_map[expiry_attribute.strike_idx_map[strike]] = ticker

            table_widget_items = table_builder.create_expiry_section(expiry,
                                                                    expiry_attribute.strikes, 
                                                                    instrument_names, 
                                                                    self.metrics,
                                                                    expiry_attribute.expiry_idx
                                                                    )     
            self.exp_container.addItem(table_widget_items[0]["item"]) 
            for table_widget_item_dict in table_widget_items:
                pos, item = table_widget_item_dict["pos"], table_widget_item_dict["item"]
                self.setItem(*pos, item)
                if pos[0] == expiry_attribute.expiry_idx:
                    self.setRowHidden(pos[0], False)
                else:
                    self.setRowHidden(pos[0], True)
                
    def check_text_width(self, table_widget_items: List[Dict[str, Tuple|OptionExpiryCellItem]]):
        shrink_text={}
        for table_widget_item_dict in table_widget_items:
            item = table_widget_item_dict["item"]
            t = type(item)
            if isinstance(t, (OptionExpiryCellItem, OptionNameCellItem)):
                if not t in shrink_text:
                    shrink_text[t] = False
                if item.does_text_fit():
                    shrink_text[t] = True
        for table_widget_item_dict in table_widget_items:
            item = table_widget_item_dict["item"]
            t = type(item)
            if t in shrink_text:
                if shrink_text[t]:
                    new_pointSize=item.font().pointSize()-1
                    item.font().setPointSize(new_pointSize)

    def setRowHidden(self, row, hide):
        if hide:
            if row in self.idx_instrument_map:
                ticker = self.idx_instrument_map[row]
                if ticker in self.visible_instruments:
                    self.visible_instruments.remove(ticker)
        else:
            if row in self.idx_instrument_map:
                ticker = self.idx_instrument_map[row]
                if not ticker in self.visible_instruments:
                    self.visible_instruments.append(ticker)
        return super().setRowHidden(row, hide)
    
    def updateFromOption(self, option_object: Option):
        exp = option_object.expiry
        expiry_attr_dataclass = self.expiry_attributes[exp]
        idx = expiry_attr_dataclass.strike_idx_map[option_object.strike]
        
        for jdx, metric in enumerate(self.metrics, start=1):
            value = getattr(option_object, metric)
            if value == self.last_values[option_object.ticker][metric]:
                continue
            else:
                self.last_values[option_object.ticker][metric]=value
            
            text_item = self.item(idx, jdx)
            
            if get_metric_category(metric) == "volatility":     
                if value == value:            
                    if not option_object.OTM:
                        value_str = f"{(np.round(value, 2))}*"
                    else:
                        value_str = str(np.round(value, 2))
                else:
                    continue
            else:
                value_str = f"{value:,.2f}"
            text_item.setText(value_str)  

    def _internalTableUpdate(self, table: OptionMetricsWithTabs, instrument_names: List[str]):
        for ticker in instrument_names:
            option_object=self.options_container[ticker]
            table.updateFromOption(option_object)
    
    def update_table(self):
        if not self.block_update:
            self.setItemDelegate(None)
            self._internalTableUpdate(self, self.visible_instruments)
                
            if not self.expiry_underlying_map is None:
                for expiry, expiry_attr in self.expiry_attributes.items():
                    underlying_object = self.expiry_underlying_map[expiry]
                    idx = expiry_attr.expiry_idx
                    text_item = self.item(idx, 0)
                    text_item.update_from_base(underlying_object.mid)
            
            for table_widget in self.subtable_widget_container:
                self._internalTableUpdate(table_widget, table_widget.instrument_names)
            self.setItemDelegate(extra_widgets.CustomDelegate(self))  
                
    def _select_subtable(self):
        selected_items = self.selectedItems()
        if not selected_items:
            return
        self.blockSignals(True)
        for item in selected_items:
            row, col = item.row(), item.column()
            if row in self._expiry_cells:
                expiry = self._cell_expiry_map[row]
                expiry_attr = self.expiry_attributes[expiry]
                
                if col == 0:
                    for j in range(self.columnCount()):
                        self.item(row, j).setSelected(True)
                    for strike_row in expiry_attr.strike_idx_map.values():
                        if not self.isRowHidden(strike_row):
                            for j in range(self.columnCount()):
                                if self.item(strike_row, j):
                                    self.item(strike_row, j).setSelected(True)
                else:
                    for strike_row in expiry_attr.strike_idx_map.values():
                        if not self.isRowHidden(strike_row) and self.item(strike_row, col):
                            self.item(strike_row, col).setSelected(True)
            else:
                if col == 0:
                    for j in range(self.columnCount()):
                        if self.item(row, j):
                            self.item(row, j).setSelected(True)
        
        self.blockSignals(False)

    def reset_right_click_flag(self):
        self._right_clicked = False
        
    def mouseMoveEvent(self, event):
        if event.buttons() & QtCore.Qt.LeftButton:
            if self.right_click_menu.isVisible():
                self.right_click_menu.hide()
        super().mouseMoveEvent(event)
    
    def focusOutEvent(self, event):
        self.focusOutSig.emit()
        return super().focusOutEvent(event)
    
    def keyPressEvent(self, event: QtGui.QKeyEvent):
        if event.key() == QtGui.Qt.Key_Escape and event.modifiers() == QtGui.Qt.NoModifier:
            self.focusOutSig.emit()
        return super().keyPressEvent(event)
            
    def mousePressEvent(self, event: QtGui.QMouseEvent):
        if event.button() == QtCore.Qt.LeftButton:
            self._right_clicked = False
            super().mousePressEvent(event)
        
        if event.button() == QtCore.Qt.RightButton:
            self._right_clicked = True
            rows = [item.row() for item in self.selectedItems()]
            cols = [item.column() for item in self.selectedItems()]
            name_metric_map={}
            for row, col in zip(rows, cols):
                if 0 < col < 1 + len(self.metrics):
                    if row in self._expiry_cells:
                        continue
                    ticker = self.idx_instrument_map[row]
                    selected_column = self.currentColumns()[col]
                    if get_metric_category(selected_column.lower()) == "price":
                        
                    
                        if not ticker in name_metric_map:
                            inner_dict = {"object" : self.options_container[ticker],
                                          "selectedPriceTypes" : {"label" : [selected_column],
                                                                  "attribute" : [selected_column.lower()]}
                                        }
                            name_metric_map[ticker] = inner_dict
                        else:
                            name_metric_map[ticker]["selectedPriceTypes"]["label"].append(selected_column)
                            name_metric_map[ticker]["selectedPriceTypes"]["attribute"].append(selected_column.lower())

            if len(name_metric_map) > 0:
                self.right_click_menu.popup(event.globalPos(), name_metric_map, self) 
                
        super().mousePressEvent(event) 
    
    @QtCore.Slot(QtCore.QPoint, dict)
    def create_subtable(self, q_point, name_metric_map):
        app = QtWidgets.QApplication.instance()
    
        getattr_map = {"ivol" : "get_ivol",
                       "delta" : "get_delta",
                       "gamma" : "get_gamma",
                       "vega" : "get_vega",
                       "theta" : "get_theta",
                       "rho" : "get_rho",
                       }

        metric_table = extra_widgets.OptionMetricsWithTabs(name_metric_map=name_metric_map, getattr_map=getattr_map, parent=self)        
        geomtry = QtCore.QRect(int(q_point.x()), int(q_point.y()), int(metric_table.width()), int(metric_table.height()))
        self.subtable_widget_container.append(metric_table)
        metric_table.show()
        #################app.open_sub_window(metric_table, geomtry, True, parent=self)
        
    @QtCore.Slot()
    def closingSubtle(self, table):
        self.subtable_widget_container.remove(table)
        

class StrikeTableColumn(QtWidgets.QTableWidget):
    sigRowsUpdated = QtCore.Signal(object)
    def __init__(self,
                 n_rows: int,
                 expiry_attributes: Dict[str, ExpiryAttributes]
                 ):
        super().__init__()
        self.name="strike"
        self.expiry_attributes=expiry_attributes
        self.comboboxes: List[extra_widgets.StrikeOptionsComboBox]=[]
        self.current_expiry_strike_map={expiry : [] for expiry in self.expiry_attributes}
        self.strike_center=None
        self.row_hidden_callbacks={idx : [] for idx in range(n_rows)}
        self.max_width=0
        self.init_layout(n_rows)
        self.setStyleSheet(stylesheets.get_settings_stylesheets("QTableWidget"))
        self.autoFillBackground()
        
    def init_layout(self, n_rows):
        self.setColumnCount(1)
        self.setRowCount(n_rows)

        for expiry_attribute in self.expiry_attributes.values():
            select_strikes_combobox = extra_widgets.StrikeOptionsComboBox()
            select_strikes_combobox.addItem(str(0))

            self.setCellWidget(expiry_attribute.expiry_idx, 0, select_strikes_combobox)
            
            select_strikes_combobox.blockSignals(True)
            select_strikes_combobox.setCurrentText(str(0))    
            select_strikes_combobox.currentTextChanged.connect(lambda selected_text, exp_attr=expiry_attribute: self.update_strikes(selected_text, exp_attr))
            select_strikes_combobox.blockSignals(False)
            self.comboboxes.append(select_strikes_combobox)
            for idx, strike in enumerate(expiry_attribute.strikes, start=1):
                text_widget_item = extra_widgets.StrikeCellItem(str(strike))
                select_strikes_combobox.addItem(str(idx))
                self.setItem(expiry_attribute.strike_idx_map[strike], 0, text_widget_item)
                
        for idx in range(self.rowCount()):
            self.setRowHidden(idx, False)
        self.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        self.max_width = self.columnWidth(0)
        for idx in range(self.rowCount()):
               self.setRowHidden(idx, True)
        for expiry_attribute in self.expiry_attributes.values():
            self.setRowHidden(expiry_attribute.expiry_idx, False)
                    
        self.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Fixed)
        self.columnWidth(self.max_width)

        self.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.horizontalHeader().setVisible(True)
        self.setHorizontalHeaderItem(0, extra_widgets.TableColumnItem(""))
        self.verticalHeader().setVisible(False)
        
    def add_row_hidden_callback(self, callback, idx):
        self.row_hidden_callbacks[idx].append(callback)

    def setRowHidden(self, idx, hide_flag):
        super().setRowHidden(idx, hide_flag)
        if idx in self.row_hidden_callbacks:
            for callback in self.row_hidden_callbacks[idx]:
                callback(idx, hide_flag)
        self.sigRowsUpdated.emit(self)
    
    def set_strikes(self, new_n_strikes, expiry_attribute):
        old_strikes = self.current_expiry_strike_map[expiry_attribute.expiry]
        new_strikes, _, _  = utils_omon.get_closest_n_strikes(self.strike_center, expiry_attribute.strikes, new_n_strikes)
        self.current_expiry_strike_map[expiry_attribute.expiry] = new_strikes

        if len(new_strikes) > len(old_strikes):
            strikes_to_change = [strike for strike in new_strikes if not strike in old_strikes]
            self.update_table_rows(expiry_attribute, strikes_to_change, False)
        elif len(new_strikes) == len(old_strikes):
            strikes_to_add = [strike for strike in new_strikes if not strike in old_strikes]
            self.update_table_rows(expiry_attribute, strikes_to_add, False)
            strikes_to_remove = [strike for strike in old_strikes if not strike in new_strikes]
            self.update_table_rows(expiry_attribute, strikes_to_remove, True)
        else:
            strikes_to_change = [strike for strike in old_strikes if not strike in new_strikes]
            self.update_table_rows(expiry_attribute, strikes_to_change, True)

    def update_strikes(self, new_n_strikes, expiry_attribute):
        new_n_strikes = int(float(new_n_strikes))
        if new_n_strikes == len(self.current_expiry_strike_map[expiry_attribute.expiry]):
            return
        else:
            self.set_strikes(new_n_strikes, expiry_attribute)

    def update_table_rows(self, expiry_attribute: ExpiryAttributes, strikes_to_change: List[float], hide_flag: bool):
        for strike in strikes_to_change:
            idx = expiry_attribute.strike_idx_map[strike]
            self.setRowHidden(idx, hide_flag)

    def change_center(self, center):
        self.strike_center = float(center)
        for expiry, expiry_attribute in self.expiry_attributes.items():
            if len(self.current_expiry_strike_map[expiry]) == 0:
                continue
            else:
                self.set_strikes(len(self.current_expiry_strike_map[expiry]), expiry_attribute)
                
    def bulk_change_strike_num(self, new_n_strike):
        for combobox in self.comboboxes:
            if new_n_strike > combobox.maxCount():
                combobox.setCurrentIndex(combobox.maxCount() - 1)
            else:
                combobox.setCurrentText(str(new_n_strike))

