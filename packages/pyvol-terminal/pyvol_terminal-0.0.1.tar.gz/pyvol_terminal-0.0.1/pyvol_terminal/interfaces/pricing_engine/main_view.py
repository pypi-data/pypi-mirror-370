from __future__ import annotations 
from typing import List, Optional, Tuple, Union, Dict, TYPE_CHECKING, Callable
if TYPE_CHECKING:
    from ...data_classes.classes import AbstractDataClass, VolatilityData, VolVector, Surface, Points, Slice
    from instruments.utils import InstrumentManager
    from instruments.instruments import Spot, Option, Future

from PySide6 import QtWidgets, QtCore
from pyvol_terminal.settings import utils as settings_utils
from datetime import datetime
import numpy as np
from PySide6.QtCore import Qt
import QuantLib as ql
from pyvol_terminal.data_classes import builders as builders_data_classes
from ...quantities import engines
import math
from ..abstract_classes import ABCMainViewQTableWidget


class MainView(ABCMainViewQTableWidget):
    def __init__(self,
                 instrument_manager: InstrumentManager=None,
                 data_container=None,
                 tick_engine_manager=None,
                 **kwargs):
        super().__init__()
        self.instrument_manager=instrument_manager
        self.options_container=instrument_manager.options_instrument_container
        self.data_container=data_container
        self.column_items=[]
        if tick_engine_manager is None:
            self.tick_engine_manager = engines.TickEngineManager("Strike",
                                                                 "Expiry",
                                                                 "Implied Volatility"
                                                                 )

        else:
            self.tick_engine_manager=tick_engine_manager
        
        self.row_labels=["Style", "Call/Put", "Direction", "Strike", "Expiry", "Model", "Price"]
        self.data_container = self._initDataClassContainer(**kwargs)

        self.spot_object: Spot = list(self.instrument_manager.spot_instrument_container.objects.values())[0]
        
        self.initSettingsTable()
        self._initConstantQLObject()
        
        self.check_until_ready()
        
    def check_until_ready(self):
        xyz = self.data_container["mid"].vol_vector.data()
        if not math.isnan(self.spot_object.mid) and np.isnan(xyz[2]).sum()==0:
            print("Condition met, initializing...")
            print(xyz[2])
            print(np.isnan(xyz[2]).sum()    )
            self.initQLObjects()
        else:
            QtCore.QTimer.singleShot(500, self.check_until_ready)
        
    def _initDataClassContainer(self,       
                                vol_vect_container: VolVector|None=None,
                                default_nTicks: Tuple[int, int]=(30,30),
                                **kwargs
                                ) -> Dict[str, VolatilityData]:
        if vol_vect_container is None:
            return {}
        else:
            return builders_data_classes.create_volatility_data_from_vol_vect(vol_vect_container, default_nTicks)

    def initSettingsTable(self):
        self.table = QtWidgets.QTableWidget()
        self.table.setRowCount(6)
        self.table.setColumnCount(3)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setVisible(False)
        
        for idx, row_label in enumerate(self.row_labels):
            self.table.setItem(idx, 0, QtWidgets.QTableWidgetItem(row_label))
    
    def initModelOptionsTable(self):
        self.table = QtWidgets.QTableWidget()
        self.table.setRowCount(6)
        self.table.setColumnCount(3)
        
        
    def _initConstantQLObject(self):
        expiration_dt = [datetime.fromtimestamp(ts) for ts in self.data_container["mid"].surface.data()[1]]
        self.expiration_dates_ql = [ql.Date(dt.day, dt.month, dt.year) for dt in expiration_dt]
        self.calculation_date = ql.Date(datetime.now().day, datetime.now().month, datetime.now().year)
        ql.Settings.instance().evaluationDate = self.calculation_date

    def initQLObjects(self):
        v0, kappa, theta, rho, sigma = 0.01, 0.2, 0.02, -0.75, 0.5
        dfs=[1.]
        futures_exp_dates = [self.calculation_date]
        
        spot = self.spot_object.mid

        for futures_object in self.instrument_manager.futures_instrument_container.objects.values():
            exp_ts = futures_object.expiry
            exp_dt = datetime.fromtimestamp(exp_ts)
            exp_ql = ql.Date(exp_dt.day, exp_dt.month, exp_dt.year)
            dfs.append(futures_object.mid / spot)
            futures_exp_dates.append(exp_ql)
        
        data_container = self.data_container["mid"]
        xyz = np.column_stack(data_container.vol_vector.data())



        xyz = MainView.getRectStrikesExpiries(xyz)

        strikes = np.unique(xyz[:, 0])
        expiries = np.unique(xyz[:, 1])
        vol_grid = xyz[:, 2].reshape(len(strikes), len(expiries))
        print(vol_grid)
        expiration_dt = [datetime.fromtimestamp(ts) for ts in expiries]
        self.expiration_dates_ql = [ql.Date(dt.day, dt.month, dt.year) for dt in expiration_dt]
        

        
        implied_vols = ql.Matrix(vol_grid.shape[0], vol_grid.shape[1])
        
        
        for i, _ in enumerate(strikes):
            for j, _ in enumerate(expiries):
                implied_vols[i][j] = vol_grid[i][j]

        
        calendar = ql.UnitedStates(ql.UnitedStates.NYSE)
        day_count = ql.Actual365Fixed()
        black_var_surface = ql.BlackVarianceSurface(self.calculation_date,
                                                    calendar,
                                                    self.expiration_dates_ql,
                                                    strikes.tolist(),
                                                    implied_vols,
                                                    day_count
                                                    )
                
        
        strikes_grid = np.arange(strikes[0], strikes[-1], 10)
        expiry = 0.6
        implied_vols = [black_var_surface.blackVol(expiry, s)
                        for s in strikes_grid] # can interpolate here

        print(implied_vols) 
        
        _ = dfs.pop(1)
        _ = futures_exp_dates.pop(1)
        
        
        self.calendar = ql.NullCalendar()
        curve = ql.DiscountCurve(futures_exp_dates, dfs, ql.Actual360())
        self.interest_ts = ql.YieldTermStructureHandle(curve)
        self.dividend_ts = ql.YieldTermStructureHandle(ql.FlatForward(self.calculation_date, ql.QuoteHandle(ql.SimpleQuote(0.0)), ql.Actual365Fixed())),  # No dividend yield
        
        
        
        process = ql.HestonProcess(self.interest_ts, self.dividend_ts,
                                ql.QuoteHandle(ql.SimpleQuote(spot)),
                                v0, kappa, theta, sigma, rho)

        self.model = ql.HestonModel(process)
        self.engine = ql.AnalyticHestonEngine(self.model)
    
    def calibrate(self):
        heston_helpers = []
        for j, (date, ts) in enumerate(zip(self.expiration_dates_ql, self.data_container.domain["mid"].y_vect)):
            for i, s in enumerate(self.data_container.domain["mid"].x_vect):
                t = (date - self.calculation_date)
                p = ql.Period(t, ql.Days)
                sigma = self.data_container.raw
                helper = ql.HestonModelHelper(p, self.calendar, self.spot_object.mid, s,
                                              ql.QuoteHandle(ql.SimpleQuote(sigma)),
                                              self.interest_ts,
                                              self.dividend_ts)
                helper.setPricingEngine(self.engine)
                heston_helpers.append(helper)
        lm = ql.LevenbergMarquardt(1e-8, 1e-8, 1e-8)
        self.model.calibrate(heston_helpers, lm, ql.EndCriteria(500, 50, 1.0e-8, 1.0e-8, 1.0e-8))
        theta, kappa, sigma, rho, v0 = self.model.params()
        print((theta, kappa, sigma, rho, v0))        

    def _internal_update_view(self):
        pass



    @classmethod
    def getRectStrikesExpiries(cls, xyz) -> Tuple[np.ndarray, ...]:
        print(len(np.unique(xyz[:, 0])))
        strikes, expiries, vol = xyz[:,0], xyz[:,1], xyz[:,2]
        exp = np.unique(expiries)
        unique, counts = np.unique(strikes, return_counts=True)
        k = unique[counts >= exp.size]
        
        xyz = xyz[np.isin(xyz[:, 0], k)]
        xyz = xyz[np.isin(xyz[:, 1], exp)]
        
        return xyz
    
    @classmethod
    def drop_duplicate_strike_exp(cls, arr: np.ndarray) -> np.ndarray:
        col01 = arr[:, :2]
        _, inv, counts = np.unique(col01, axis=0, return_inverse=True, return_counts=True)
        mask = counts[inv] == 1
        return arr[mask]