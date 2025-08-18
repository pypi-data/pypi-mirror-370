from __future__ import annotations 
from typing import List, Optional, Tuple, Union, Dict, TYPE_CHECKING, Callable, Any
if TYPE_CHECKING:
    from instruments.instruments import Option, ABCInstrument, Derivative
    from instruments.utils import InstrumentManager
    from ...data_classes.classes import Slice
    
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt
from . import stylesheets
from datetime import datetime  
import pandas as pd 
from ...settings.widgets import CenteredPopupComboBox
from pprint import pprint
from . import utils as utils_omon



class CustomDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, table):
        super().__init__()
        self.table = table

    def paint(self, painter, option, index):
        HIGHLIGHT_COLOR = QtGui.QColor("#9e9e9f")
        if option.state & QtWidgets.QStyle.State_Selected:
            painter.fillRect(option.rect, option.palette.highlight().color())
        else:
            
            item = self.table.item(index.row(), index.column())
            if item:
                painter.fillRect(option.rect, item.background().color())
        item = self.table.item(index.row(), index.column())
        if item:
            painter.save()
            painter.setFont(item.font())
            text_color = item.foreground().color()
            if option.state & QtWidgets.QStyle.State_Selected:
                text_color = option.palette.highlightedText().color()
            painter.setPen(text_color)
            text_rect = option.rect.adjusted(4, 0, -4, 0)
            painter.drawText(text_rect, item.textAlignment() | Qt.AlignVCenter, item.text())
            painter.restore()

    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        if option.state & QtWidgets.QStyle.State_Selected:
            option.backgroundBrush = option.palette.highlight()
            option.palette.setColor(QtGui.QPalette.HighlightedText, index.data(Qt.ForegroundRole).color())
                
                
class StrikeCellItem(QtWidgets.QTableWidgetItem):   
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFlags(self.flags() | Qt.ItemIsSelectable)
        self.setFlags(self.flags() & ~Qt.ItemIsEditable)
        self.setBackground(QtGui.QBrush("black"))
        self.setForeground(QtGui.QBrush("white"))
        self.setTextAlignment(Qt.AlignCenter)
        font = QtGui.QFont("Neue Haas Grotesk", 12)
        self.setFont(font)


class OptionMetricCellItem(QtWidgets.QTableWidgetItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFlags(self.flags() | Qt.ItemIsSelectable)
        self.setFlags(self.flags() & ~Qt.ItemIsEditable)
        self.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)  
        self.setBackground(QtGui.QBrush(QtGui.QColor("black"))) 
        self.setForeground(QtGui.QBrush(QtGui.QColor("white"))) 
        self.setTextAlignment(Qt.AlignRight)
        font = QtGui.QFont("Neue Haas Grotesk", 12)
        self.setFont(font)
        

