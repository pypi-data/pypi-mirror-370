#%%
import QuantLib as ql
from datetime import datetime
import pandas as pd
import time
import py_vollib_vectorized 
from pyvol_terminal.instruments import instruments
from pyvol_terminal.instruments import builders as builders_instruments
from pyvol_terminal import utils as main_utils
from pyvol_terminal.instruments import instruments
from pyvol_terminal.instruments import builders as builders_instruments
from pyvol_terminal.engines.option_engines import black
from pyvol_terminal.engines import surface_engines
from pyvol_terminal.interfaces.volatility_surface.interface import Interface as interface_surface
#from pyvol_terminal.interfaces.volatility_table.interface import Interface as interface_vol_table
from pyvol_terminal.interfaces.option_monitor.interface import Interface as interface_omon_table
from pyvol_terminal.interfaces.pricing_engine.interface import Interface as interface_pricing_engine
#from pyvol_terminal.interfaces.slice.interface import Interface as interface_slice
from pyvol_terminal import misc_widgets
from pyvol_terminal.ui_themes import legend_colourmap_getter
from pyvol_terminal.data_classes import builders as builders_dataclasses
from examples.synthetic import websocket_streamer
import sys
import numpy as np
from PySide6 import QtGui   


def format_date(dt: datetime) -> str:
    return f"{dt.day}{dt.strftime('%b%y').upper()}"


def reformat_instrument_names(df, fut=False):
    expiries = pd.to_datetime(df['expiry'], utc=True, unit="s")
    instrument_names = []
    channels=[]
    for idx, expiry in enumerate(expiries):
        exp_str = format_date(expiry)
        tupl = df["instrument_name"].iloc[idx].split("-")
        if len(tupl) == 4:
            underlying, _, strike, flag = tupl
            instrument_name = f"{underlying}-{exp_str}-{strike}-{flag}"
        elif len(tupl) == 2:
            underlying, _ = tupl
            instrument_name = f"{underlying}-{exp_str}"
        channel = f"ticker.{instrument_name}.100ms"
        
        instrument_names.append(instrument_name)
        channels.append(channel)    
    df["instrument_name"] = instrument_names
    return channels
    

def get_saved_data():
    df_options = pd.read_csv("df_options.csv")
    df_futures = pd.read_csv("df_futures.csv")
    df_spot = pd.read_csv("df_spot.csv")
    
    reference_time = 1743506630.313821
    time_delta = time.time() - reference_time
    df_options["expiry"]+=time_delta
    df_futures["expiry"]+=time_delta

    channels_opt = reformat_instrument_names(df_options)
    channels_fut = reformat_instrument_names(df_futures)
    

    """
    expiry = df_options["expiry"].unique()[:6]
    df_options = df_options[df_options["expiry"].isin(expiry)]
    df_options = df_options[(df_options["strike"] <= 100_000) & (df_options["strike"] >= 70_000)]
    df_futures = df_futures[df_futures["expiry"].isin(expiry)]
    """
    
    with open("channels.txt", "r") as file:
        channels = [line.strip() for line in file]  
    
    channels_spot = [channel for channel in channels if "BTC_USDC" in channel]
    channels = channels_spot + channels_fut + channels_spot
        
    return channels, df_options, df_futures, df_spot


