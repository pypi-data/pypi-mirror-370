from __future__ import annotations 
from typing import List, Optional, Tuple, Union, Dict, TYPE_CHECKING, Callable, Any
if TYPE_CHECKING:
    from engines.yield_engines.implied_engines import AbstractYieldEngine 

from abc import ABC, abstractmethod
from pyvol_terminal.engines.option_engines import interpolation
import numpy as np
import math
import time
from datetime import datetime
from .. import utils
from dataclasses import dataclass, field, fields
from . import quantities
from ..engines.option_engines.base import ABCEuroEngine



@dataclass(slots=True, frozen=True, kw_only=True)
class _BaseSpecifications:
    ticker: str
    px_quotation: float=None

    
    def __repr__(self):
        cls_name = self.__class__.__name__
        non_none = {f.name: getattr(self, f.name) for f in fields(self) if getattr(self, f.name) is not None}
        args_str = ", ".join(f"{k}={v!r}" for k, v in non_none.items())
        return f"{cls_name}({args_str})"


@dataclass(slots=True, kw_only=True)
class Quotes:
    last_ts: float=np.nan
    px: Dict[str, float]
    size: Dict[str, float]
    
    open_interest: float=np.nan
    
    callbacks: List[Callable]=field(default=list)

    
    def update(self,
               timestamp: float,
               px_bid=None,
               px_ask=None,
               size_bid=None,
               size_ask=None,
               open_interest=None,
                )-> None:
        self.last_ts=timestamp
        
        self.px["bid"]=px_bid
        self.px["ask"]=px_ask
        self.px["mid"]=0.5 * (px_bid + px_ask)

        self.size["bid"]=size_bid
        self.size["ask"]=size_ask

        if not open_interest is None:
            self.open_interest = open_interest
        
    def copy(self):
        return list(self, self.px.keys())
        
    def add_callback(self, callback):
        self.callbacks.append(callback)
    
    def remove_quote_callback(self, callback):
        self.callbacks.remove(callback)
    


class ABCPyVol(ABC):
    
    def update(self, timestamp, px_bid=None, px_ask=None, callbacks=True) -> None: 
        self.update_internal(timestamp, px_bid, px_ask, callbacks)
    
    @abstractmethod
    def update_internal(self): ...


class ABCInstrument(ABCPyVol):
    def __init__(self,
                 specs: _BaseSpecifications,
                 *args, 
                 **kwargs
                 ) -> None:
        super().__init__(*args, **kwargs)
        self.specs=specs
        self.quotes=Quotes()

        self._metric_state_container=[]
        self._child_derivative_callbacks=[]
        self._metric_callbacks=[]
        self._structure_callbacks=[]
        

    def update_quotes(self, *args, **kwargs) -> None:
        self.quotes.update(*args, **kwargs)
        for callback in self.quotes.callbacks:
            callback(self)


    def update_metrics(self):...
                        
    def update_internal(self, *args, **kwargs) -> None:
        self.update_quotes(*args, **kwargs)   
            
        self.update_metrics()
        
        for callback in self._child_derivative_callbacks:
            callback()
        for callback in self._structure_callbacks:
            callback(self)
    
    def add_quote_callback(self, callback):
        self.quotes.add_callback(callback)
    
    def remove_quote_callback(self, callback):
        self.quotes.add_callback(callback)

    def add_child_derivative_callback(self, callback):
        self._child_derivative_callbacks.append(callback)
    
    def remove_child_derivative_callback(self, callback):
        self._child_derivative_callbacks.remove(callback)
    
    def add_structure_callback(self, callback):
        self._structure_callbacks.append(callback)

    def remove_structure_callback(self, callback):
        self._structure_callbacks.remove(callback)

    def add_price_callbacks(self, callback):
        self._price_callbacks.append(callback)
        
    def remove_price_callbacks(self, callback):
        self._price_callbacks.remove(callback)

    def add_metric_callbacks(self, callback):
        self._metric_callbacks.append(callback)
        
    def remove_metric_callbacks(self, callback):
        self._metric_callbacks.remove(callback)
        
    def modify_metric_state(self, metric, state, rebuild=True):
        if state=="add":
            self._metric_state_container.append(metric)
        else:
            self._metric_state_container.remove(metric)
        
        if rebuild:
            self._build_metric_state_container()
    
    def _build_metric_state_container(self):
        ...


@dataclass(slots=True, kw_only=True, frozen=True)
class SpotSpecifications(_BaseSpecifications):
    category: str=field(default="spot", init=False)
  