class BlankCellItem(QtWidgets.QTableWidgetItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFlags(self.flags() & ~Qt.ItemIsSelectable)
        self.setFlags(self.flags() & ~Qt.ItemIsEditable)
        self.setBackground(QtGui.QBrush(QtGui.QColor("#414141")))
        self.setForeground(QtGui.QBrush(QtGui.QColor("#fb8b1e")))
        self.setTextAlignment(Qt.AlignRight)

class CellItemContainer(QtCore.QObject):
    def __init__(self, *args):
        super().__init__(*args)
        self.container=[]
    
    def addItem(self, item):
        self.container.append(item)
    
    def checkWidths(self, column, table):
        if not table:
            return True
        
        column_width = table.columnWidth(column)
        
        while True:
            _fits=True
            for item in self.container:
                text = item.text()
                font_metrics = QtGui.QFontMetrics(item.font())
                text_width = font_metrics.horizontalAdvance(text)
                if text_width > column_width:
                    _fits=False
            if _fits:
                break
            else:
                for item in self.container:
                    font = item.font()
                    new_pointSize = font.pointSize()-1
                    font.setPointSize(new_pointSize)
                    item.setFont(font)


class OptionNameCellItem(QtWidgets.QTableWidgetItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)  
        self.setBackground(QtGui.QBrush("black"))
        self.setForeground(QtGui.QBrush(QtGui.QColor("#fb8b1e")))
        self.setTextAlignment(Qt.AlignLeft)
        self.setFlags(self.flags() | Qt.ItemIsSelectable)
        self.setFlags(self.flags() & ~Qt.ItemIsEditable)
        font = QtGui.QFont("Neue Haas Grotesk", 12)
        
        self.setFont(font)
        
        
class OptionExpiryCellItem(QtWidgets.QTableWidgetItem):
    def __init__(self, *args, **kwargs):
        args = list(args)
        self.expiry = args[0]
        if not self.expiry is None:
            dte = int(round((self.expiry - datetime.now().timestamp()) / 3600 / 24))
            dte_str = f"({dte}d)"
            expiry_str = f"{pd.to_datetime(self.expiry, utc=True, unit="s").strftime('%d-%b-%y')} {dte_str}"
        else:
            expiry_str = args[0]
        args[0]=expiry_str
        
        super().__init__(*args, **kwargs)
        self.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        self.setBackground(QtGui.QBrush(QtGui.QColor("#414141")))
        self.setForeground(QtGui.QBrush(QtGui.QColor("white")))
        self.setTextAlignment(Qt.AlignLeft)
        font = QtGui.QFont("Neue Haas Grotesk", 8)
        self.setFont(font)
    
    def update_from_base(self, appended_str):
        dte = int(round((self.expiry - datetime.now().timestamp()) / 3600 / 24))
        dte_str = f"({dte}d)"
        expiry_str = f"{pd.to_datetime(self.expiry, utc=True, unit="s").strftime('%d-%b-%y')} {dte_str}"
        expiry_str = expiry_str + f" {round(appended_str, 2)}"
        self.setText(expiry_str)

    def does_text_fit(self) -> bool:
        table = self.tableWidget()
        if not table:
            return True
        
        column = self.column()
        column_width = table.columnWidth(column)
        
        font_metrics = QtGui.QFontMetrics(self.font())
        text = self.text()
        text_width = font_metrics.horizontalAdvance(text)
        
        padding = 10 
        return (text_width + padding) <= column_width

class TableColumnItem(QtWidgets.QTableWidgetItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFlags(self.flags() | Qt.ItemIsEnabled)
        self.setBackground(QtGui.QBrush(QtGui.QColor("#414141")))
        self.setForeground(QtGui.QBrush("white"))
        self.setTextAlignment(Qt.AlignCenter)
        font = QtGui.QFont("Neue Haas Grotesk", 12)
        font.setBold(True)
        self.setFont(font) 
        
class StrikeOptionsComboBox(CenteredPopupComboBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.view().setAutoScroll(False)
    #    self.setStyleSheet(stylesheets.get_settings_stylesheets("StrikeOptionsComboBox"))        
     #   font = QtGui.QFont("Neue Haas Grotesk", 12)
     #   self.setFont(font)

            

class RightClickMenu(QtWidgets.QMenu):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hide()
        
    def eventFilter(self, obj, event):
        if event.type() in (QtCore.QEvent.MouseButtonPress,
                            QtCore.QEvent.KeyPress,
                            QtCore.QEvent.FocusOut
                            ):
            self.close()
        return super().eventFilter(obj, event)
    
    def popup(self, q_point, name_metric_map, parent_table):
        if hasattr(self, "greeks_action"):
            self.removeAction(self.greeks_action)
        self._create_greeks(q_point,
                            name_metric_map,
                            parent_table
                            )
        global_pos = self.parent().mapFromGlobal(q_point)
        self.parent().installEventFilter(self)
        print(self.parent())
        super().popup(global_pos)
        
    def _create_greeks(self, q_point, name_metric_map, parent_table):
        self.greeks_action = self.addAction("Greeks")
        self.greeks_action.triggered.connect(lambda : parent_table.create_subtable(q_point, name_metric_map))
        

class MetricTable(QtWidgets.QTableWidget):
    def __init__(self, name_metric_map, getattr_map, label_price_types, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.getattr_map=getattr_map
        self.label_price_types=label_price_types
        self.nrows = 1 + len(self.getattr_map)
        self.ncols=len(self.label_price_types["label"])
        self.cellitem_container={}
        self._on_view=True
        self._underlying_object = name_metric_map["object"]
        self._initLayout()
        self._initContents()
        self.autoFillBackground()
        self.setShowGrid(False)
        self.pop_table=False
        
    def set_on_view(self, flag):
        self._on_view=flag
        
    def _initLayout(self):
        self.verticalHeader().setVisible(True)
        self.horizontalHeader().setVisible(True)
        self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        self.setStyleSheet(stylesheets.get_settings_stylesheets("SubQTableWidget"))   
        
        self.setRowCount(self.nrows)
        self.setColumnCount(self.ncols)        
        
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
    def _initContents(self):
        for jdx, px_type in enumerate(self.label_price_types["label"]):
            col_name_item = TableColumnItem(px_type)
            font = QtGui.QFont("Neue Haas Grotesk", 12)
            col_name_item.setFont(font)
            self.setHorizontalHeaderItem(jdx, col_name_item)

        underlying_label = TableColumnItem("underlying_px")
        underlying_label.setTextAlignment(QtCore.Qt.AlignLeft)
        font = QtGui.QFont("Neue Haas Grotesk", 12)
        underlying_label.setFont(font)
        self.setVerticalHeaderItem(0, underlying_label)
        if self.columnCount() > 1:
            self.setSpan(0, 0, 1, self.columnCount())

        for idx, name in enumerate(self.getattr_map, start=1):
            row_name_item = TableColumnItem(name)
            row_name_item.setTextAlignment(QtCore.Qt.AlignLeft)
            row_name_item.setFont(font)
            self.setVerticalHeaderItem(idx, row_name_item)
    
                    


class OptionMetricsWithTabs(QtWidgets.QWidget):
    def __init__(self, *, name_metric_map, getattr_map, **kwargs):
        super().__init__(**kwargs)
        self.getattr_map=getattr_map
        self.name_metric_map=name_metric_map
        self.instrument_names=list(name_metric_map.keys())
        pprint(getattr_map)
        self.label_ptype_container={name : inner_dict["selectedPriceTypes"] for name, inner_dict in name_metric_map.items()}
        self.nrows = 2 + len(self.getattr_map)
        self.cellItemContainer={}
        self.name_tab_idx_map={}
        self.buttons=[]
        self._initLayout()
        self._initTabs(name_metric_map)
        self._initTableDimensions(name_metric_map)
        self._initCellItems(name_metric_map)
        self.autoFillBackground()
        btn = self.button_group.button(0)
        btn.click()
        self.fitToTable()
        
    def _initLayout(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)
        self.button_group = QtWidgets.QButtonGroup()
        self.table_stack = QtWidgets.QStackedLayout()
        
        self.table_stack.currentChanged.connect(self.fitToTable)
        
        self.button_layout = FlowLayout()
        self.button_layout.setContentsMargins(0, 0, 0, 0)
        
        self.main_layout.addLayout(self.button_layout)
        self.main_layout.addLayout(self.table_stack)
        
        self.main_layout.setStretch(0, 0) 
        self.main_layout.setStretch(1, 1) 
    

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
            self.button_group.addButton(btn, id=idx) 
            self.button_group.idToggled.connect(slot)
            self.name_tab_idx_map[name]=idx
        self.button_layout.addStretch()
            
    def _popout_table(self, pos, button):
        ticker = button.text()
        table = self.table_stack.itemAt(self.name_tab_idx_map[ticker]).widget()
        table.set_on_view(True)
        idx = self.name_tab_idx_map[ticker]
        
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
            table = MetricTable(inner_container, self.getattr_map, self.label_ptype_container[name])
            table.set_on_view(False)
            self.table_stack.addWidget(table)
            
    def closeEvent(self, event):
        self.parent().closingSubtable(self)
        super().closeEvent(event)
            
    def _initCellItems(self, metric_object_container):
        print("\n\ninit")
        for name_instrument, idx in self.name_tab_idx_map.items():
            print(f"\n{name_instrument}")
            inner_container=metric_object_container[name_instrument]
            
            instrument_object=inner_container["object"]

            value = instrument_object.underlying_px
            
            underlyingCellItem = OptionMetricCellItem(f"{value:,.2f}")
            underlyingCellItem.setTextAlignment(QtCore.Qt.AlignLeft)
            table = self.table_stack.itemAt(idx).widget()
            print("dimension")
            print(idx)
            print((table.rowCount(), table.columnCount()))
            table.setItem(0, 0, underlyingCellItem)
            metric_map={}
            
            for jdx, px_type in enumerate(self.name_metric_map[name_instrument]["selectedPriceTypes"]["attribute"]):
                print(px_type)
                metric_type_map = {}
                for idx, (metric_label, metric_attr) in enumerate(self.getattr_map.items(), start=1):
                    print(metric_label)
                    value = getattr(instrument_object, metric_attr)(px_type)
                    if metric_label in ["delta", "gamma"]:
                        val_str=f"{value:,.2g}"
                    else:
                        val_str=f"{value:,.2f}"
                    cell_item = OptionMetricCellItem(val_str)
                    metric_type_map[metric_label]=cell_item
                    table.setItem(idx, jdx, cell_item)
                    print(f"{(idx, jdx)} {cell_item.text()}")
                metric_map[px_type] = metric_type_map
            
            self.cellItemContainer[name_instrument]={"underlying_px" : underlyingCellItem,
                                                     "metrics" : metric_map}

    def updateFromOption(self, instrument_object: Option):
        if self.name_tab_idx_map[instrument_object.ticker] == self.table_stack.currentIndex():
            cell_item = self.table_stack.currentWidget().itemAt(0, 0)
            cell_item.setText(f"{instrument_object.underlying_px:,.2f}")

            inner_cellitem_map = self.cellItemContainer[instrument_object.ticker]
            
            for px_type, metric_map in inner_cellitem_map["metrics"].items():
                for name_metric, cell_item in metric_map.items():
                    value = getattr(instrument_object, self.getattr_map[name_metric])(px_type)
                    
                    if abs(value) < 0.01:
                        val_str=f"{value:,.2g}"
                    else:
                        val_str=f"{value:,.2f}"
                    cell_item.setText(val_str)
                
    def fitToTable(self):
        current_table = self.table_stack.currentWidget()
        table_width = (current_table.verticalHeader().width() + 
                        current_table.horizontalHeader().length() + 
                        current_table.frameWidth() * 2)
        
        table_height = (current_table.horizontalHeader().height() + 
                        current_table.verticalHeader().length() + 
                        current_table.frameWidth() * 2)
        
        button_height = 0
        if self.buttons:
            button_height = self.buttons[0].sizeHint().height() * len(self.buttons)
            button_height += self.button_layout.spacing() * (len(self.buttons) - 1)
        
        margins = self.main_layout.contentsMargins()
        
        total_width = max(table_width, self.button_layout.sizeHint().width()) + margins.left() + margins.right()
        total_height = table_height + button_height + margins.top() + margins.bottom()        
        self.setFixedSize(total_width, total_height)
            
    def resizeEvent(self, event):
        if self.parent() and isinstance(self.window(), QtWidgets.QMainWindow):
            window = self.window()
            frame_size = window.frameSize()
            content_size = window.size()
            
            width_diff = frame_size.width() - content_size.width()
            height_diff = frame_size.height() - content_size.height()
            
            window.resize(self.width() + width_diff,
                          self.height() + height_diff
                          )
        super().resizeEvent(event)
        

class FlowLayout(QtWidgets.QLayout):
    def __init__(self, parent=None, margin=0, spacing=-1):
        super().__init__(parent)
        
        if parent is not None:
            self.setContentsMargins(margin, margin, margin, margin)
            
        self.setSpacing(spacing)
        self.itemList = []
        
    def addItem(self, item):
        self.itemList.append(item)
        
    def count(self):
        return len(self.itemList)
        
    def itemAt(self, index):
        if 0 <= index < len(self.itemList):
            return self.itemList[index]
        return None
        
    def takeAt(self, index):
        if 0 <= index < len(self.itemList):
            return self.itemList.pop(index)
        return None
        
    def expandingDirections(self):
        return QtCore.Qt.Orientations(QtCore.Qt.Orientation(0))
        
    def hasHeightForWidth(self):
        return True
        
    def heightForWidth(self, width):
        return self.doLayout(QtCore.QRect(0, 0, width, 0), True)
        
    def setGeometry(self, rect):
        super().setGeometry(rect)
        self.doLayout(rect, False)
        
    def sizeHint(self):
        return self.minimumSize()
        
    def minimumSize(self):
        size = QtCore.QSize()
        
        for item in self.itemList:
            size = size.expandedTo(item.minimumSize())
            
        margins = self.contentsMargins()
        size += QtCore.QSize(margins.left() + margins.right(), margins.top() + margins.bottom())
        return size
        
    def doLayout(self, rect, testOnly):
        x = rect.x()
        y = rect.y()
        lineHeight = 0
        
        for item in self.itemList:
            spaceX = self.spacing()
            spaceY = self.spacing()
            nextX = x + item.sizeHint().width() + spaceX
            if nextX - spaceX > rect.right() and lineHeight > 0:
                x = rect.x()
                y = y + lineHeight + spaceY
                nextX = x + item.sizeHint().width() + spaceX
                lineHeight = 0
                
            if not testOnly:
                item.setGeometry(QtCore.QRect(QtCore.QPoint(x, y), item.sizeHint()))
                
            x = nextX
            lineHeight = max(lineHeight, item.sizeHint().height())
            
        return y + lineHeight - rect.y()
    
    def addStretch(self, stretch=0):
        spacer = QtWidgets.QSpacerItem(0, 0, 
                                       QtWidgets.QSizePolicy.Policy.Expanding, 
                                       QtWidgets.QSizePolicy.Policy.Minimum)
        self.addItem(spacer)
        
    def addWidget(self, widget):
        self.addChildWidget(widget)  
        self.addItem(QtWidgets.QWidgetItem(widget))