def get_data():
    
    channels, df_options, df_futures, df_spot = get_saved_data()
    
    vol_params = {"ATM_vol" : 0.65,
                  "kurtosis_1" : 0.95,
                  "kurtosis_2" : 0.2,
                  "decay" : 0.8
                  }

    btc_usdc = 90000.
    r = 0.05 
    
    df_options = df_options[df_options["flag"]=="p"]
    df_options = df_options[df_options["strike"] <= btc_usdc-2000]       
    print(df_options)
    df_options["underlying_px"] = np.nan
    
    df_options["bid_iv"] = np.nan
    df_options["ask_iv"] = np.nan
    df_options["best_bid_price"] = np.nan
    df_options["best_ask_price"] = np.nan
    
    df_options["expiry_T"] = (df_options["expiry"] - time.time()) / 3600 / 24 / 365
    df_options = df_options[df_options["expiry_T"] >0.05]       
    
    generate_futures(df_futures, btc_usdc, r)
    df_futures = df_futures[df_futures["expiry_T"] >0.05]     
    
    print(df_futures)
    
    
    for idx, row in df_options.iterrows():
        exp = row["expiry"]
        price = df_futures[df_futures["expiry"] == exp]["mid"].item()
        df_options.loc[idx, "underlying_px"] = price
        df_options.loc[idx, "underlying_ticker"] = df_futures[df_futures["expiry"] == exp]["instrument_name"].item()
        
    for idx, row in df_options.iterrows():
        price = row["underlying_px"]
        bid_iv = generate_synthetic_surface(vol_params, row["underlying_px"], df_options.loc[idx, "strike"], df_options.loc[idx, "expiry_T"]) + 0.01
        mid_iv = generate_synthetic_surface(vol_params, row["underlying_px"], df_options.loc[idx, "strike"], df_options.loc[idx, "expiry_T"]) 
        ask_iv = generate_synthetic_surface(vol_params, row["underlying_px"], df_options.loc[idx, "strike"], df_options.loc[idx, "expiry_T"]) - 0.01
        df_options.loc[idx, "mid_iv"] = mid_iv

        df_options.loc[idx, "bid_iv"] = bid_iv
        df_options.loc[idx, "ask_iv"] = ask_iv
        df_options.loc[idx, "best_bid_price"] = py_vollib_vectorized.vectorized_black(row["flag"], price, row["strike"], row["expiry_T"], r, bid_iv)["Price"].item() / price
        df_options.loc[idx, "best_ask_price"] = py_vollib_vectorized.vectorized_black(row["flag"], price, row["strike"], row["expiry_T"], r, ask_iv)["Price"].item() / price
        
    df_spot["bids"] = btc_usdc - 0.01
    df_spot["asks"] = btc_usdc + 0.01
    
    future_underlying_ticker_map = {future_name : df_spot["instrument_name"].values[0] for future_name in df_futures["instrument_name"]}
    
    option_underlying_ticker_map = {}
    for _, option_row in df_options.iterrows():
        option_name = option_row["instrument_name"]
        option_expiry = option_row["expiry"]
        future_name = df_futures[df_futures["expiry"] == option_expiry]["instrument_name"].iloc[0]
        option_underlying_ticker_map[option_name] = future_name
    return channels, df_options, df_futures, df_spot, option_underlying_ticker_map, future_underlying_ticker_map

def generate_futures(df_futures, spot, r):
    df_futures["expiry_T"] = (df_futures["expiry"] - time.time()) / 3600 / 24 / 365
    
    df_futures["mid"] = spot * np.exp(r * df_futures["expiry_T"])
    df_futures["mid"] = np.round(df_futures["mid"])
    df_futures["best_bid_price"] = (spot -0.5) * np.exp(r * df_futures["expiry_T"])
    df_futures["best_ask_price"] = (spot + 0.5) * np.exp(r * df_futures["expiry_T"])
    df_futures["r"] = r
    
def generate_synthetic_surface(market_params, S, K, T):
    ATM_vol = market_params["ATM_vol"]
    kurtosis_1 = market_params["kurtosis_1"]
    kurtosis_2 = market_params["kurtosis_2"]
    decay = market_params["decay"]
    
    if K < S:
        smile=ATM_vol + kurtosis_1 * ((K - S) / S) ** 2
    else:
        smile=ATM_vol + kurtosis_2 * ((K - S) / S) ** 2
    
    flattening_factor = np.exp(-decay * T)
    IV = smile * flattening_factor
    return IV

channels, df_options, df_futures, df_spot, option_underlying_ticker_map, future_underlying_ticker_map = get_data()


price_types = ["mid", "bid", "ask"]
class DummyEngine:
    def evaluate(self, x):
        return 0

interest_rate_config = {"engine" : DummyEngine(),
                        "use_ws_response" : False} 
dividend_rate_config = {"engine" : DummyEngine(),
                        "use_ws_response" : False} 

spot_config = {"object" : instruments.Spot,
                "data" : df_spot,
                "price_types" : price_types,
                "valid_price_checker" : main_utils.ValidPriceChecker(50)}

