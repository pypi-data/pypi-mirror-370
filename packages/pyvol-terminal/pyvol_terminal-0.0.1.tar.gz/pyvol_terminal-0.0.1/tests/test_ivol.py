#%%

import py_vollib_vectorized
import numpy as np

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


vol_params = {"ATM_vol" : 0.20,
                "kurtosis_1" : 0.55,
                "kurtosis_2" : 0.2,
                "decay" : 0.1
                }


def generate_spread_pct(price, min_spread=0.001, max_spread=0.05):
    inv_price = 1 / price
    norm_inv = (inv_price - inv_price.min()) / (inv_price.max() - inv_price.min())
    return min_spread + norm_inv * (max_spread - min_spread)

mid_prices = np.linspace(5, 30, 30)[::-1]

spread_pcts = generate_spread_pct(mid_prices)
random_noise = np.random.uniform(0.9, 1.1, size=len(mid_prices))
spread_pcts *= random_noise
bids = mid_prices * (1 - spread_pcts / 2)
asks = mid_prices * (1 + spread_pcts / 2)


S = 130.
K = np.linspace(100, 130, 30)
K = [100.]
prices = np.arange(5, 200, dtype=float)
t = 1
r = 0
flag = ['c']
vols=[]
for p in prices:
    vol=100 * py_vollib_vectorized.vectorized_implied_volatility(p, S, K, t, r, flag, q=0, model='black_scholes_merton',return_as='numpy').item()
    vols.append(vol)
import matplotlib.pyplot as plt
plt.plot(prices, vols)
plt.xlabel("Price ($)")
plt.ylabel("IVOL (%)")
plt.show()
#%%
vols_b=[]
vols_a=[]

vols=[]
for k in K:
    vol = generate_synthetic_surface(vol_params, S, k, t)
    vols.append(vol)


for b, a, k in zip(bids, asks, K):
    ivol_b = py_vollib_vectorized.vectorized_implied_volatility(b, S, k, t, r, flag, q=0, model='black_scholes_merton',return_as='numpy').item()
    ivol_a = py_vollib_vectorized.vectorized_implied_volatility(a, S, k, t, r, flag, q=0, model='black_scholes_merton',return_as='numpy').item()
    vols_b.append(ivol_b)
    vols_a.append(ivol_a)

#%%
from scipy.interpolate import make_interp_spline
from scipy.stats import linregress
m = (vols[1] - vols[0]) / (prices[1] - prices[0])

c = vols[0] - m * prices[0] 
slope, intercept, r_value, p_value, std_err = linregress(prices, vols)
spline = make_interp_spline(prices, vols, k=1)

#%%
import matplotlib.pyplot as plt
plt.plot(K, vols_b)
plt.plot(K, vols_a)

plt.show()