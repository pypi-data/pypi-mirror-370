from __future__ import annotations 
from typing import List, Optional, Tuple, Union, Dict, TYPE_CHECKING, Callable, Any, Set
import math
from . import base
import numpy as np
from py_lets_be_rational.normaldistribution import norm_cdf, norm_pdf

import py_vollib_vectorized
from .base import OptionPricingModel

class BlackScholes(OptionPricingModel):
    def __init__(self, S: float, K: float, t: float, r: float, q: float, sigma: float, flag: int):
        self.S = S
        self.K = K
        self.t = t
        self.r = r
        self.q = q
        self.sigma = sigma
        self.flag = flag

    def _calculate_intermediates(self, greeks: Set[str]) -> Dict[str, float]:
        required = set()
        for g in greeks:
            if g in self._GREEK_REQUIREMENTS:
                required.update(self._GREEK_REQUIREMENTS[g])
        
        cache = {}
        if not required:
            return cache
        
        if "d1" in required:
            d1 = (math.log(self.S / self.K) + (self.r - self.q + 0.5 * self.sigma**2) * self.t)
            d1 /= (self.sigma * math.sqrt(self.t))
            cache["d1"] = d1
            
            if "phi_d1" in required:
                cache["phi_d1"] = norm_pdf(d1)
            if "N_flag_d1" in required:
                cache["N_flag_d1"] = norm_cdf(self.flag * d1)
        
        if "d2" in required and "d1" in cache:
            d2 = cache["d1"] - self.sigma * math.sqrt(self.t)
            cache["d2"] = d2
            if "N_flag_d2" in required:
                cache["N_flag_d2"] = norm_cdf(self.flag * d2)
        
        return cache

    def _compute_greeks(self, greeks: Set[str], cache: Dict[str, float]) -> Dict[str, float]:
        results = {}
        discount_q = math.exp(-self.q * self.t)
        discount_r = math.exp(-self.r * self.t)
        
        if "delta" in greeks:
            results["delta"] = self.flag * discount_q * cache["N_flag_d1"]
        if "gamma" in greeks:
            results["gamma"] = discount_q * cache["phi_d1"] / (self.S * self.sigma * math.sqrt(self.t))
        if "vega" in greeks:
            results["vega"] = self.S * discount_q * cache["phi_d1"] * math.sqrt(self.t)
        if "theta" in greeks:
            term1 = -self.S * discount_q * cache["phi_d1"] * self.sigma / (2 * math.sqrt(self.t))
            term2 = -self.flag * self.S * (self.r - self.q) * discount_q * cache["N_flag_d1"]
            term3 = self.flag * self.r * self.K * discount_r * cache["N_flag_d2"]
            results["theta"] = term1 + term2 + term3
        if "rho" in greeks:
            results["rho"] = self.flag * self.K * self.t * discount_r * cache["N_flag_d2"]
        if "price" in greeks:
            results["price"] = self.flag * (
                self.S * discount_q * cache["N_flag_d1"] - 
                self.K * discount_r * cache["N_flag_d2"]
            )
        return results
        
