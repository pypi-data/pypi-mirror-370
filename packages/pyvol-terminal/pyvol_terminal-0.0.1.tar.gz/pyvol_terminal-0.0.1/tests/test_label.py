from PySide6 import QtWidgets, QtCore
from datetime import datetime   
import numpy as np

class VolTable(QtWidgets.QTableWidget):
    def __init__(self, data_container_manager, tick_label_engine=None, parent=None):
        self.data_container_manager=data_container_manager
        self.tick_label_engine=tick_label_engine
        
        self.column_items=[]
        self.row_items=[]
        
        self.init_xy_data(data_container_manager)

        super().__init__(self.rows, self.columns, parent)
        self.setHorizontalHeaderLabels(self.column_vals)
        self.setVerticalHeaderLabels(self.row_vals)
        self.update_table()


    def init_xy_data(self, data_container_manager):
        self.domain_mid = data_container_manager.objects["mid"].domain
        
        self.row_vals = self.domain_mid.y_vect
        self.column_vals = self.domain_mid.x_vect
        self.rows = self.row_vals.size
        self.columns = self.column_vals.size
        
        self.column_vals=[self.tick_label_engine.x_func(new_val) for new_val in self.column_vals]
        self.row_vals=[self.tick_label_engine.y_func(new_val) for new_val in self.row_vals]

    def update_table(self):
        self.blockSignals(True)
        self.setUpdatesEnabled(False)        
        for idx in range(self.domain_mid.z_mat.shape[0]):
            for jdx in range(self.domain_mid.z_mat.shape[1]):
                new_val_str = self.tick_label_engine.z_func(self.domain_mid.z_mat[idx,jdx])
                item = QtWidgets.QTableWidgetItem(new_val_str)
                self.setItem(idx, jdx, item)
        
        self.blockSignals(False)
        self.setUpdatesEnabled(True)
    
    def _update_table_labels(self):
        self.row_vals = self.domain_mid.y_vect
        self.column_vals = self.domain_mid.x_vect
        self.rows = self.row_vals.size
        self.columns = self.column_vals.size
        
        self.setColumnCount(self.columns)
        self.setRowCount(self.rows)
        
        new_cols=[self.tick_label_engine.x_func(new_val) for new_val in self.column_vals]
        self.setHorizontalHeaderLabels(new_cols)
        
        new_rows=[self.tick_label_engine.y_func(new_val) for new_val in self.row_vals]
        self.setVerticalHeaderLabels(new_rows)




