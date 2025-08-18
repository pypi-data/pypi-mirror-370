from __future__ import annotations 
from typing import List, Optional, Tuple, Union, Dict, TYPE_CHECKING, Callable, Any
if TYPE_CHECKING:
    from instruments.instruments import Option, ABCInstrument, Derivative
    from instruments.utils import InstrumentManager
    from ..data_classes.classes import Slice
    
import pyqtgraph as pg
import numpy as np
from PySide6 import QtCore, QtWidgets, QtGui
from .option_monitor import extra_widgets, stylesheets as utils_omon


class CustomTextItem(pg.TextItem):
    def __init__(self, text=None, view_box_anchor=None, **kwargs):
        self.view_box_anchor=view_box_anchor
        if self.view_box_anchor[0] == 0:
            self.use_vb_xmin=True
        else:
            self.use_vb_xmin=False
        if self.view_box_anchor[1] == 0:
            self.use_vb_ymin=False
        else:
            self.use_vb_ymin=True

        super().__init__(text=text, **kwargs)
        self.p=[self.pos()[0], self.pos()[1]]
    
    def attach_viewbox(self, vb: pg.ViewBox):
        self.vb=vb
        self.vb.sigResized.connect(self.view_box_resize)
        self.vb.sigRangeChanged.connect(self.view_box_resize)
        self.vb.sigRangeChangedManually.connect(self.view_box_resize)


    def right_click(self, *args):
        if not self.isVisible():
            super().show()
    
    def view_box_resize(self, args):
        if not self.view_box_anchor is None:
            vb_range = self.vb.viewRange()
            if self.use_vb_xmin:
                self.p[0] = vb_range[0][0]
            else:
                self.p[0] = vb_range[0][1]
            if self.use_vb_ymin:
                self.p[1] = vb_range[1][0]
            else:
                self.p[1] = vb_range[1][1]
            super().setPos(*self.p)

class CustomPlotDataItem(pg.PlotDataItem):
    def __init__(self, px_type, *args, **kwargs):
        self.px_type=px_type  
        super().__init__(*args, **kwargs)
    
    def update_from_dataclass(self, dclass: Slice):
        self.setData(**dclass.plot_item_kwargs())
    

