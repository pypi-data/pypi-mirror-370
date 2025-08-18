#%%
import timeit




def filter_data(data, lower, upper):
    result = []

    x, y = data.shape[0], len(lower)
    
    for i in range(x):
        keep = True
        for j in range(y):
            val = data[i, j]
            if val < lower[j]:
                keep = False
                break
            if val > upper[j]:
                keep = False
                break
        if keep:
            result.append(data[i])
    return np.array(result)

#%%


import timeit
import math
import numpy as np


def expansion(v1, p1, k2):
    if v1[0] > 0 and v1[1] == 0:
        angle = math.atan2(k2[1] - p1[1], k2[0] - p1[0])

    elif v1[0] < 0 and v1[1] == 0:
        angle = math.atan2(-(k2[1] - p1[1]), -(k2[0] - p1[0]))

    elif v1[0] == 0 and v1[1] > 0:
        angle = math.atan2(-(k2[0] - p1[0]), k2[1] - p1[1])

    elif v1[0] == 0 and v1[1] < 0:
        angle = math.atan2(k2[0] - p1[0], -(k2[1] - p1[1]))
    clockwise_angle = (-angle) % (2 * math.pi)
    return math.degrees(clockwise_angle)



def clockwise_angle(p1, p2, k2):
    v1 = p2 - p1
    v2 = k2 - p1

    dot = np.dot(v1, v2)
    det = v1[0]*v2[1] - v1[1]*v2[0]  
    angle_rad = math.atan2(det, dot) 
    clockwise_angle = (-angle_rad) % (2 * np.pi)
    return math.degrees(clockwise_angle)

p1 = (5, 20)
p2 = (5, 0)

k2 = (18, 30)
v1 = (0, -20)

res = expansion(v1, p1, k2)
print(res)
res = clockwise_angle(np.array(p1), np.array(p2), np.array(k2))
print(res)


#%%

import timeit

setup1 = """
from dataclasses import dataclass
import numpy as np

@dataclass(slots=True, frozen=False)
class OptionGreeks:
    delta: float = np.nan
    gamma: float = np.nan
    vega: float = np.nan
    theta: float = np.nan
    rho: float = np.nan

og = OptionGreeks(0.5, 0.1, 0.2, -0.3, 0.4)
"""

run1 = """
og.vega
"""

setup2 = """
from dataclasses import dataclass
import numpy as np

@dataclass(slots=True, frozen=False)
class OptionGreeks:
    delta: float = np.nan
    gamma: float = np.nan
    _vega: float = np.nan
    theta: float = np.nan
    rho: float = np.nan
    
    @property
    def vega(self):return self._vega

og = OptionGreeks(0.5, 0.1, 0.2, -0.3, 0.4)
"""

run2 = """
og.vega
"""

setup3 = """
from dataclasses import dataclass
import numpy as np

@dataclass(slots=True, frozen=True)
class OptionGreeks:
    delta: float = np.nan
    gamma: float = np.nan
    vega: float = np.nan
    theta: float = np.nan
    rho: float = np.nan

og = OptionGreeks(0.5, 0.1, 0.2, -0.3, 0.4)
"""

run3 = """
og.__getattribute__("vega")
"""



setup4 = """
greeks_dict = {
    'delta': 0.5,
    'gamma': 0.1,
    'vega': 0.2,
    'theta': -0.3,
    'rho': 0.4
}
"""

run4 = """
greeks_dict["vega"]
"""
from dataclasses import dataclass

@dataclass(slots=True)
class Greeks:
    _ptype_idx_map: dict
    _delta: float
    _gamma: float
    _vega: float
    _theta: float
    _rho: float

def make_property(attr_name):
    def prop(self):
        return getattr(self, f"_{attr_name}")
    return property(prop)

for var in ("delta", "gamma", "vega", "theta", "rho"):
    setattr(Greeks, var, make_property(var))

setup5 = """
from __main__ import Greeks
g = Greeks({}, 0.5, 0.1, 0.2, -0.3, 0.4)
"""

run5 = """
g.vega
"""

N = 50000000
t1 = timeit.timeit(run1, setup=setup1, number=N)
t2 = timeit.timeit(run2, setup=setup2, number=N)
#t3 = timeit.timeit(run3, setup=setup3, number=N)
#t4 = timeit.timeit(run4, setup=setup4, number=N)
#t5 = timeit.timeit(run5, setup=setup5, number=N)