futures_config = {"object" : instruments.Future,
                    "data" : df_futures,
                    "price_types" : price_types,
                    "underlying_map" : future_underlying_ticker_map,
                    "underlying_px_type" : "mid", #{p : "mid" for p in ["bid", "ask", "mid"]},
                    "valid_price_checker" : main_utils.ValidPriceChecker(50),
                    "interest_rate_config" : interest_rate_config,
                    "dividend_rate_config" : dividend_rate_config
                    }

options_config = {"object" : instruments.OptionInverted,
                    "data" : df_options,
                    "price_types" : price_types,
                    "underlying_map": option_underlying_ticker_map,
                    "underyling_price_type" : "mid", #{p : "mid" for p in ["bid", "ask", "mid"]},
                    "engine": black.Engine,
                    "valid_price_checker" : main_utils.ValidPriceChecker(50),
                    "interest_rate_config" : interest_rate_config,
                    "dividend_rate_config" : dividend_rate_config
                    }




instruments_config = {"options" : options_config,
                        "futures" : futures_config,
                        "spot"    : spot_config,
                        }
instrument_manager = builders_instruments.create_instrument_manager(instruments_config)


#%%
spot = df_spot[[]]

import numpy as np

expiration_dt = [datetime(2025, 9,10), datetime(2025, 10,10), datetime(2025, 12,10), datetime(2026, 2,10)]

expiration_dates_ql = [ql.Date(dt.day, dt.month, dt.year) for dt in expiration_dt]

calculation_date = ql.Date(datetime.now().day, datetime.now().month, datetime.now().year)
        
v0, kappa, theta, rho, sigma = 0.01, 0.2, 0.02, -0.75, 0.5
dfs=[1.]
futures_exp_dates = [calculation_date]
spot_object = list(instrument_manager.spot_instrument_container.objects.values())[0]
spot = spot_object.mid



for futures_object in instrument_manager.futures_instrument_container.objects.values():
    exp_ts = futures_object.expiry
    exp_dt = datetime.fromtimestamp(exp_ts)
    exp_ql = ql.Date(exp_dt.day, exp_dt.month, exp_dt.year)
    dfs.append(futures_object.mid / spot)
    futures_exp_dates.append(exp_ql)
builders_data_classes.create_volatility_data_from_vol_vect(vol_vect_container, default_nTicks)
data_container = data_container["mid"]
xyz = np.column_stack(data_container.vol_vector.data())

def getRectStrikesExpiries(xyz) -> Tuple[np.ndarray, ...]:
    print(len(np.unique(xyz[:, 0])))
    strikes, expiries, vol = xyz[:,0], xyz[:,1], xyz[:,2]
    exp = np.unique(expiries)
    unique, counts = np.unique(strikes, return_counts=True)
    k = unique[counts >= exp.size]
    
    xyz = xyz[np.isin(xyz[:, 0], k)]
    xyz = xyz[np.isin(xyz[:, 1], exp)]
    
    return xyz


xyz = getRectStrikesExpiries(xyz)

strikes = np.unique(xyz[:, 0])
expiries = np.unique(xyz[:, 1])
vol_grid = xyz[:, 2].reshape(len(strikes), len(expiries))
print(vol_grid)
expiration_dt = [datetime.fromtimestamp(ts) for ts in expiries]
expiration_dates_ql = [ql.Date(dt.day, dt.month, dt.year) for dt in expiration_dt]



implied_vols = ql.Matrix(vol_grid.shape[0], vol_grid.shape[1])


for i, _ in enumerate(strikes):
    for j, _ in enumerate(expiries):
        implied_vols[i][j] = vol_grid[i][j]


calendar = ql.UnitedStates(ql.UnitedStates.NYSE)
day_count = ql.Actual365Fixed()
black_var_surface = ql.BlackVarianceSurface(calculation_date,
                                            calendar,
                                            expiration_dates_ql,
                                            strikes.tolist(),
                                            implied_vols,
                                            day_count
                                            )


ql.Settings.instance().evaluationDate = calculation_date

# Ensure you explicitly add the reference date with discount 1.0
futures_exp_dates = [calculation_date] + futures_exp_dates
dfs = [1.0] + dfs  # Ensure first discount = 1.0