class CustomQTableWidgetItem(QtWidgets.QTableWidgetItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
    

class OptionMonitorTable(QtWidgets.QWidget):
    def __init__(self, instrument_manager, parent=None):
        super().__init__(parent)
        self.instrument_manager=instrument_manager
        self.KT_instrument_obj_map = {}
        self.instrument_obj_textitem_maps = {}        
        self.data_cols = ['instrument_name', 'bid', 'ask', 'mid', 'IVOL']
        
        self.v_layout = QtWidgets.QVBoxLayout(self)
        
        
        self.n_data_cols = len(self.data_cols)
        self.metric_columns = self.data_cols[1:]
        self.child1_n_columns = len(self.data_cols)
        self.setup_parent_table(self.data_cols, 5)
        self.expiry_strike_map = {exp : self.strikes for exp in self.expiry}
        
        self.initialise_child_tables(self.option_table)
        self.header_layout.setColumnCount(self.option_table.columnCount())
        for col in range(self.option_table.columnCount()):
            self.header_layout.setColumnWidth(col, self.option_table.columnWidth(col))
            


    def _create_table_maps(self, n_strikes):
        strikes = []
        expiry = []
        for instrument_name, option_object in self.instrument_manager.options.items():
            strikes.append(option_object.strike)
            expiry.append(option_object.expiry)

        self.expiry=np.unique(expiry)
        self.strikes=np.unique(strikes)
        
        centre = 0.5 * (self.strikes.min() + self.strikes.max())
        differences = np.abs(centre - self.strikes)
        closest_indices  = np.argsort(differences)[:n_strikes]
        
        self.strikes = self.strikes[closest_indices]
        
        self.expiry_strike_map = {}
        
        self.expiry.sort()
        self.strikes.sort()
        
        self.KT_instrument_obj_map = {}

        for T in self.expiry:
            for K in self.strikes:
                for instrument_name, option_object in self.instrument_manager.options.items():
                    if T == option_object.expiry and K == option_object.strike:
                        if option_object.flag_int == 1:
                            call_obj = option_object
                            put_name = self.instrument_manager.options_maps.put_call_map[instrument_name]
                            put_obj = self.instrument_manager.options[put_name]
                            break
                        else:
                            put_obj = option_object
                            call_name = self.instrument_manager.options_maps.put_call_map[instrument_name]
                            call_obj = self.instrument_manager.options[call_name]

                            break
                        
                self.KT_instrument_obj_map[(K,T)] = {"call" : call_obj,
                                                     "put" : put_obj}
                if "call" in self.KT_instrument_obj_map[(K,T)] and "put" in self.KT_instrument_obj_map[(K,T)]:
                    self.expiry_strike_map[T] = self.strikes

    def _create_header_tables(self, data_cols):
        self.header_layout = QtWidgets.QHBoxLayout()

        self.header_layout.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, 
            QtWidgets.QSizePolicy.Minimum  
        )

    
        n_data_cols = len(data_cols)

        n_cols = 1 + int(2 * n_data_cols)

        self.header_layout.setColumnCount(n_cols)
        self.header_layout.setRowCount(1)
        self.header_layout.setSpan(0, 0, 1, n_data_cols)
        self.header_layout.setSpan(0, n_data_cols + 1, 1, n_data_cols)
        h_c = QtWidgets.QLabel("Calls")
        h_s = QtWidgets.QLabel("Strikes")
        h_p = QtWidgets.QLabel("Puts")
        
        self.header_layout.addWidget(h_c)
        self.header_layout.addWidget(h_s)
        self.header_layout.addWidget(h_p)
        
        return self.header_layout
    
    def setup_parent_table(self, data_cols, n_strikes):
        
        self.header_layout=self._create_header_tables(data_cols)
        self._create_table_maps(n_strikes)
        self.option_table = QtWidgets.QTableWidget()
        self.option_table.verticalHeader().setVisible(False)
        self.option_table.horizontalHeader().setVisible(True)
        n_rows = len(self.expiry) * (1 + n_strikes) 
        self.option_table.setRowCount(n_rows)
        
        self.header_layout.verticalHeader().setVisible(False)
        self.header_layout.horizontalHeader().setVisible(False)
        self.header_layout.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)

        self.header_layout
        
        self._create_table_maps(n_strikes)

        n_rows = int(n_strikes * (len(self.expiry + 1)))
        
        self.option_table.setColumnCount(self.header_layout.columnCount())
        self.option_table.setRowCount(n_rows)
        
        self.option_table.setHorizontalHeaderLabels(data_cols  + [""] + data_cols)
        self.v_layout.addWidget(self.header_layout)
        self.v_layout.addWidget(self.option_table)
        

        
    def update_table(self):
        self.blockSignals(True)
        self.setUpdatesEnabled(False)        
        for instrument_obj, text_item_dict in self.instrument_obj_textitem_maps.items():
            for metric, text_item in text_item_dict.items():
                val = getattr(instrument_obj, metric)
                if metric == "IVOL":
                    val = val[2]

                text_item.setText(str(np.round(val, 2)))
        self.blockSignals(False)
        self.setUpdatesEnabled(True)     
           

    def initialise_child_tables(self, option_table):
        idx = 0
        idx_sets_c = []
        idx_sets_p = []
        for exp, strikes in self.expiry_strike_map.items():
            
            item_call = QtWidgets.QTableWidgetItem(datetime.fromtimestamp(exp).strftime("%d-%b-%y") + "c")
            
            item_call.setTextAlignment(QtCore.Qt.AlignLeft)
            font_call = item_call.font()
            font_call.setPointSize(12)
            item_call.setFont(font_call)
            item_call.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            
            item_put = CustomQTableWidgetItem(datetime.fromtimestamp(exp).strftime("%d-%b-%y") + 'p')
            item_put.setTextAlignment(QtCore.Qt.AlignLeft)
            font_put = item_put.font()
            font_put.setPointSize(12)
            item_put.setFont(font_put)
            item_put.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            
            option_table.setSpan(idx, 0, 1, self.n_data_cols) 
            option_table.setSpan(idx, self.n_data_cols + 1, 1, self.n_data_cols)
            
            line_edit_widget = self.create_line_edit(len(strikes))
            
            option_table.setItem(idx, 0, item_call)
            option_table.setCellWidget(idx, self.n_data_cols, line_edit_widget)
            option_table.setItem(idx, self.n_data_cols + 1, item_put)
            
            idx += 1
        
            for strike in strikes:
                call_object = self.KT_instrument_obj_map[(strike, exp)]["call"]
                put_object = self.KT_instrument_obj_map[(strike, exp)]["put"]

                item_c = CustomQTableWidgetItem(str(call_object.instrument_name))
                item_p = CustomQTableWidgetItem(str(put_object.instrument_name))

                item_c.setTextAlignment(QtCore.Qt.AlignLeft)
                item_p.setTextAlignment(QtCore.Qt.AlignLeft)
                
                if (idx,0) in idx_sets_c:
                    print("call")
                    print(idx, 0)
                    
                if (idx,0) in idx_sets_p:
                    print("put")
                    print(idx, 0)
            
                item_s = CustomQTableWidgetItem(str(strike))
                
                option_table.setItem(idx, 0, item_c)
                option_table.setItem(idx, self.n_data_cols, item_s)
                option_table.setItem(idx, self.n_data_cols + 1, item_p)
                
                idx_sets_c.append((idx,0))
                idx_sets_p.append((idx,0))

                self.instrument_obj_textitem_maps[call_object] = item_c
                self.instrument_obj_textitem_maps[put_object] = item_p

                call_metric_dict = {}
                put_metric_dict = {}
                jdx = 1
                
                for metric in self.metric_columns:
                    c_val = getattr(call_object, metric)
                    if metric == "IVOL":
                        c_val = c_val[2]
                    if c_val != c_val:
                        c_val=str(c_val)
                    else:
                        c_val=str(np.round(c_val),2)
                    
                    p_val = getattr(put_object, metric)
                    if metric == "IVOL":
                        p_val = p_val[2]

                    if p_val != p_val:
                        p_val=str(p_val)
                    else:
                        p_val=str(np.round(p_val),2)
                        
                        
                        
                    item_c = CustomQTableWidgetItem(c_val)
                    item_p = CustomQTableWidgetItem(p_val)
                    call_metric_dict[metric] = item_c
                    put_metric_dict[metric] = item_p

                    item_c.setTextAlignment(QtCore.Qt.AlignCenter)
                    item_p.setTextAlignment(QtCore.Qt.AlignCenter)
                    
                    if (idx,jdx) in idx_sets_c:
                        print("call")
                        print(idx, jdx)
                        
                    if (idx,jdx) in idx_sets_p:
                        print("put")
                        print(idx, jdx)

                    idx_sets_c.append((idx,jdx))
                    idx_sets_p.append((idx,jdx))


                    option_table.setItem(idx, jdx, item_c)
                    option_table.setItem(idx, jdx + self.n_data_cols + 1, item_p)
                    jdx+=1
                    
                idx+=1
                self.instrument_obj_textitem_maps[call_object] = call_metric_dict
                self.instrument_obj_textitem_maps[put_object] = put_metric_dict

                
    def create_line_edit(self, n_strikes):
        line_edit = QtWidgets.QLineEdit()
        line_edit.setText(f"{n_strikes}") 
        line_edit.setAlignment(QtCore.Qt.AlignCenter)  
        line_edit.setStyleSheet("""
                                QLineEdit {
                                        background-color: white;
                                        color: black;
                                        text-align: center;
                                 }
                                    QLineEdit:focus {
                                        background-color: #ffffcc; 
                                        border: 2px solid #3366ff;
                                 }
                                """)
        line_edit.editingFinished.connect(self.change_strikes)
        return line_edit
    
    def change_strikes(self):
        line_edit = self.sender() 
        typed_text = line_edit.text() 
        n_strikes = int(float(typed_text))
        line_edit.clearFocus()
        