class Spot(ABCInstrument):
    def __init__(self, specs, *args, **kwargs):
        self.specs=specs
        super().__init__(*args, **kwargs)
    
    def update_metrics(self): ...   


@dataclass(slots=True, kw_only=True, frozen=True)
class DerivativeSpecifications(_BaseSpecifications):
    specs_underlying: _BaseSpecifications=None
    settlement_px_quotation: str=None
    
    def __post_init__(self):
        if self.settlement_px_quotation is None:
            self.settlement_px_quotation=self.px_quotation


class Derivative(ABCInstrument):
    def __init__(self,
                 *args, 
                 **kwargs
                 ):
        self.quotes_underlying: Quotes=None
        super().__init__(*args, **kwargs)

    @abstractmethod
    def update_metrics(self): ...   
    
    @abstractmethod
    def underlying_listener(self): ...
    

@dataclass(slots=True, kw_only=True, frozen=True)
class FutureSpecifications(DerivativeSpecifications):
    expiry: float=None
    category: str=field(default="future", init=False) 

    
class Future(Derivative):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.specs: FutureSpecifications
    
    def update_from_underlying(self, underlying_object):
        self._underlying_pxs=underlying_object.copy()
    
    def get_forward_rate(self):
        yte = utils.convert_unix_maturity_to_years(self.specs.expiry)         
        self.forward_rate = np.log(self / getattr(self.underlying_px, self.underlying_px_type)) / yte
        
    def update_metrics(self):...
    

@dataclass(slots=True, frozen=True, kw_only=True)
class OptionSpecifications(Derivative):
    category: str=field(default="option", init=False)
    expiry: float
    strike: float
    option_type: str
    exercise_style: str
    delivery: str=None
    
    
    def __post_init__(self):
        if self.option_type is not None and self.option_type not in ["c", "p"]:
            raise
        elif self.exercise_style is not None and self.exercise_style not in ["eu", "am"]:
            raise
        elif self.delivery is not None and self.exercise_style not in ["p", "c"]:
            raise