print(f"Direct access (slots): {t1:.6f} seconds")
print(f"getattr access (slots): {t2:.6f} seconds")
print(f"getattr access (slots+frozen): {t2:.6f} seconds")
print(f"Dict access: {t4:.6f} seconds")
print(f"Direct access (slots+frozen): {t5:.6f} seconds")

#%%
"""
from py_lets_be_rational.normaldistribution import norm_cdf
import time
discounted_option_price= 10
F=100.
K=105.
r=0.05
t=1
flag="c"

N = 1000000

start1 = time.time()

for _ in range(N):
    for _ in range(2):
        norm_cdf(0.5)

print(time.time() - start1)

import py_vollib_vectorized 
import numpy as np


price= 10
F=100.
K=105.
r=0.05
t=1
flag="c"

from scipy.special import ndtr

start2 = time.time()

for _ in range(N):
    for _ in range(2):
        ndtr(0.5)

print(time.time() - start2)



from scipy.stats import norm

from scipy.special import ndtr

start2 = time.time()
arr = np.array([0.5, 0.6])
for _ in range(N):
    norm.cdf(arr, 0, 1)

print(time.time() - start2)
"""
# %%

#$import numpy as np
#import py_vollib_vectorized




from pprint import pprint
S = 100.
K=102.
t=0.002
r=0.05
q=0.02
flag="c"
iv=0.2

#greeks = py_vollib_vectorized.get_all_greeks(flag, S, K, t, r, iv, model='black_scholes', return_as='dict')
#pprint(greeks)


#%%

import timeit

setup1 = """

d = {i : i for i in range(10)}



"""

run1 = """


for i, j in d.items():
    pass


"""

setup2 = """
d = {i : i for i in range(10)}


"""

run2 = """

for i in d:
    v=d[i]


"""


N = 10000000
t1 = timeit.timeit(run1, setup=setup1, number=N)
t2 = timeit.timeit(run2, setup=setup2, number=N)



print(f"t1: {t1:.6f} seconds")
print(f"t2: {t2:.6f} seconds")

#%%


class StaticClass:
    @staticmethod
    def delta(sigma, F, K, t, r, flag, **kwargs):
        d1 =  1/(sigma*math.sqrt(t)) * (np.log(F/K) + (0.5*sigma**2)*t)
        return flag * math.exp(-r*t)*norm_cdf(flag*d1)

    @staticmethod
    def gamma(sigma, F, K, t, r, flag, **kwargs):
        d1 =  1/(sigma*math.sqrt(t)) * (np.log(F/K) + (0.5*sigma**2)*t)
        return math.exp(-r * t) * norm_cdf(d1) / (F * sigma * math.sqrt(t))

    @staticmethod
    def vega(sigma, F, K, t, r, flag, **kwargs):
        d1 =  1/(sigma*math.sqrt(t)) * (np.log(F/K) + (0.5*sigma**2)*t)
        return F * math.exp(-r*t) * norm_cdf(d1, ) * math.sqrt(t)

    @staticmethod
    def theta(sigma, F, K, t, r, flag, **kwargs):
        d1 =  1/(sigma*math.sqrt(t)) * (np.log(F/K) + (0.5*sigma**2)*t)
        d2 = d1 - math.sqrt(t)
        t1 = - F * math.exp(-r*t) * norm_pdf(d1) * sigma / (2 * math.sqrt(t))
        t2 = - flag * r * K *math.exp(-r*t) * norm_cdf(flag*d2) + flag* r * F * math.exp(-r*t) * norm_cdf(flag*d1)
        return t1 + t2

    @staticmethod
    def rho(sigma, F, K, t, r, flag, **kwargs):
        d1 =  1/(sigma*math.sqrt(t)) * (np.log(F/K) + (0.5*sigma**2)*t)
        d2 = d1 - math.sqrt(t)
        return -t * flag * (F * norm_cdf(flag *sigma) - K * norm_cdf(flag*d2))

    @staticmethod
    def price(sigma, F, K, t, r, flag, **kwargs):
        d1 = F * norm_cdf(flag * (math.log(F / K) / sigma + sigma/2))
        d2 = K * norm_cdf(flag * (math.log(F / K) / sigma - sigma/2))
        return math.exp(-r*t) * (d1 - d2)



# Add this timing test
def time_static_class():
    results = {}
    for greek in greeks:
        fn = getattr(StaticClass, greek)
        results[greek] = fn(**params)
    return results

