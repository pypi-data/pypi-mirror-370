from __future__ import annotations 
from typing import List, Optional, Tuple, Union, Dict, TYPE_CHECKING, Callable
if TYPE_CHECKING:
    from instruments.instruments import Option
    from instruments.utils import InstrumentManager
    
from PySide6 import QtWidgets, QtCore, QtGui
import numpy as np
from . import tables, table_builder, extra_widgets, settings
import time
from . import utils as utils_omon
from .tables import OptionTableWidget, StrikeTableColumn
from ..abstract_classes import ABCMainViewQTableWidget

class MainView(ABCMainViewQTableWidget):
    def __init__(self,
                 instrument_manager: InstrumentManager=None,
                 expiry_underlying_map=None,
                 tick_label_engine=None,
                 update_timer=0,
                 queue_interaction=None,
                 metricLabels: List[str]=[],
                 parent=None,
                 **kwargs
                 ):
        super().__init__(parent=parent)
        self.calls_table: OptionTableWidget=None
        self.puts_table: OptionTableWidget=None
        self.options_container=instrument_manager.options_instrument_container
        self.update_timer=update_timer
        self.last_update=time.time()
        self.strike_table_column: StrikeTableColumn=None
        self._subtable_update_callbacks: List[Callable]=[]
        expiry_attributes, total_rows = self.init_expiry_attr()
        
        self.scroll_delay=None
        self.queue_interaction=queue_interaction
        
        if self.queue_interaction:
            self.scroll_delay = 300
            self.scroll_timer = QtCore.QTimer()
            self.scroll_timer.setSingleShot(True)
            self.scroll_timer.timeout.connect(self._scrollFinished)

        self.init_option_tables(instrument_manager, total_rows, expiry_attributes, metricLabels, expiry_underlying_map, tick_label_engine)
        self.init_layout()

    def _internal_update_view(self, *args):
        self.calls_table.update_table()
        self.puts_table.update_table()  
        for callback in self._subtable_update_callbacks:
            callback()
                
    def add_subtable_update_callback(self, callback):
        self._subtable_update_callbacks.append(callback)
        
    def init_expiry_attr(self):
        all_strikes_per_expiry = {expiry : strike_arr for expiry, strike_arr in self.options_container.maps.expiry_strike_map.items()}        
        
        expiry_strike_idx_map = {}
        expiry_idx_map = {}
    
        total_rows=0
        for expiry, strike_arr in all_strikes_per_expiry.items():
            temp_dict = {}
            expiry_idx_map[expiry] = total_rows
            total_rows+=1
            for strike in strike_arr:
                temp_dict[strike] = total_rows
                total_rows+=1
            expiry_strike_idx_map[expiry] = temp_dict
        
        expiry_attributes={}

        for expiry in self.options_container.maps.expiry_strike_map:
            expiry_attribute = utils_omon.ExpiryAttributes(expiry,
                                                           np.array(all_strikes_per_expiry[expiry]),
                                                           np.array(all_strikes_per_expiry[expiry]).size,
                                                           expiry_idx_map[expiry],
                                                           expiry_strike_idx_map[expiry]
                                                           )
            expiry_attributes[expiry] = expiry_attribute
        return expiry_attributes, total_rows

    def init_option_tables(self, instrument_manager, total_rows, expiry_attributes, metric_labels, expiry_underlying_map, tick_label_engine):
        self.strike_table_column = tables.StrikeTableColumn(total_rows, expiry_attributes)   # A QTableWidget object

        table_args = [instrument_manager,
                      metric_labels,
                      expiry_attributes,
                      total_rows,
                      ]

        table_kwargs = {"expiry_underlying_map" : expiry_underlying_map,
                        "tick_label_engine" : tick_label_engine,
                        "parent" : self
                        }
        self.calls_table = tables.OptionTableWidget(*table_args,
                                                    "c",
                                                    **table_kwargs
                                                    )
        self.puts_table = tables.OptionTableWidget(*table_args,
                                                   "p",
                                                   **table_kwargs
                                                   )
        self.strike_table_column.sigRowsUpdated.connect(self._sync_strike_to_options_heights)
        self.strike_table_column.sigRowsUpdated.emit(self.strike_table_column)
        for expiry_attribute in expiry_attributes.values():
            for idx in expiry_attribute.strike_idx_map.values():
                self.strike_table_column.add_row_hidden_callback(self.calls_table.setRowHidden, idx)
                self.strike_table_column.add_row_hidden_callback(self.puts_table.setRowHidden, idx)
        
        for child_table in [self.calls_table, self.puts_table, self.strike_table_column]:
            child_table.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
            child_table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        
        self.link_scrollbars(*[self.calls_table, self.puts_table, self.strike_table_column])
                
        self._link_row_heights(self.strike_table_column,
                               self.calls_table,
                               self.puts_table)
        
        self.calls_table.right_click_menu.setParent(self.parent())
        self.puts_table.right_click_menu.setParent(self.parent())
    
    def match_initial_row_heights(self):
        for i in range(1, self.strike_table_column.rowCount()):
            height = self.strike_table_column.rowHeight(i)
            self.calls_table.setRowHeight(i-1, height)
            self.puts_table.setRowHeight(i-1, height)
    
    def _sync_strike_to_options_heights(self, strike_table):
        for strike_row in range(1, strike_table.rowCount()):
            height = strike_table.rowHeight(strike_row)
            target_row = strike_row - 1  # Adjust for blank row
            self.calls_table.setRowHeight(target_row, height)
            self.puts_table.setRowHeight(target_row, height)    

    def _link_row_heights(self, master, *slaves: Tuple[tables.OptionTableWidget,...]):
        vh = master.verticalHeader()                  
        def _copy_height(logical_row, _old, new):
            for table in slaves:
                table.setRowHeight(logical_row, new)
                
            self.strike_table_column.setRowHeight(logical_row + 1, new)
        vh.sectionResized.connect(_copy_height)
        
        for row in range(master.rowCount()):
            h = master.rowHeight(row)
            for table in slaves:
                table.setRowHeight(row, h)
            self.strike_table_column.setRowHeight(row + 1, h)
                        
    def link_scrollbars(self, *tables):
        for table in tables:
            table.verticalScrollBar().valueChanged.connect(lambda value, current=table: self.sync_scroll(value, current, tables))

    def sync_scroll(self, value, source, tables):
        for table in tables:
            if not table is source:
                table.verticalScrollBar().setValue(value)
        
    def update_spot_text(self):
        pass
        
    def init_layout(self):
        self.setRowCount(1)
        self.setColumnCount(3)
        self.verticalHeader().setVisible(False)
        self.setHorizontalHeaderItem(0, extra_widgets.TableColumnItem("Calls"))
        self.setHorizontalHeaderItem(1, extra_widgets.TableColumnItem("Strike"))
        self.setHorizontalHeaderItem(2, extra_widgets.TableColumnItem("Puts"))
        
        self.setCellWidget(0, 0, self.calls_table)
        self.setCellWidget(0, 1, self.strike_table_column)
        self.setCellWidget(0, 2, self.puts_table)
        
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)  
        self.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Fixed)
        self.setColumnWidth(1, self.strike_table_column.columnWidth(0))

        self.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)        
        self.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        
        
    def wheelEvent(self, ev):
        if self.queue_interaction:
            self._mouseScroll=True
            self._internalCheckIntenseInteraction()
            self.scroll_timer.start(self.scroll_delay)
        return super().wheelEvent(ev)
    
    def _scrollFinished(self):
        self._mouseScroll=False
        self._internalCheckIntenseInteraction()

    def _internalCheckIntenseInteraction(self):
        self.processIntenseInteraction("table", self._mouseScroll)
        
    def setColumns(self, columns):
        pass
    
    def currrentColumns(self):
        return self.calls_table.currrentColumns()