calendar = ql.NullCalendar()
curve = ql.DiscountCurve(futures_exp_dates, dfs, ql.Actual360())
interest_ts = ql.YieldTermStructureHandle(curve)

dividend_ts = ql.YieldTermStructureHandle(ql.FlatForward(calculation_date, ql.QuoteHandle(ql.SimpleQuote(0.0)), ql.Actual365Fixed())),  # No dividend yield
process = ql.HestonProcess(interest_ts, dividend_ts,
                           ql.QuoteHandle(ql.SimpleQuote(spot)),
                           v0, kappa, theta, sigma, rho)

model = ql.HestonModel(process)
engine = ql.AnalyticHestonEngine(model)

#%%


def generate_synthetic_surface(market_params, S, k, t):
    ATM_vol = market_params["ATM_vol"]
    kurtosis_1 = market_params["kurtosis_1"]
    kurtosis_2 = market_params["kurtosis_2"]
    decay = market_params["decay"]
    vols=[]
    
    for Ki, T in zip(k,t):
        vol_i=[]
        for K in Ki:
            if K < S:
                smile=ATM_vol + kurtosis_1 * ((K - S) / S) ** 2
            else:
                smile=ATM_vol + kurtosis_2 * ((K - S) / S) ** 2
            
            flattening_factor = np.exp(-decay * T)
            IV = smile * flattening_factor
            vol_i.append(IV) 
        vols.append(vol_i)
    return vols


atm = 120
expiries = 4
max_strikes = 9  # must be > 8 as per your requirement

# Decreasing number of strikes per expiry
strikes_per_expiry = [max_strikes - i for i in range(expiries)]  # [9, 8, 7, 6]

strike_step = 2  # spacing between strikes
strike_lists = []

for n in strikes_per_expiry:
    half = n // 2
    # Center around ATM, offset evenly
    if n % 2 == 1:
        strikes = [atm + (i - half) * strike_step for i in range(n)]
    else:
        strikes = [atm + (i - half + 0.5) * strike_step for i in range(n)]
    # Only include strikes > 8
    strikes = [s for s in strikes if s > 8]
    strike_lists.append(strikes)

# Result
for i, expiry_strikes in enumerate(strike_lists, 1):
    print(f"Expiry {i}: {expiry_strikes}")

vol_params = {"ATM_vol" : 0.65,
              "kurtosis_1" : 1.05,
              "kurtosis_2" : 0.35,
              "decay" : 0.3
              }

vols = generate_synthetic_surface(vol_params, spot, strike_lists, dt_y)


#%%
import QuantLib as ql
import math


import numpy as np
import time
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
plt.rcParams['figure.figsize']=(15,7)
plt.style.use("dark_background")
from matplotlib import cm
import gc


total_seconds = 0

day_count = ql.Actual365Fixed()
calendar = ql.UnitedStates(ql.UnitedStates.NYSE)

calculation_date = ql.Date(6, 11, 2015)

spot = 659.37
ql.Settings.instance().evaluationDate = calculation_date

dividend_yield = ql.QuoteHandle(ql.SimpleQuote(0.0))
risk_free_rate = 0.01
dividend_rate = 0.0
flat_ts = ql.YieldTermStructureHandle(
    ql.FlatForward(calculation_date, risk_free_rate, day_count))
dividend_ts = ql.YieldTermStructureHandle(
    ql.FlatForward(calculation_date, dividend_rate, day_count))