class Option(Derivative):
    def __init__(self,
                 *args,
                 ivol_engine: Any,
                 itm_conversion_engine=None, 
                 **kwargs
                 ) -> None:
        
        super().__init__(*args, **kwargs)
        self.specs: OptionSpecifications
        self.ivol_engine: ABCEuroEngine=ivol_engine

        self.states={px_type : quantities.OptionState({"flag" : self.specs.option_type,
                                                       "strike" : self.specs.option_type
                                                       }) for px_type in ["bid", "ask", "mid"]
                     }
        self.ivol_metrics: List[quantities.IVOLMetrics]
        self.itm_conversion_engine = itm_conversion_engine if itm_conversion_engine is not None else interpolation.ITMConversionEngine()
        
        self.listening_px_types = {"option" : [],
                                   "underlying" : []
                                   }
        
        self.underlying_target_px: List[str]=[]
        
        self._cached_underlying_quotes: Dict[str, float] = {"bid" : np.nan,
                                                            "ask" : np.nan,
                                                            "mid" : np.nan
                                                            }
        self._underlying_px_targets=set()
        
        self._ptype_idx_map = {"px_bid" : 0,
                               "px_ask" : 1,
                               "px_mid" : 2
                               }
    
    def refresh_quotes(self, *args) -> None:
        self._refresh("option")
    
    def refresh_quotes_underlying(self, *args) -> None:
        self._refresh("underlying")
        
    def _refresh(self, instrument: str) -> None:
        """
        
        Skip if instrument being refresh has cache. This method is only called when we get response from instrument, therefore
        another metric was what changed. 
        
        """
        for ivol_metrics in self.ivol_metrics:
            ivol_config = ivol_metrics.config
            px_option = self.quotes[ivol_config.px_type_option]
            px_underlying = self.quotes_underlying.px[ivol_config.px_type_underlying]            
            ts_px = self.quotes.last_ts, px_option if instrument == "option" else self.quotes_underlying.last_ts, px_underlying
            
            if math.isnan(ts_px[1]) or ivol_metrics.is_cached(*{instrument : ts_px}):
                continue
            else:
                if not self.states[ivol_config.px_type_underlying].check_set_get("OTM", px_underlying):
                    continue
                
                timestamp = max(self.quotes.last_ts, self.quotes_underlying.last_ts)
                ivol = self.calc_ivol(timestamp, px_option, px_underlying)
                                                       
                ivol_metrics.update(ivol,
                                    {"option" : [self.quotes.last_ts, px_option],
                                     "underlying" : [self.quotes_underlying.last_ts, px_underlying],
                                     })
            metric_names = ivol_metrics.get_req_metrics()
            metric_values = self.ivol_engine.calculate(metric_names)
            ivol_metrics.set_metrics(**metric_values)
            
            
    def calc_ivol(self, ts, px_opt, px_under):
        """
        
        extra call for people to easily override if subclassing the Option class.

        Parameters
        ----------
        ts : float
            epoch timestamp in (s)
        px_opt : float
            _description_
        px_under : float
            _description_

        Returns
        -------
        _type_
            _description_
        """
        return self.ivol_engine.calculate_IVOL(ts, px_opt, px_under)

            
    def update_ivol(self) -> None:
        for ivol_metrics in self.ivol_metrics:
            ivol_config = ivol_metrics.config
            
            quotes_underlying = self.quotes_underlying

            if quotes_underlying:
                pass
            
            
            ivol = self.ivol_engine.calculate_IVOL(max(self.quotes.last_ts, quotes_underlying.last_ts),
                                                   getattr(self.quotes, ivol_config.px_type_option),
                                                   getattr(self.quotes_underlying, ivol_config.px_type_underlying),
                                                   )
            ivol_metrics.update(ivol)
            
        
    def create_ivol_metric(self, config) -> None:
        ivol_config = quantities.IVOLConfig(**config)
        
        if all(len(self.ivol_metrics) > 0,
               not math.isnan(self.quotes[ivol_config.px_type_option]),
               not math.isnan(self.quotes_underlying[ivol_config.px_type_underlying])
            
            ##### We have to check if other variables are also non-nan #####
            
            ):
            ts = np.nan
        else:
            ts=np.nan
        

        ivol_metrics = quantities.IVOLMetrics(config=ivol_config,
                                              last_ts=ts,
                                              greeks=quantities.Greeks(),
                                              moneyness=quantities.Moneyness()
                                              )
        self.ivol_metrics.append(ivol_metrics)
        self._underlying_px_targets.update(ivol_config.px_type_underlying)
        
    
    def add_active_ivol_ptype(self, opt_pytpe) -> None:
        if opt_pytpe not in self.active_ivol_ptypes:
            self.active_ivol_ptypes = self.active_ivol_ptypes + (opt_pytpe,)
        
    def remove_active_ivol_ptype(self, opt_ptype) -> None:
        self.active_ivol_ptypes = tuple(ivol for ivol in self.active_ivol_ptypes if ivol != opt_ptype)
    
    def update_metrics(self, engine=None, cachedIV=False):
        self.calculate_implied_volatility(engine, cachedIV)
        self.calculate_greeks(engine)
        self.calculate_moneyness_metrics(engine)
        
    def update_from_OTM_sister(self, sister_option: "Option", engine=None):
        ivol_b, ivol_a = self.itm_conversion_engine.ITM_ivol(sister_option, self)
        self.ivol[self._ptype_idx_map["px_bid"]] = ivol_b
        self.ivol[self._ptype_idx_map["px_ask"]] = ivol_a
        self.ivol[self._ptype_idx_map["px_mid"]] = sister_option.ivol[self._ptype_idx_map["px_mid"]]
        self.calculate_greeks(engine)
        self.calculate_moneyness_metrics()
    
    def get_all_metrics_price_type(self, px_type):
        idx = self._ptype_idx_map[px_type]
        self.underlying_px = self.underlying_px
        return self.prices[idx], self.ivol[idx], self.delta[idx], self.delta_mag[idx], self.gamma[idx], self.vega[idx], self.theta[idx], self.rho[idx], self.moneyness, \
                self.log_moneyness, self.standardised_moneyness[idx], self.OTM, self.call_flag, self.underlying_px

    def get_all_metrics(self):# -> tuple[Any, Any, Any, Any, Any, Moneyness | Any | float, f...:
        return self.ivol, self.delta, self.delta_mag, self.gamma, self.vega, self.moneyness, self.log_moneyness,\
                self.standardised_moneyness, self.OTM, self.underlying_px
        
            
    def calculate_implied_volatility(self, option_engine=None, cachedIV=False):
        if cachedIV:
            return
        if not math.isnan(self.underlying_px) and self.OTM:
            if option_engine is None:
                option_engine = self.ivol_engine
            
            for px_type in self.active_ivol_ptypes:
                self.ivol[self._ptype_idx_map[px_type]] = option_engine.calculate_IVOL(self.last_update_time,
                                                                                    getattr(self, px_type),
                                                                                    self.underlying_px
                                                                                    )
                print(self.ivol)
        else:
            self.ivol=self._nan_3_numpy.copy()

    def calculate_greeks(self, option_engine=None):
        if not math.isnan(self.underlying_px):
            if option_engine is None:
                option_engine = self.ivol_engine
            self.delta, self.gamma, self.vega, self.theta, self.rho = option_engine.calculate_all_greeks(self.last_update_time,
                                                                                                        self.ivol,
                                                                                                        self.underlying_px)          
            self.delta_mag = np.abs(self.delta)
        else:
            self.delta, self.gamma, self.vega, self.theta, self.rho, self.delta_mag = [self._nan_3_numpy.copy()] * 6

    def get_underlying(self, *args):
        return self.underlying_px
    
    def get_ivol(self, px_type=None):
        if px_type is None:
            return self.ivol
        return self.ivol[self._ptype_idx_map[px_type]]
    
    def get_delta(self, px_type=None):
        if px_type is None:
            return self.delta
        return self.delta[self._ptype_idx_map[px_type]]

    def get_gamma(self, px_type=None):
        if px_type is None:
            return self.gamma
        return self.gamma[self._ptype_idx_map[px_type]]

    def get_vega(self, px_type=None):
        if px_type is None:
            return self.vega
        return self.vega[self._ptype_idx_map[px_type]]

    def get_theta(self, px_type=None):
        if px_type is None:
            return self.theta
        return self.theta[self._ptype_idx_map[px_type]]

    def get_rho(self, px_type=None):
        if px_type is None:
            return self.rho
        return self.rho[self._ptype_idx_map[px_type]]
    
    def get_greeks(self, px_type=None):
        if px_type is None:
            return self.delta, self.gamma, self.vega, self.theta, self.rho
        idx = self._ptype_idx_map[px_type]
        return self.delta[idx], self.gamma[idx], self.vega[idx], self.theta[idx], self.rho[idx]
    
    def moneyness_metrics(self, px_type=None):
        if px_type is None:
            return self.moneyness, self.log_moneyness, self.standardised_moneyness
        idx = self._ptype_idx_map[px_type]
        return self.moneyness, self.log_moneyness, self.forward_moneyness, self.standardised_moneyness[idx], 
    
    def calculate_moneyness_metrics(self, *arg):
        if not math.isnan(self.underlying_px):
            self.moneyness = self.specs.strike / self.underlying_px
            if not self.future_underyling:
                forward_factor = 0
                if not self.ivol_engine.interest_rate_engine is None:
                    forward_factor += self.ivol_engine.interest_rate_engine.evaluate(utils.convert_unix_maturity_to_years(self.specs.expiry))
                if not self.ivol_engine.dividend_rate_engine is None:
                    forward_factor += self.ivol_engine.dividend_rate_engine.evaluate(utils.convert_unix_maturity_to_years(self.specs.expiry))

                forward_rate = math.exp(forward_factor * utils.convert_unix_maturity_to_years(self.specs.expiry))
                self.forward_moneyness = forward_rate * self.moneyness
            
            self.log_moneyness = math.log(self.moneyness)
            
            if self.future_underyling:
                self.standardised_moneyness = self.log_moneyness / (self.ivol * math.sqrt(utils.convert_unix_maturity_to_years(self.specs.expiry)))
            else:
                self.standardised_moneyness = math.log(self.forward_moneyness) / (self.ivol * math.sqrt(utils.convert_unix_maturity_to_years(self.specs.expiry)))
        else:
            self.moneyness=np.nan
            self.log_moneyness=np.nan
            self.standardised_moneyness = self._nan_3_numpy.copy()

  
@dataclass(slots=True, frozen=True, kw_only=True)
class OptionInvSpecifications(OptionSpecifications):
    category: str=field(default="opi", init=False)


class OptionInverted(Option):
    """
    inverted options are essentially FX options settle in foreign ccy
    """
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
    
    
    
    
    def calc_ivol(self, ts, px_opt, px_under):
        
        return super().calc_ivol(ts, px_under*px_opt, px_under)
    


class ExchangeTradedProduct(ABCInstrument):
    def __init__(self, tickers, bpx_asket_instrument_type, **kwargs):
        super().__init__(tickers, **kwargs)
        self.object_bpx_asket=[]
        for ticker in tickers:
            self.object_bpx_asket.append(getattr(bpx_asket_instrument_type(ticker)))
            
    def update_from_underlying(self, underlying_object):
        self.underlying_px=getattr(underlying_object, self.underlying_px_type)
    
    def update_metrics(self):...