class OptionInfoTable(QtWidgets.QWidget):
    def __init__(self, name_metric_map, getattr_map, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.getattr_map=getattr_map
        self.price_types=name_metric_map["price_types"]    
        self.cellitem_container={}
        self._on_view=True
        self._initLayout()
        self._initTables(name_metric_map, getattr_map)
        
    def _initLayout(self):
        self.setLayout(QtWidgets.QVBoxLayout())

    """
    def _initTables(self, name_metric_map, getattr_map):
        self.name_table = NameTable(name_metric_map["object"].ticker,
                                    name_metric_map["object"].underlying_px)
        
        self.metric_table = MetricTable(name_metric_map, getattr_map)
        self.layout().addWidget(self.name_table)
        self.layout().addWidget(self.metric_table)
        
        self.autoFillBackground()
        self.pop_table=False
        self.metric_table.verticalHeader().sectionResized.connect(self.update_vertical_dims)
        self.name_table.horizontalHeader().sectionResized.connect(self.update_horizontal_dims)
        self.showEvent = self.on_show_event
    """
    def update_horizontal_dims(self, *args):
        self.name_table.horizontalHeader().setFixedWidth(self.metric_table.horizontalHeader().width())
        
    def update_vertical_dims(self, *args):
        self.metric_table.verticalHeader().setFixedWidth(self.metric_table.verticalHeader().width())
        

    def on_show_event(self, event):
        self.name_table.verticalHeader().resizeSections(QtWidgets.QHeaderView.ResizeMode.ResizeToContents) 
        self.update_vertical_dims(0, 0, 0) 
        super().showEvent(event)


class MetricTable(QtWidgets.QTableWidget):
    def __init__(self, name_metric_map, getattr_map, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.getattr_map=getattr_map
        self.price_types=name_metric_map["price_types"]    
        self.nrows = 1 + len(self.getattr_map)
        self.ncols=len(self.price_types)
        self.cellitem_container={}
        self._on_view=True
        self._underlying_object = name_metric_map["object"]
        self._initTableDimensions()
        self._initCellItems(name_metric_map["object"])
        self.autoFillBackground()
        self.setShowGrid(False)
        self.pop_table=False
        
    def set_on_view(self, flag):
        self._on_view=flag
        
    def _initTableDimensions(self):
        self.verticalHeader().setVisible(True)
        self.horizontalHeader().setVisible(True)
        self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        self.setStyleSheet(utils_omon.get_settings_stylesheets("SubQTableWidget"))   
        
        self.setRowCount(self.nrows)
        self.setColumnCount(self.ncols)        
        
        for jdx, px_type in enumerate(self.price_types):
            col_name_item = extra_widgets.TableColumnItem(px_type)
            font = QtGui.QFont("Neue Haas Grotesk", 12)
            col_name_item.setFont(font)
            self.setHorizontalHeaderItem(jdx, col_name_item)

        underlying_label = extra_widgets.TableColumnItem("underlying_px")
        underlying_label.setTextAlignment(QtCore.Qt.AlignLeft)
        font = QtGui.QFont("Neue Haas Grotesk", 12)
        underlying_label.setFont(font)
        self.setVerticalHeaderItem(0, underlying_label)
        if self.columnCount() > 1:
            self.setSpan(0, 0, 1, self.columnCount())
        
        for idx, name in enumerate(self.getattr_map, start=1):
            row_name_item = extra_widgets.TableColumnItem(name)
            row_name_item.setTextAlignment(QtCore.Qt.AlignLeft)
            row_name_item.setFont(font)
            self.setVerticalHeaderItem(idx, row_name_item)

    def _initCellItems(self, instrument_object: ABCInstrument):
        if hasattr(instrument_object, "underlying_px"):
            value = instrument_object.underlying_px
            
            cell_item = extra_widgets.OptionMetricCellItem(f"{value:,.2f}")
            cell_item.setTextAlignment(QtCore.Qt.AlignLeft)
            self.cellitem_container["underlying_px"]=cell_item
            self.setItem(0, 0, cell_item)
            start_idx=1
        else:
            start_idx=0

        for jdx, px_type in enumerate(self.price_types):
            for idx, (name, call) in enumerate(self.getattr_map.items(), start=start_idx):
                value = getattr(instrument_object, call)(px_type)
                if name in ["delta", "gamma"]:
                    val_str=f"{value:,.2g}"
                else:
                    val_str=f"{value:,.2f}"
                cell_item = extra_widgets.OptionMetricCellItem(val_str)
                self.cellitem_container[name]=cell_item
                self.setItem(idx, jdx, cell_item)
    
    def update_view(self):
        self.update_table(self._underlying_object)
    
    def update_table(self, instrument_object: Derivative):
        if self._on_view:
            name = "underlying_px"
            cell_item = self.item(0, 0)
            cell_item.setText(f"{instrument_object.underlying_px:,.2f}")
            for jdx, px_type in enumerate(self.price_types):
                for idx, (name, call) in enumerate(self.getattr_map.items(), start=1):
                    value = getattr(instrument_object, call)(px_type)
                    if name in ["delta", "gamma"]:
                        val_str=f"{value:,.2g}"
                    else:
                        val_str=f"{value:,.2f}"
                    cell_item = self.item(idx, jdx)
                    cell_item.setText(val_str)


class OptionMetricsWithTabs(QtWidgets.QWidget):
    def __init__(self, name_metric_map, getattr_map, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.getattr_map=getattr_map
        self.instrument_names=list(name_metric_map.keys())
        self.nrows = 2 + len(self.getattr_map)
        self.metric_name_cellitem_map={}
        self.name_tab_idx_map={}
        self.buttons=[]
        self._initLayout()
        self._initTabs(name_metric_map)
        self._initTableDimensions(name_metric_map)
        self._initCellItems(name_metric_map)
        self.autoFillBackground()
        btn = self.button_group.button(0)
        btn.click()
        
    def _initLayout(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)
        self.button_group = QtWidgets.QButtonGroup()
        self.table_stack = QtWidgets.QStackedLayout()
        
        self.button_layout = QtWidgets.QHBoxLayout()
        self.button_layout.setContentsMargins(0, 0, 0, 0)
        
        self.main_layout.addLayout(self.button_layout)
        self.main_layout.addLayout(self.table_stack)
        
        self.main_layout.setStretch(0, 0)  # Buttons don't stretch vertically
        self.main_layout.setStretch(1, 1)  # Table g     
    

    def _initTabs(self, metric_object_container):
        for idx, name in enumerate(metric_object_container):
            slot=lambda idx, checked: (self.table_stack.setCurrentIndex(idx),
                                       setattr(self.table_stack.itemAt(idx).widget(), "_on_view", True)) if checked \
                                        else setattr(self.table_stack.itemAt(idx).widget(), "_on_view", False)
            
            btn=QtWidgets.QPushButton(name)
            btn.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            btn.setSizePolicy(QtWidgets.QSizePolicy.Expanding, 
                              QtWidgets.QSizePolicy.Fixed)
                        
            if len(metric_object_container) > 1:
                btn.customContextMenuRequested.connect(self._open_button_context)
            
            btn.setCheckable(True)
            btn.setChecked(False)
            self.buttons.append(btn)
            
            self.button_layout.addWidget(btn)
            #self.button_layout.addWidget(btn, stretch=1)  
            self.button_group.addButton(btn, id=idx) 
            self.button_group.idToggled.connect(slot)
            self.name_tab_idx_map[name]=idx
        self.button_layout.addStretch()
            
    def _popout_table(self, pos, button):
        ticker = button.text()
        table = self.table_stack.itemAt(self.name_tab_idx_map[ticker]).widget()
        table.set_on_view(True)
        idx = self.name_tab_idx_map[ticker]
        
        app = QtWidgets.QApplication.instance()
        table.popped=True
        
        self.button_layout.removeWidget(button)
        button.deleteLater()  
        del self.name_tab_idx_map[ticker]
        self.button_group.removeButton(button)
        
        for name, i in list(self.name_tab_idx_map.items()):
            if idx < i:
                button = self.button_group.buttons()[i-1]
                new_i = self.name_tab_idx_map[name] - 1
                self.button_group.setId(button, new_i)
                self.name_tab_idx_map[name]=new_i
 
        self.table_stack.removeWidget(table)
        table.show()
        
    def _open_button_context(self, pos):
        button = self.sender()
        menu = QtWidgets.QMenu(self)
        print_action = menu.addAction("Open in New Window")
        print_action.triggered.connect(lambda: self._popout_table([pos.x(), pos.y()], button))
        menu.exec(button.mapToGlobal(pos))
    
    def _initTableDimensions(self, metric_object_container):
        for name in self.name_tab_idx_map:
            inner_container=metric_object_container[name]
            table = MetricTable(inner_container, self.getattr_map)
            table.set_on_view(False)
            self.table_stack.addWidget(table)
            
    
    def closeEvent(self, event):
        self.parent().closingSubtable(self)
        super().closeEvent(event)
            

    def _initCellItems(self, metric_object_container):
        for name_instrument, idx in self.name_tab_idx_map.items():
            inner_container=metric_object_container[name_instrument]
            
            instrument_object=inner_container["object"]
            price_types=inner_container["price_types"]            

            value = instrument_object.underlying_px
            
            underlying_px_cell_item = extra_widgets.OptionMetricCellItem(f"{value:,.2f}")

            table = self.table_stack.itemAt(idx).widget()
            table.setItem(1, 0, underlying_px_cell_item)
            greeks_map={}
            for jdx, px_type in enumerate(price_types):
                metric_type_map = {}
                for idx, (name_metric, call) in enumerate(self.getattr_map.items(), start=2):
                    value = getattr(instrument_object, call)(px_type)
                    if name_metric in ["delta", "gamma"]:
                        val_str=f"{value:,.2g}"
                    else:
                        val_str=f"{value:,.2f}"
                    cell_item = extra_widgets.OptionMetricCellItem(val_str)
                    metric_type_map[name_metric]=cell_item
                    table.setItem(idx, jdx, cell_item)
                greeks_map[px_type] = metric_type_map
            
            self.metric_name_cellitem_map[name_instrument]={"underlying_px" : underlying_px_cell_item,
                                                            "greeks" : greeks_map}

    def updateFromOption(self, instrument_object: Option):
        if self.name_tab_idx_map[instrument_object.ticker] == self.table_stack.currentIndex():
            inner_cellitem_map = self.metric_name_cellitem_map[instrument_object.ticker]
            cell_item = inner_cellitem_map["underlying_px"]
            cell_item.setText(f"{instrument_object.underlying_px:,.2f}")
            for px_type, metric_map in inner_cellitem_map["greeks"].items():
                for name_metric, cell_item in metric_map.items():
                    value = getattr(instrument_object, self.getattr_map[name_metric])(px_type)
                    
                    if abs(value) < 0.01:
                        val_str=f"{value:,.2g}"
                    else:
                        val_str=f"{value:,.2f}"
                    cell_item.setText(val_str)
            