"""
expiration_dates = [ql.Date(9,12,2021), ql.Date(9,1,2022), ql.Date(9,2,2022),
                    ql.Date(9,3,2022), ql.Date(9,4,2022), ql.Date(9,5,2022),
                    ql.Date(9,6,2022), ql.Date(9,7,2022), ql.Date(9,8,2022),
                    ql.Date(9,9,2022), ql.Date(9,10,2022), ql.Date(9,11,2022),
                    ql.Date(9,12,2022), ql.Date(9,1,2023), ql.Date(9,2,2023),
                    ql.Date(9,3,2023), ql.Date(9,4,2023), ql.Date(9,5,2023),
                    ql.Date(9,6,2023), ql.Date(9,7,2023), ql.Date(9,8,2023),
                    ql.Date(9,9,2023), ql.Date(9,10,2023), ql.Date(9,11,2023)]


strikes_data = {
    ql.Date(9,12,2021): [527.50, 560.46, 593.43, 626.40, 659.37, 692.34],
    ql.Date(9,1,2022): [527.50, 560.46, 593.43, 626.40, 659.37, 692.34, 725.31],
    ql.Date(9,2,2022): [560.46, 593.43, 626.40, 659.37, 692.34, 725.31],
    ql.Date(9,3,2022): [527.50, 560.46, 593.43, 626.40, 659.37, 692.34, 725.31, 758.28],
    ql.Date(9,4,2022): [560.46, 593.43, 626.40, 659.37, 692.34, 725.31],
    ql.Date(9,5,2022): [527.50, 560.46, 593.43, 626.40, 659.37, 692.34, 725.31],
    ql.Date(9,6,2022): [593.43, 626.40, 659.37, 692.34, 725.31],
    ql.Date(9,7,2022): [527.50, 560.46, 593.43, 626.40, 659.37, 692.34, 725.31, 758.28],
    ql.Date(9,8,2022): [560.46, 593.43, 626.40, 659.37, 692.34],
    ql.Date(9,9,2022): [527.50, 560.46, 593.43, 626.40, 659.37, 692.34, 725.31],
    ql.Date(9,10,2022): [593.43, 626.40, 659.37, 692.34, 725.31, 758.28],
    ql.Date(9,11,2022): [527.50, 560.46, 593.43, 626.40, 659.37, 692.34, 725.31],
    ql.Date(9,12,2022): [560.46, 593.43, 626.40, 659.37, 692.34, 725.31],
    ql.Date(9,1,2023): [527.50, 560.46, 593.43, 626.40, 659.37, 692.34, 725.31, 758.28],
    ql.Date(9,2,2023): [560.46, 593.43, 626.40, 659.37, 692.34],
    ql.Date(9,3,2023): [527.50, 560.46, 593.43, 626.40, 659.37, 692.34, 725.31],
    ql.Date(9,4,2023): [593.43, 626.40, 659.37, 692.34, 725.31, 758.28],
    ql.Date(9,5,2023): [527.50, 560.46, 593.43, 626.40, 659.37, 692.34],
    ql.Date(9,6,2023): [560.46, 593.43, 626.40, 659.37, 692.34, 725.31],
    ql.Date(9,7,2023): [527.50, 560.46, 593.43, 626.40, 659.37, 692.34, 725.31, 758.28],
    ql.Date(9,8,2023): [560.46, 593.43, 626.40, 659.37, 692.34],
    ql.Date(9,9,2023): [527.50, 560.46, 593.43, 626.40, 659.37, 692.34, 725.31],
    ql.Date(9,10,2023): [593.43, 626.40, 659.37, 692.34, 725.31, 758.28],
    ql.Date(9,11,2023): [527.50, 560.46, 593.43, 626.40, 659.37, 692.34]
}


vol_data = {
    ql.Date(9,12,2021): [0.37819, 0.34177, 0.30394, 0.27832, 0.26453, 0.25916],
    ql.Date(9,1,2022): [0.3445, 0.31769, 0.2933, 0.27614, 0.26575, 0.25729, 0.25228],
    ql.Date(9,2,2022): [0.37419, 0.35372, 0.33729, 0.32492, 0.31601, 0.30883],
    ql.Date(9,3,2022): [0.37498, 0.35847, 0.34475, 0.33399, 0.32715, 0.31943, 0.31098, 0.30506],
    ql.Date(9,4,2022): [0.35941, 0.34516, 0.33296, 0.32275, 0.31867, 0.30969],
    ql.Date(9,5,2022): [0.35521, 0.34242, 0.33154, 0.3219, 0.31948, 0.31096, 0.30424],
    ql.Date(9,6,2022): [0.35442, 0.34267, 0.33288, 0.32374, 0.32245],
    ql.Date(9,7,2022): [0.35384, 0.34286, 0.33386, 0.32507, 0.3246, 0.31745, 0.31135, 0.306],
    ql.Date(9,8,2022): [0.35338, 0.343, 0.33464, 0.32614, 0.3263],
    ql.Date(9,9,2022): [0.35301, 0.34312, 0.33526, 0.32698, 0.32766, 0.32132, 0.31558],
    ql.Date(9,10,2022): [0.35272, 0.34322, 0.33574, 0.32765, 0.32873, 0.32267],
    ql.Date(9,11,2022): [0.35246, 0.3433, 0.33617, 0.32822, 0.32965, 0.32383, 0.31831],
    ql.Date(9,12,2022): [0.35226, 0.34336, 0.33651, 0.32869, 0.3304, 0.32477],
    ql.Date(9,1,2023): [0.35207, 0.34342, 0.33681, 0.32911, 0.33106, 0.32561, 0.32025, 0.3155],
    ql.Date(9,2,2023): [0.35171, 0.34327, 0.33679, 0.32931, 0.3319],
    ql.Date(9,3,2023): [0.35128, 0.343, 0.33658, 0.32937, 0.33276, 0.32769, 0.32255],
    ql.Date(9,4,2023): [0.35086, 0.34274, 0.33637, 0.32943, 0.3336, 0.32872],
    ql.Date(9,5,2023): [0.35049, 0.34252, 0.33618, 0.32948, 0.33432, 0.32959],
    ql.Date(9,6,2023): [0.35016, 0.34231, 0.33602, 0.32953, 0.33498, 0.3304],
    ql.Date(9,7,2023): [0.34986, 0.34213, 0.33587, 0.32957, 0.33556, 0.3311, 0.32631, 0.32217],
    ql.Date(9,8,2023): [0.34959, 0.34196, 0.33573, 0.32961, 0.3361],
    ql.Date(9,9,2023): [0.34934, 0.34181, 0.33561, 0.32964, 0.33658, 0.33235, 0.32769],
    ql.Date(9,10,2023): [0.34912, 0.34167, 0.3355, 0.32967, 0.33701, 0.33288],
    ql.Date(9,11,2023): [0.34891, 0.34154, 0.33539, 0.3297, 0.33742, 0.33337]
}


all_strikes = set()
for strikes in strikes_data.values():
    all_strikes.update(strikes)
all_strikes = sorted(all_strikes)
n=10000
for i in range(n):

    s = time.time()
    implied_vols = ql.Matrix(len(all_strikes), len(expiration_dates))
    for j, date in enumerate(expiration_dates):
        date_strikes = strikes_data[date]
        date_vols = vol_data[date]
        for i, strike in enumerate(all_strikes):
            if strike in date_strikes:
                idx = date_strikes.index(strike)
                implied_vols[i][j] = date_vols[idx]
            else:
                implied_vols[i][j] = np.nan  # or use ql.Null<Real>()

    black_var_surface = ql.BlackVarianceSurface(
        calculation_date, calendar,
        expiration_dates, all_strikes,
        implied_vols, day_count)

    black_var_surface.enableExtrapolation()

    strikes_grid = strikes_grid = np.linspace(min(all_strikes)*0.8, max(all_strikes)*1.2, 100)
    expiry = 1.0 

    implied_vols = [black_var_surface.blackVol(expiry, s)for s in strikes_grid]
    total_seconds+=time.time() - s
print(f"total_seconds: {total_seconds}")
print(f"per sec: {n/total_seconds}")
"""
expiration_dates = [ql.Date(6,12,2015), ql.Date(6,1,2016), ql.Date(6,2,2016),
                    ql.Date(6,3,2016), ql.Date(6,4,2016), ql.Date(6,5,2016), 
                    ql.Date(6,6,2016), ql.Date(6,7,2016), ql.Date(6,8,2016),
                    ql.Date(6,9,2016), ql.Date(6,10,2016), ql.Date(6,11,2016), 
                    ql.Date(6,12,2016), ql.Date(6,1,2017), ql.Date(6,2,2017),
                    ql.Date(6,3,2017), ql.Date(6,4,2017), ql.Date(6,5,2017), 
                    ql.Date(6,6,2017), ql.Date(6,7,2017), ql.Date(6,8,2017),
                    ql.Date(6,9,2017), ql.Date(6,10,2017), ql.Date(6,11,2017)]
