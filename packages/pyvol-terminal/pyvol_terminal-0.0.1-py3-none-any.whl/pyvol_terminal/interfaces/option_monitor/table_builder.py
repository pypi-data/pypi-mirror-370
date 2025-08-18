from . import stylesheets as stylesheets
import numpy as np
from . import extra_widgets
from datetime import datetime   
import time 
from line_profiler import profile
from . import utils as utils_omon


def create_and_set_text_widget(table, widget, string, idx, jdx):
    text_item = widget(string)
    table.setItem(idx, jdx, text_item)

def change_strikes(new_n_strikes, table, expiry_attribute):
    new_n_strikes = int(float(new_n_strikes))
    table.blockSignals(True)
    table.setUpdatesEnabled(False)
    if new_n_strikes == len(table.current_expiry_strike_map[expiry_attribute.expiry]):
        return
    else:
        table.setItemDelegate(None)
        update_strikes_for_expiry(table, new_n_strikes, expiry_attribute)
        table.setItemDelegate(extra_widgets.CustomDelegate(table))
        
    table.blockSignals(False)
    table.setUpdatesEnabled(True)
    
def create_strike_combobox(expiry_attribute):
    combobox = extra_widgets.StrikeOptionsComboBox()
    combobox.addItem(str(0))
    for n_strike, _ in enumerate(expiry_attribute.strikes, start=1):
        combobox.addItem(str(n_strike))
    return combobox

def create_expiry_section(expiry, strikes, insturment_names, metrics, start_idx):
    table_widget_items=[]
    
    table_widget_item = extra_widgets.OptionExpiryCellItem(expiry)
    table_widget_items.append({"pos" : (start_idx, 0), "item" : table_widget_item})
    
    for jdx, _ in enumerate(metrics, start=1):
        table_widget_item = extra_widgets.OptionExpiryCellItem(None)
        table_widget_items.append({"pos" : (start_idx, jdx), "item" : table_widget_item})

    for strike, ticker in zip(strikes, insturment_names):        
        start_idx += 1
        
        table_widget_item = extra_widgets.OptionNameCellItem(ticker)
        table_widget_items.append({"pos" : (start_idx, 0), "item" : table_widget_item})
        
        for jdx, _ in enumerate(metrics, start=1):     
            table_widget_item = extra_widgets.OptionMetricCellItem("")           
            table_widget_items.append({"pos" : (start_idx, jdx), "item" : table_widget_item})
    return table_widget_items

def update_table_rows(table, expiry_attribute, strikes_to_change, hide_flag, table_method):
    for strike in strikes_to_change:
        idx = expiry_attribute.strike_idx_map[strike]
        table.setRowHidden(idx, hide_flag)
        for opt_type in ["c", "p"]:
            opt_name = table.options_container.maps.expiry_strike_type_instrument_map[expiry_attribute.expiry][strike][opt_type]
            getattr(table.viewable_instruments, table_method)(opt_name)

@profile
def update_strikes_for_expiry(table, new_n_strikes, expiry_attribute):
    old_strikes = table.current_expiry_strike_map[expiry_attribute.expiry]
    new_strikes, _, _  = utils_omon.get_closest_n_strikes(table.strike_center, expiry_attribute.strikes, new_n_strikes)

    table.current_expiry_strike_map[expiry_attribute.expiry] = new_strikes

    if len(new_strikes) > len(old_strikes):
        strikes_to_change = [strike for strike in new_strikes if not strike in old_strikes]
        update_table_rows(table, expiry_attribute, strikes_to_change, False, "append")

    elif len(new_strikes) == len(old_strikes):
        strikes_to_add = [strike for strike in new_strikes if not strike in old_strikes]
        update_table_rows(table, expiry_attribute, strikes_to_add, False, "append")
        strikes_to_remove = [strike for strike in old_strikes if not strike in new_strikes]
        update_table_rows(table, expiry_attribute, strikes_to_remove, True, "remove")
    else:
        strikes_to_change = [strike for strike in old_strikes if not strike in new_strikes]
        update_table_rows(table, expiry_attribute, strikes_to_change, True, "remove")