N = 20000


# Test setup
params = {
    'sigma': 0.2,
    'F': 100,
    'K': 100,
    't': 1,
    'r': 0.05,
    'flag': 1
}
greeks = {'delta', 'gamma', 'vega', 'theta', 'rho', 'price'}


greeks =  {'delta', 'gamma', 'vega', 'theta', 'rho', 'price'}

original = BlackScholesCacheOriginal(**params)
new = BlackScholesCacheNew(**params)

original_time = timeit.timeit(lambda: original.build_cache(greeks), number=N)
new_time = timeit.timeit(lambda: new.build_cache(greeks), number=N)
#static_time = timeit.timeit(time_static_class, number=N)


print(f"Original: {original_time:.5f} seconds")
print(f"New: {new_time:.5f} seconds") 
print(f"Static: {static_time:.5f} seconds")

# %%
# %%

import math
from dataclasses import dataclass
from typing import Dict, Set, Callable
from scipy.stats import norm




@dataclass(frozen=True)
class PricingModelCache:
    sigma: float
    F: float
    K: float
    t: float
    r: float
    flag: int
    model_type: str = "black76"  

    def build_cache(self, greeks: Set[str]) -> Dict[str, float]:
        return IntermediateCalculations.calculate(
            greeks=greeks,
            F=self.F,
            K=self.K,
            sigma=self.sigma,
            t=self.t,
            r=self.r,
            flag=self.flag,
            model_type=self.model_type
        )

@dataclass(frozen=True)
class IntermediateCalculations:
    _calculation_methods = {
        "black_scholes": {
            "d1": lambda F, K, sigma, t, r, **_: (math.log(F / K) + (r + 0.5 * sigma**2) * t) / (sigma * math.sqrt(t)),
            "d2": lambda d1, sigma, t, **_: d1 - sigma * math.sqrt(t),
        },
        "black76": {
            "d1": lambda F, K, sigma, t, **_: (math.log(F / K) + 0.5 * sigma**2 * t) / (sigma * math.sqrt(t)),
            "d2": lambda d1, sigma, t, **_: d1 - sigma * math.sqrt(t),
        }
    }

    _common_methods = {
        "phi_d1": lambda d1, **_: norm.pdf(d1),
        "phi_d2": lambda d2, **_: norm.pdf(d2),
        "N_d1": lambda d1, **_: norm.cdf(d1),
        "N_d2": lambda d2, **_: norm.cdf(d2),
        "N_flag_d1": lambda d1, flag, **_: norm.cdf(flag * d1),
        "N_flag_d2": lambda d2, flag, **_: norm.cdf(flag * d2),
    }

    @classmethod
    def calculate(cls, greeks, F, K, sigma, t, r, flag, model_type):
        greek_requirements = {
            "delta": {"d1", "N_flag_d1"},
            "gamma": {"d1", "phi_d1"},
            "vega": {"d1", "phi_d1"},
            "theta": {"d1", "d2", "phi_d1", "N_flag_d1", "N_flag_d2"},
            "rho": {"d2", "N_flag_d2"},
            "price": {"d1", "d2", "N_flag_d1", "N_flag_d2"},
        }

        required = set()
        for g in greeks:
            required |= greek_requirements.get(g, set())

        cache = {}
        params = {'F': F, 'K': K, 'sigma': sigma, 't': t, 'r': r, 'flag': flag}
        
        if required and "d1" in required:
            cache["d1"] = cls._calculation_methods[model_type]["d1"](**params)
            params.update(cache)

        calculation_order = ["d2", "phi_d1", "phi_d2", "N_d1", "N_d2", "N_flag_d1", "N_flag_d2"]
        for key in calculation_order:
            if key in required and key not in cache:
                if key in cls._calculation_methods[model_type]:
                    cache[key] = cls._calculation_methods[model_type][key](**params)
                else:
                    cache[key] = cls._common_methods[key](**params)
                params[key] = cache[key]

        return cache


