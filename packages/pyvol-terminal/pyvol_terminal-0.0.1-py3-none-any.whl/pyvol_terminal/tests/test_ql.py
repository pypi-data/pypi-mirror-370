#%%


import QuantLib as ql
from datetime import datetime
import numpy as np
import pandas as pd
import examples.deribit.generate_synthetic_data as gen_syn_data 
import json 
from pyvol_terminal.engines import interpolation_engines
import Heston_COS_METHOD

def get_saved_data():
    df_options = pd.read_csv("df_options.csv")
    df_futures = pd.read_csv("df_futures.csv")
    df_spot = pd.read_csv("df_spot.csv")
    
    
    #expiry = df_options["expiry"].unique()[:8]
    df_options = df_options[(df_options["strike"] <= 100_000) & (df_options["strike"] >= 70_000)]
    df_options = df_options[df_options["strike"] % 5000 == 0]
    
    with open("option_underlying_ticker_map.json", "r") as file:
        option_underlying_ticker_map = json.load(file)
        
    with open("future_underlying_ticker_map.json", "r") as file:
        future_underlying_ticker_map = json.load(file)

    with open("channels.txt", "r") as file:
        channels = [line.strip() for line in file]  
        
    return channels, df_options, df_futures, df_spot, option_underlying_ticker_map, future_underlying_ticker_map



channels, df_options, df_futures, df_spot, option_underlying_ticker_map, future_underlying_ticker_map = get_saved_data()


vol_params = {"ATM_vol" : 0.65,
            "kurtosis_1" : 0.55,
            "kurtosis_2" : 0.2,
            "decay" : 0.1}


df_options, df_futures, df_spot = gen_syn_data.generate_synth_data(vol_params, df_options, df_futures, df_spot)

def create_matrices(df):
    x = df["strike"]
    y = df["expiry"]
    z = df["mid_iv"]

    instrument_names = df["instrument_name"].to_list()
    
    x_unique = np.unique(x)
    y_unique = np.unique(y)
    
    X_grid, Y_grid = np.meshgrid(x_unique, y_unique)
    Z_grid = np.full_like(X_grid, np.nan)
    name_index_map = {}
    for xi, yi, zi, name in zip(x, y, z, instrument_names):
        i = np.where(y_unique == yi)[0][0] 
        j = np.where(x_unique == xi)[0][0] 
        Z_grid[i, j] = zi
        name_index_map[name] = (i,j)
    
    missing_points = []
    
    for i in range(Z_grid.shape[0]):
        for j in range(Z_grid.shape[1]):
            if np.isnan(Z_grid[i,j]):
                missing_points.append((i,j))

    return X_grid, Y_grid, Z_grid, name_index_map , missing_points

X_grid, Y_grid, Z_grid, name_index_map, missing_points = create_matrices(df_options)

X_flat = X_grid.flatten()
Y_flat = Y_grid.flatten()
Z_flat = Z_grid.flatten()

mask = ~np.isnan(Z_flat)

X_flat, Y_flat, Z_flat = X_flat[mask], Y_flat[mask], Z_flat[mask]


interpolator = interpolation_engines.CustomBSplineInterpolator()
interpolator.fit(X_flat, Y_flat, Z_flat)

xi = X_grid.flatten()
yi = Y_grid.flatten()

data = interpolator.evaluate(xi, yi)


day_count = ql.Actual365Fixed()
calendar = ql.UnitedStates(m=1)

t_0 = 1743506630.313821
dt_0 = datetime.fromtimestamp(t_0)

calculation_date = ql.Date(dt_0.day, dt_0.month, dt_0.year)
spot = 0.5 * (df_spot['bids'].item() + df_spot['asks'].item())
ql.Settings.instance().evaluationDate = calculation_date


risk_free_rate = 0.01
dividend_rate = 0.00
dividend_yield = ql.QuoteHandle(ql.SimpleQuote(0.0))

flat_ts = ql.YieldTermStructureHandle(ql.FlatForward(calculation_date, risk_free_rate, day_count))
dividend_ts = ql.YieldTermStructureHandle(ql.FlatForward(calculation_date, dividend_rate, day_count))

strikes = np.unique(X_grid)

expiration_ts = np.unique(Y_grid)

expiration_dt = [datetime.fromtimestamp(ts) for ts in expiration_ts]    

expiration_dates = [ql.Date(dt.day, dt.month, dt.year) for dt in expiration_dt]

v0, kappa, theta, rho, sigma = 0.01, 0.2, 0.02, -0.75, 0.5