strikes = [527.50, 560.46, 593.43, 626.40, 659.37, 692.34, 725.31, 758.28]
data = [
[0.37819, 0.34177, 0.30394, 0.27832, 0.26453, 0.25916, 0.25941, 0.26127],
[0.3445, 0.31769, 0.2933, 0.27614, 0.26575, 0.25729, 0.25228, 0.25202],
[0.37419, 0.35372, 0.33729, 0.32492, 0.31601, 0.30883, 0.30036, 0.29568],
[0.37498, 0.35847, 0.34475, 0.33399, 0.32715, 0.31943, 0.31098, 0.30506],
[0.35941, 0.34516, 0.33296, 0.32275, 0.31867, 0.30969, 0.30239, 0.29631],
[0.35521, 0.34242, 0.33154, 0.3219, 0.31948, 0.31096, 0.30424, 0.2984],
[0.35442, 0.34267, 0.33288, 0.32374, 0.32245, 0.31474, 0.30838, 0.30283],
[0.35384, 0.34286, 0.33386, 0.32507, 0.3246, 0.31745, 0.31135, 0.306],
[0.35338, 0.343, 0.33464, 0.32614, 0.3263, 0.31961, 0.31371, 0.30852],
[0.35301, 0.34312, 0.33526, 0.32698, 0.32766, 0.32132, 0.31558, 0.31052],
[0.35272, 0.34322, 0.33574, 0.32765, 0.32873, 0.32267, 0.31705, 0.31209],
[0.35246, 0.3433, 0.33617, 0.32822, 0.32965, 0.32383, 0.31831, 0.31344],
[0.35226, 0.34336, 0.33651, 0.32869, 0.3304, 0.32477, 0.31934, 0.31453],
[0.35207, 0.34342, 0.33681, 0.32911, 0.33106, 0.32561, 0.32025, 0.3155],
[0.35171, 0.34327, 0.33679, 0.32931, 0.3319, 0.32665, 0.32139, 0.31675],
[0.35128, 0.343, 0.33658, 0.32937, 0.33276, 0.32769, 0.32255, 0.31802],
[0.35086, 0.34274, 0.33637, 0.32943, 0.3336, 0.32872, 0.32368, 0.31927],
[0.35049, 0.34252, 0.33618, 0.32948, 0.33432, 0.32959, 0.32465, 0.32034],
[0.35016, 0.34231, 0.33602, 0.32953, 0.33498, 0.3304, 0.32554, 0.32132],
[0.34986, 0.34213, 0.33587, 0.32957, 0.33556, 0.3311, 0.32631, 0.32217],
[0.34959, 0.34196, 0.33573, 0.32961, 0.3361, 0.33176, 0.32704, 0.32296],
[0.34934, 0.34181, 0.33561, 0.32964, 0.33658, 0.33235, 0.32769, 0.32368],
[0.34912, 0.34167, 0.3355, 0.32967, 0.33701, 0.33288, 0.32827, 0.32432],
[0.34891, 0.34154, 0.33539, 0.3297, 0.33742, 0.33337, 0.32881, 0.32492]]

