import numpy as np
from dataclasses import dataclass
import time
from datetime import datetime
import numpy as np
import pandas as pd
from abc import ABC, abstractmethod

class CustomDatetime:
    @staticmethod
    def fromtimestamp(ts):
        if ts != ts: 
            return str(ts)
        return datetime.fromtimestamp(ts)


def cleanup_dataframe(df, df_type):
    if df_type == "options":
        df = df.sort_values(by=["expiry", "strike", "flag"], ascending=[True, True, False])
        df.reset_index(drop=True, inplace=True)
        
        for idx, opt_type in zip(df.index, df["flag"]):
            if opt_type.lower() == "call":
                df.loc[idx, "flag"] = "c"
            elif opt_type.lower() == "put":
                df.loc[idx, "flag"] = "p"

    elif df_type == "futures" or df_type == "options":
        df = df.sort_values(by=["expiry"], ascending=[True])
    
    numeric_columns = ["strike", "expiry", "bid", "ask", "mid"]
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    return df

class AbstractValidPriceChecker(ABC):
    
    @abstractmethod
    def __init__(self, *args):
        ...

    @abstractmethod
    def check(self, *args):
        ...

class ValidPriceChecker(AbstractValidPriceChecker):
    def __init__(self, spread_minimum):
        self.spread_minimum = spread_minimum  
        
    def check(self, bid, ask):
        if (np.isnan(bid)
            or np.isnan(ask)
            or bid==0
            or ask==0
            or 100 * (ask - bid) / (0.5 * (bid + ask)) > self.spread_minimum
            ):
            return False
        else:
            return True

def filter_nans_2D(x, y):
    return x[~np.isnan(y)], y[~np.isnan(y)]

def filter_nans_on_z(x, y, z):
    return x[~np.isnan(z)], y[~np.isnan(z)], z[~np.isnan(z)]

def filter_nans_on_z_OTM(x, y, OTM, z):
    return x[~np.isnan(z)], y[~np.isnan(z)], OTM[~np.isnan(z)], z[~np.isnan(z)]


def check_same_nan_structure(arr1, arr2):
    mask1 = np.isfinite(arr1)  
    mask2 = np.isfinite(arr2)  
    return np.array_equal(mask1, mask2)

@dataclass(frozen=True, slots=True)
class ws_pyvol_keymap:
    ticker: str
    bid: str
    ask: str
    timestamp: str

def create_websocket_pyvol_keymapper(ticker_key, bid_key, ask_key, timestamp_key) -> ws_pyvol_keymap:
    return ws_pyvol_keymap(ticker_key,
                           bid_key,
                           ask_key,
                           timestamp_key
                           )

def convert_unix_maturity_to_years(unix_maturity):
    return (unix_maturity - time.time()) / 3600 / 24 / 365

def convert_to_yte(timestamp, unix_maturity):
    return (unix_maturity - timestamp) / 3600 / 24 / 365

def calculate_xy_lines(X, Y, Z, x_fixed, y_fixed, const_axis):
    if const_axis:
        y_index = np.argmin(np.abs(Y - y_fixed))  
        line = np.column_stack((X, [y_fixed]*X.size, Z[:,y_index]))     
    else:
        x_index = np.argmin(np.abs(X - x_fixed)) 
        line = np.column_stack(([x_fixed] * Y.size, Y, Z[x_index,: ]))  
    return line


class BiDict:
    def __init__(self):
        self._type1_to_type2 = {}  # Maps type1 keys to type2 values
        self._type2_to_type1 = {}  # Maps type2 keys to type1 values

    def add(self, type1, type2):
        """Add a bidirectional mapping between type1 and type2."""
        self._type1_to_type2[type1] = type2
        self._type2_to_type1[type2] = type1

    def get_type2(self, type1):
        """Get the type2 value associated with a type1 key."""
        return self._type1_to_type2.get(type1)

    def get_type1(self, type2):
        """Get the type1 value associated with a type2 key."""
        return self._type2_to_type1.get(type2)

    def remove_type1(self, type1):
        """Remove a mapping by type1 key."""
        if type1 in self._type1_to_type2:
            type2 = self._type1_to_type2.pop(type1)
            del self._type2_to_type1[type2]

    def remove_type2(self, type2):
        """Remove a mapping by type2 key."""
        if type2 in self._type2_to_type1:
            type1 = self._type2_to_type1.pop(type2)
            del self._type1_to_type2[type1]

    @property
    def type1(self):
        """Return an iterable view of type1 keys."""
        return self._type1_to_type2.keys()

    @property
    def type2(self):
        """Return an iterable view of type2 keys."""
        return self._type2_to_type1.keys()

    def iter_type1(self):
        """Iterate over type1 keys and their corresponding type2 values."""
        return self._type1_to_type2.items()

    def iter_type2(self):
        """Iterate over type2 keys and their corresponding type1 values."""
        return self._type2_to_type1.items()

    def __contains__(self, key):
        """Check if a key exists in either type1 or type2."""
        return key in self._type1_to_type2 or key in self._type2_to_type1

    def __len__(self):
        """Return the number of mappings."""
        return len(self._type1_to_type2)

    def __repr__(self):
        """Return a string representation of the BiDict."""
        return f"BiDict(type1_to_type2={self._type1_to_type2}, type2_to_type1={self._type2_to_type1})"