process = ql.HestonProcess(flat_ts, dividend_ts,
                           ql.QuoteHandle(ql.SimpleQuote(spot)),
                           v0, kappa, theta, sigma, rho)

model = ql.HestonModel(process)
engine = ql.AnalyticHestonEngine(model)
heston_helpers = []


for j, date in enumerate(expiration_dates):
    for i, s in enumerate(strikes):
        t = (date - calculation_date)
        p = ql.Period(t, ql.Days)
        sigma = data[i][j]
        helper = ql.HestonModelHelper(p, calendar, spot, s,
                                    ql.QuoteHandle(ql.SimpleQuote(sigma)),
                                    flat_ts,
                                    dividend_ts)
        helper.setPricingEngine(engine)
        heston_helpers.append(helper)
lm = ql.LevenbergMarquardt(1e-8, 1e-8, 1e-8)
model.calibrate(heston_helpers, lm, ql.EndCriteria(500, 50, 1.0e-8, 1.0e-8, 1.0e-8))
theta, kappa, sigma, rho, v0 = model.params()

print ("\ntheta = %f, kappa = %f, sigma = %f, rho = %f, v0 = %f" % (theta, kappa, sigma, rho, v0))
avg = 0.0

print ("%15s %15s %15s %20s" % (
    "Strikes", "Market Value",
     "Model Value", "Relative Error (%)"))
print ("="*70)
for i, opt in enumerate(heston_helpers):
    err = (opt.modelValue()/opt.marketValue() - 1.0)
    print ("%15.2f %15.5f %20.7f " % (
        opt.marketValue(),
        opt.modelValue(),
        100.0*(opt.modelValue()/opt.marketValue() - 1.0)))
    avg += abs(err)
avg = avg*100.0/len(heston_helpers)
print ("-"*70)
print ("Average Abs Error (%%) : %5.3f" % (avg))
# %%

N = 100
L = 20
r = 0
q = 0

expiry_years = (Y_flat - t_0) /3600 / 24/365


riskFreeTS = ql.YieldTermStructureHandle(ql.FlatForward(calculation_date, 0.05, ql.Actual365Fixed()))
dividendTS = ql.YieldTermStructureHandle(ql.FlatForward(calculation_date, 0.01, ql.Actual365Fixed()))

initialValue = ql.QuoteHandle(ql.SimpleQuote(spot))


hestonProcess = ql.HestonProcess(riskFreeTS, dividendTS, initialValue, v0, kappa, theta, sigma, rho)
hestonModel = ql.HestonModel(hestonProcess)

engine = ql.AnalyticHestonEngine(hestonModel)



#%%
flags = [1 if k > spot else 1 for k in X_flat]


expiration_dt_flat = [datetime.fromtimestamp(ts) for ts in Y_flat]    

expiration_dates_flat = [ql.Date(dt.day, dt.month, dt.year) for dt in expiration_dt_flat]


prices = Heston_COS_METHOD.heston_cosine_method(spot, X_flat, expiry_years, N, L, r, q, theta, v0, sigma, rho, kappa, flags)

for idx, price in enumerate(prices.flatten()):
    
    strike = X_flat[idx]
    if strike > spot:
        ql_opt_type = ql.Option.Call
    else:
        ql_opt_type = ql.Option.Put
    
    payoff = ql.PlainVanillaPayoff(ql_opt_type, strike)
    exercise = ql.EuropeanExercise(expiration_dates_flat[idx])
    europeanOption = ql.VanillaOption(payoff, exercise)

    europeanOption.setPricingEngine(engine)
    
    print("")
    print(f"mine: {price}, ql: {europeanOption.NPV()}")
#%%



volTS = ql.BlackVolTermStructureHandle(ql.BlackConstantVol(calculation_date, ql.TARGET(), 0, ql.Actual360()))
process = ql.GeneralizedBlackScholesProcess(initialValue, dividendTS, riskFreeTS, volTS)
europeanOption.impliedVolatility(europeanOption.NPV(), process)

#%%%
from examples.deribit import generate_synthetic_data
vol_params = {"ATM_vol" : 0.65,
                           "kurtosis_1" : 0.55,
                           "kurtosis_2" : 0.2,
                            "decay" : 0.1}


channels, df_options, df_futures, df_spot, option_underlying_ticker_map, future_underlying_ticker_map = generate_synthetic_data.get_saved_data()
df_options, df_futures, df_spot = generate_synthetic_data.generate_synth_data(vol_params, df_options, df_futures, df_spot)
messages_options, messages_futures, messages_spot = generate_synthetic_data.create_starting_messages(df_options, df_futures, df_spot)