n=100

for i in range(n):
    s = time.time()
    implied_vols = ql.Matrix(len(strikes), len(expiration_dates))
    for i in range(implied_vols.rows()):
        for j in range(implied_vols.columns()):
            implied_vols[i][j] = data[j][i]
    black_var_surface = ql.BlackVarianceSurface(
        calculation_date, calendar, 
        expiration_dates, strikes, 
        implied_vols, day_count) 

    strike = 600.0
    expiry = 1.2 # years
    """
    black_var_surface.blackVol(expiry, strike)


    strikes_grid = np.arange(strikes[0], strikes[-1],10)
    expiry = 1.0 # years
    implied_vols = [black_var_surface.blackVol(expiry, s) 
                    for s in strikes_grid] # can interpolate here
    actual_data = data[11] # cherry picked the data for given expiry

    fig, ax = plt.subplots()
    ax.plot(strikes_grid, implied_vols, label="Black Surface")
    ax.plot(strikes, actual_data, "o", label="Actual")
    ax.set_xlabel("Strikes", size=12)
    ax.set_ylabel("Vols", size=12)
    legend = ax.legend(loc="upper right")
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    """

    plot_years = np.arange(0, 2, 0.1)
    plot_strikes = np.arange(535, 750, 1)

    X, Y = np.meshgrid(plot_strikes, plot_years)
    Z = np.array([black_var_surface.blackVol(float(y), float(x)) 
                for xr, yr in zip(X, Y) 
                    for x, y in zip(xr,yr) ]
                ).reshape(len(X), len(X[0]))
    total_seconds+=time.time() - s
    
    