class Engine(base.ABCEuroEngine):
    def __init__(self, strike, expiry, flag, flag_int=None,
                 interest_rate_engine=None, dividend_rate_engine=None):
        super().__init__(strike, expiry, flag, flag_int, interest_rate_engine=interest_rate_engine, dividend_rate_engine=dividend_rate_engine)
        self.dividend_rate_engine = dividend_rate_engine
        self.IVOL_engine = self.IVOL
        self.greek_engine_all = self.get_all_greeks
        self.greeks_engines = {
                               "delta": self.delta,
                               "gamma": self.gamma,
                               "vega": self.vega,
                               "rho" : self.rho,
                               "theta" : self.theta
                              }
    @staticmethod
    def IVOL(price, S, K, t, r, flag, q=0, return_as='numpy', **kwargs):
        return py_vollib_vectorized.vectorized_implied_volatility(price, S, K, t, r, flag, q=q, model='black_scholes_merton',return_as=return_as)
    
    @staticmethod
    def delta(sigma, S, K, t, r, flag, q=0, return_as='numpy', **kwargs):
        d1 = (np.log(S/K) + (r - q + 0.5 * sigma**2) * t) / sigma / np.sqrt(t)
        return flag * np.exp(-q*t) * norm_cdf(-flag*d1, 0, 1)

    @staticmethod
    def gamma(sigma, S, K, t, r, flag, q=0, return_as='numpy', **kwargs):
        d1 = (np.log(S/K) + (r - q + 0.5 * sigma**2) * t) / (sigma * np.sqrt(t))
        return np.exp(-q * t) * norm_pdf(d1) / (S * sigma * np.sqrt(t))

    @staticmethod
    def vega(sigma, S, K, t, r, flag, q=0, return_as='numpy', **kwargs):
        d1 = (np.log(S/K) + (r - q + 0.5 * sigma**2) * t) / (sigma * np.sqrt(t))
        return S * np.exp(-q * t) * norm_pdf(d1) * np.sqrt(t)

    @staticmethod
    def theta(sigma, S, K, t, r, flag, q=0, return_as='numpy', **kwargs):
        d1 = (np.log(S/K) + (r - q + 0.5 * sigma**2) * t) / (sigma * np.sqrt(t))
        d2 = d1 - sigma * np.sqrt(t)
        term1 = - (S * np.exp(-q * t) * norm_pdf(d1) * sigma) / (2 * np.sqrt(t))
        term2 = flag * q * S * np.exp(-q * t) * norm_cdf(flag * d1)
        term3 = - flag * r * K * np.exp(-r * t) * norm_cdf(flag * d2)
        return term1 + term2 + term3

    @staticmethod
    def rho(sigma, S, K, t, r, flag, q=0, return_as='numpy', **kwargs):
        d1 = (np.log(S/K) + (r - q + 0.5 * sigma**2) * t) / (sigma * np.sqrt(t))
        d2 = d1 - sigma * np.sqrt(t)
        return flag * K * t * np.exp(-r * t) * norm_cdf(flag * d2)

    @staticmethod
    def get_all_greeks(sigma, S, K, t, r, flag, q=0, **kwargs):
        d1 = (np.log(S/K) + (r - q + 0.5 * sigma**2) * t) / (sigma * np.sqrt(t))
        d2 = d1 - sigma * np.sqrt(t)
        
        delta = flag * np.exp(-q * t) * norm_cdf(flag * d1)
        gamma = np.exp(-q * t) * norm_pdf(d1) / (S * sigma * np.sqrt(t))
        vega = S * np.exp(-q * t) * norm_pdf(d1) * np.sqrt(t)
        theta = - (S * np.exp(-q * t) * norm_pdf(d1) * sigma) / (2 * np.sqrt(t)) \
                + flag * q * S * np.exp(-q * t) * norm_cdf(flag * d1)\
                - flag * r * K * np.exp(-r * t) * norm_cdf(flag * d2)\
                
        rho = flag * K * t * np.exp(-r * t) * norm_cdf(flag * d2)
        return delta, gamma, vega, theta, rho
    

    @staticmethod
    def PC_parity(S, K, t, r, C=None, P=None, q=0, **kwargs):
        if P is not None:
            return P + S * np.exp(-q * t) - K * np.exp(-r * t)
        elif C is not None:
            return C - (S * np.exp(-q * t) - K * np.exp(-r * t))
        else:
            raise ValueError("Either C or P must be provided")
    
    @staticmethod
    def PC_parity_diff(S, K, t, r, C, P, q=0,):
        return C - P + S * np.exp(-q * t) - K * np.exp(-r * t)
    
    @staticmethod
    def get_implied_yield_from_PC(S, K, t, r, C=None, P=None, q=0, **kwargs):
        q = np.log((C - P + K*np.exp(-r*t))/S)/-t
        return q