import math
import timeit
from dataclasses import dataclass
from scipy.stats import norm
import numpy as np
norm_cdf = norm.cdf
norm_pdf = norm.pdf
# Original implementation
@dataclass(frozen=True)
class BlackScholesCacheOriginal:
    sigma: float
    F: float
    K: float
    t: float
    r: float
    flag: int

    def build_cache(self, greeks: set[str]) -> dict:
        cache = {}
        sigma_sqrt_t = self.sigma * math.sqrt(self.t)
        d1 = (math.log(self.F / self.K) + 0.5 * self.sigma**2 * self.t) / sigma_sqrt_t
        d2 = d1 - sigma_sqrt_t

        requirements = {
            "delta": {"d1", "N_flag_d1"},
            "gamma": {"d1", "phi_d1"},
            "vega": {"d1", "phi_d1"},
            "theta": {"d1", "d2", "phi_d1", "N_flag_d1", "N_flag_d2"},
            "rho": {"d2", "N_flag_d2"},
            "price": {"d1", "d2", "N_flag_d1", "N_flag_d2"},
        }

        required = set()
        for g in greeks:
            required |= requirements.get(g, set())

        if "d1" in required:
            cache["d1"] = d1
        if "d2" in required:
            cache["d2"] = d2
        if "phi_d1" in required:
            cache["phi_d1"] = norm.pdf(d1)
        if "phi_d2" in required:
            cache["phi_d2"] = norm.pdf(d2)
        if "N_d1" in required:
            cache["N_d1"] = norm.cdf(d1)
        if "N_d2" in required:
            cache["N_d2"] = norm.cdf(d2)
        if "N_flag_d1" in required:
            cache["N_flag_d1"] = norm.cdf(self.flag * d1)
        if "N_flag_d2" in required:
            cache["N_flag_d2"] = norm.cdf(self.flag * d2)

        return cache



class StaticClass:
    @staticmethod
    def delta(sigma, F, K, t, r, flag, **kwargs):
        d1 =  1/(sigma*math.sqrt(t)) * (np.log(F/K) + (0.5*sigma**2)*t)
        return flag * math.exp(-r*t)*norm_cdf(flag*d1)

    @staticmethod
    def gamma(sigma, F, K, t, r, flag, **kwargs):
        d1 =  1/(sigma*math.sqrt(t)) * (np.log(F/K) + (0.5*sigma**2)*t)
        return math.exp(-r * t) * norm_pdf(d1) / (F * sigma * math.sqrt(t))

    @staticmethod
    def vega(sigma, F, K, t, r, flag, **kwargs):
        d1 =  1/(sigma*math.sqrt(t)) * (np.log(F/K) + (0.5*sigma**2)*t)
        return F * math.exp(-r*t) * norm_pdf(d1) * math.sqrt(t)

    @staticmethod
    def theta(sigma, F, K, t, r, flag, **kwargs):
        d1 =  1/(sigma*math.sqrt(t)) * (np.log(F/K) + (0.5*sigma**2)*t)
        d2 = d1 - sigma*math.sqrt(t)
        t1 = - F * math.exp(-r*t) * norm_pdf(d1) * sigma / (2 * math.sqrt(t))
        t2 = - flag * r * K *math.exp(-r*t) * norm_cdf(flag*d2) + flag* r * F * math.exp(-r*t) * norm_cdf(flag*d1)
        return t1 + t2

    @staticmethod
    def rho(sigma, F, K, t, r, flag, **kwargs):
        d1 =  1/(sigma*math.sqrt(t)) * (np.log(F/K) + (0.5*sigma**2)*t)
        d2 = d1 - sigma*math.sqrt(t)
        return flag * K * t * math.exp(-r*t) * norm_cdf(flag*d2)

    @staticmethod
    def price(sigma, F, K, t, r, flag, **kwargs):
        d1 = (math.log(F/K) + (r + 0.5*sigma**2)*t) / (sigma*math.sqrt(t))
        d2 = d1 - sigma*math.sqrt(t)
        return flag * (F * norm_cdf(flag*d1) - K * math.exp(-r*t) * norm_cdf(flag*d2))

N=10000

greeks = {'delta', 'gamma', 'vega', 'theta', 'rho', 'price'}


# Test setup
params = {
    'sigma': 0.2,
    'F': 100,
    'K': 100,
    't': 1,
    'r': 0.05,
    'flag': 1
}
pmc = PricingModelCache(**params)


original = BlackScholesCacheOriginal(**params)


original_time = timeit.timeit(lambda: original.build_cache(greeks), number=N)
new_time = timeit.timeit(lambda: pmc.build_cache(greeks), number=N)
#static_time = timeit.timeit(time_static_class, number=N)


print(f"Original: {original_time:.5f} seconds")
print(f"New: {new_time:.5f} seconds") 