print(f"total_seconds: {total_seconds}")
print(f"per sec: {n/total_seconds}")


#%%
surf = ax.plot_surface(X,Y,Z, rstride=1, cstride=1, cmap=cm.coolwarm, 
                linewidth=0.1)
fig.colorbar(surf, shrink=0.5, aspect=5)

#%%


implied_vols = [black_var_surface.blackVol(expiry, s) for s in strikes_grid]

target_date = calculation_date + ql.Period(1, ql.Years)
closest_date = min(expiration_dates, key=lambda d: abs(day_count.yearFraction(calculation_date, d) - expiry))
actual_strikes = strikes_data[closest_date]
actual_vols = vol_data[closest_date]


fig, ax = plt.subplots()
ax.plot(strikes_grid, implied_vols, label="Black Surface")
ax.plot(actual_strikes, actual_vols, "o", label="Actual")
ax.set_xlabel("Strikes", size=12)
ax.set_ylabel("Vols", size=12)
legend = ax.legend(loc="upper right")

plot_years = [day_count.yearFraction(calculation_date, d) for d in expiration_dates]
plot_strikes = all_strikes

#%%

X, Y = np.meshgrid(plot_strikes, plot_years)
Z = np.array([black_var_surface.blackVol(y, x)
              for xr, yr in zip(X, Y)
                  for x, y in zip(xr,yr)]
             ).reshape(len(X), len(X[0]))

print(Z)

#%%

fig = plt.figure()
ax = fig.add_subplot(projection='3d')



surf = ax.plot_surface(X,Y,Z, rstride=1, cstride=1, cmap=cm.coolwarm,
                linewidth=0.1)
fig.colorbar(surf, shrink=0.5, aspect=5)
plt.title("Volatility Surface with Max 6 Strikes/Expiry and Max 6 Expiries/Strike")
plt.show()

# Print some diagnostics
print("Strikes usage across expiries:")
for strike, count in strike_usage.items():
    print(f"Strike {strike}: appears in {count} expiries")

print("\nStrikes per expiry:")
for date in expiration_dates:
    print(f"{date}: {len(strikes_data[date])} strikes")
    
    
#%%%


v0 = 0.01; kappa = 0.2; theta = 0.02; rho = -0.75; sigma = 0.5

process = ql.HestonProcess(flat_ts, dividend_ts, 
                           ql.QuoteHandle(ql.SimpleQuote(spot)), 
                           v0, kappa, theta, sigma, rho)
model = ql.HestonModel(process)
engine = ql.AnalyticHestonEngine(model) 
heston_helpers = []
black_var_surface.setInterpolation("bicubic")
one_year_idx = 11 
date = expiration_dates[one_year_idx]
for j, s in enumerate(strikes):
    t = (date - calculation_date)
    p = ql.Period(t, ql.Days)
    #sigma = list(vol_data.values())[one_year_idx][j]
    print(t)
    sigma = black_var_surface.blackVol(t/365.25, s)
    print(sigma)
    helper = ql.HestonModelHelper(p, calendar, spot, s, 
                                  ql.QuoteHandle(ql.SimpleQuote(sigma)),
                                  flat_ts, 
                                  dividend_ts)
    helper.setPricingEngine(engine)
    heston_helpers.append(helper)

lm = ql.LevenbergMarquardt(1e-8, 1e-8, 1e-8)
model.calibrate(heston_helpers, lm, 
                 ql.EndCriteria(500, 50, 1.0e-8,1.0e-8, 1.0e-8))
theta, kappa, sigma, rho, v0 = model.params()