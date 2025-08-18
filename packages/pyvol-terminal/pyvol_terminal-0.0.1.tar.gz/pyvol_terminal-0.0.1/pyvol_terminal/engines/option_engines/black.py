from __future__ import annotations 
from typing import List, Optional, Tuple, Union, Dict, TYPE_CHECKING, Callable, Any, Set
from . import base
import numpy as np
from py_lets_be_rational.normaldistribution import norm_cdf, norm_pdf
import py_vollib_vectorized
#from py_vollib.black.implied_volatility import implied_volatility 
from ... import utils
import math


    
class Engine(base.ABCEuroEngine):
    def __init__(self, strike, expiry, flag, flag_int=None, interest_rate_engine=None, **kwargs):
        super().__init__(strike, expiry, flag, flag_int, interest_rate_engine)
        self.IVOL_engine = self.IVOL
        self.greek_engine_all = self.get_all_greeks
        self.t=None
        self.sigma=None
        self.greeks_engines = {"delta": self.delta,
                               "gamma": self.gamma,
                               "vega": self.vega,
                               "rho" : self.rho,
                               "theta" : self.theta
                               }


    @staticmethod
    def IVOL(price, F, K, t, r, flag, return_as='numpy', **kwargs):
            return py_vollib_vectorized.vectorized_implied_volatility_black(price, F, K, r, t, flag, return_as=return_as)
        
    @staticmethod
    def IVOL2222222(price, F, K, t, r, flag, **kwargs):
            return implied_volatility(price, F, K, r, t, flag)

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
    
    @staticmethod
    def greeks(greeks: Set[str], F, K, t, r, flag, **kwargs):
        model = Black76(F, K, t, r, flag)
        return model.calculate(greeks)

    @staticmethod
    def get_all_greeks(sigma, F, K, t, r, flag, **kwargs):
        d1 = (np.log(F/K) + 0.5 * t * sigma**2) / (sigma*math.sqrt(t))
        d2 = d1 - math.sqrt(t)
        
        if flag == 1:
            norm_cdf_d1 = norm_cdf(d1, )
            norm_cdf_d1_flag = norm_cdf_d1
            norm_cdf_d2 = norm_cdf(d2, )
            norm_cdf_d2_flag = norm_cdf_d2
        else:
            norm_cdf_d1= norm_cdf(d1, )
            norm_cdf_d1_flag = 1 - norm_cdf_d1
            norm_cdf_d2= norm_cdf(d2, )
            norm_cdf_d2_flag = 1 - norm_cdf_d2

        delta=flag * math.exp(-r*t)*norm_cdf_d1_flag
        gamma=math.exp(-r * t) * norm_cdf_d1 / (F * sigma * math.sqrt(t))
        vega=F * math.exp(-r*t) * norm_cdf_d1 * math.sqrt(t)
        theta= - F * math.exp(-r*t) * norm_pdf(d1, ) * sigma / (2 * math.sqrt(t)) \
                - flag * r * K *math.exp(-r*t) * norm_cdf_d2_flag + flag* r * F * math.exp(-r*t) * norm_cdf_d1_flag
        rho = -t * flag * (F * norm_cdf_d1_flag - K * norm_cdf_d2_flag)
        return delta, gamma, vega, theta, rho
    
    def calculate_IVOL_cached(self, timestamp, px_option, px_underlying):
        self.t = utils.convert_to_yte(timestamp, self.expiry)       
        self.r = self.interest_rate_engine.evaluate(self.t)
        self.F = px_underlying
        self.sigma = self.IVOL_engine(px_option,
                                      px_underlying,
                                      self.t,
                                      self.r,
                                      self.flag_str,
                                      q=0)
        return self.sigma

    def calculate_IVOL(self, timestamp, px_option, px_underlying):
        yte = utils.convert_to_yte(timestamp, self.expiry)       
        r = self.interest_rate_engine.evaluate(yte)
        return self.IVOL_engine(px_option,
                                px_underlying,
                                self.strike,
                                yte,
                                r,
                                self.flag_str,
                                q=0
                                )

    def calculate_all_greeks(self, timestamp, IVOL, underlying_px):
        yte = utils.convert_to_yte(timestamp, self.expiry)       
        r = self.interest_rate_engine.evaluate(yte)
        args = underlying_px, self.strike, yte, r, self.flag_int
        kwargs = {"q":0}
        return  [Engine.delta(iv, *args, **kwargs) for iv in IVOL], \
                [Engine.gamma(iv, *args, **kwargs) for iv in IVOL], \
                [Engine.vega(iv, *args, **kwargs) for iv in IVOL], \
                [Engine.theta(iv, *args, **kwargs) for iv in IVOL], \
                [Engine.rho(iv, *args, **kwargs) for iv in IVOL], \
                        

    def calculate_all_greeks2(self, timestamp, IVOL, underlying_px):
        yte = utils.convert_to_yte(timestamp, self.expiry)       
        self.r = self.interest_rate_engine.evaluate(yte)
        
        return self.greek_engine_all(IVOL,
                                     underlying_px,
                                     self.strike,
                                     yte,
                                     self.r,
                                     self.flag_int,
                                     q=0
                                    )
    
    def calculate_pair_metrics(self, F, timestamp, C, P):
        yte = utils.convert_to_yte(timestamp, self.expiry)       
        r = self.interest_rate_engine.evaluate(yte)
        
        pcp = Engine.PC_parity_diff(F, self.strike, yte, r, C, P)
        
        implied_yield = Engine.get_implied_yield_from_PC(F, self.strike, yte, r, C, P)
        return pcp, implied_yield
    
    @staticmethod
    def PC_parity(F, K, t, r, C=None, P=None, **kwargs):
        if P:
            return P + (F - K) * math.exp(-r*t)
        else:
            return C - (F - K) * math.exp(-r*t)
        
    @staticmethod
    def PC_parity_diff(F, K, t, r, C, P, **kwargs):
        return C - P - (F - K) * math.exp(-r*t)

    @staticmethod
    def get_implied_yield_from_PC(F, K, t, r, C, P, **kwargs):
        return - np.log((C-P) / (F - K)) / t

    def _calculate_intermediates(self, greeks: Set[str]) -> Dict[str, float]:
        required = set()
        for greek in greeks:
            required.update(self._GREEK_REQUIREMENTS[greek])
        
        cache = {}
        if not required:
            return cache
        
        if "d1" in required:
            d1 = (math.log(self.F / self.strike) + (0.5 * self.sigma**2) * self.t)
            d1 /= (self.sigma * math.sqrt(self.t))
            cache["d1"] = d1
            
            if "phi_d1" in required:
                cache["phi_d1"] = norm_cdf(d1)
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
        if "delta" in greeks:
            results["delta"] = self.flag * math.exp(-self.r * self.t) * cache["N_flag_d1"]
        if "gamma" in greeks:
            results["gamma"] = math.exp(-self.r * self.t) * cache["phi_d1"] / (self.F * self.sigma * math.sqrt(self.t))
        if "vega" in greeks:
            results["vega"] = self.F * math.exp(-self.r * self.t) * cache["phi_d1"] * math.sqrt(self.t)
        if "theta" in greeks:
            term1 = -self.F * math.exp(-self.r * self.t) * cache["phi_d1"] * self.sigma / (2 * math.sqrt(self.t))
            term2 = -self.flag * self.r * self.strike * math.exp(-self.r * self.t) * cache["N_flag_d2"]
            results["theta"] = term1 + term2
        if "rho" in greeks:
            results["rho"] = self.flag * self.strike * self.t * math.exp(-self.r * self.t) * cache["N_flag_d2"]
        if "price" in greeks:
            results["price"] = self.flag * (self.F * cache["N_flag_d1"] - self.strike * math.exp(-self.r * self.t) * cache["N_flag_d2"])
        return results
