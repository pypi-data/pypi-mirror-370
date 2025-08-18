from __future__ import annotations 
from typing import List, Optional, Tuple, Union, Dict, TYPE_CHECKING, Callable, Any
if TYPE_CHECKING:
    from instruments.utils import InstrumentManager
    from pandas import DataFrame
    from engines.surface_engines import AbstractSurfaceEngine
    from data_classes.classes import BaseDomain, Domain, OptionChain, VolatilityData, VolVector
    from examples.synthetic.websocket_streamer import Streamer
    
from PySide6 import QtCore, QtWebSockets
import asyncio
import queue
from pyvol_terminal.instruments.instruments import ABCInstrument
import time
import numpy as np
from abc import ABC, abstractmethod
from .gl_3D_graphing.meta import QABCMeta
import json

def get_updater_dict():
    return {""}

class WebsocketWorker(QtCore.QObject):
    processedSignal = QtCore.Signal(dict)
    
    def __init__(self,
                 data_processing_config,
                 ws_worker_config, 
                 all_instruments: Dict[str, ABCInstrument],
                 active_instruments: set[str]=set(),
                 **kwargs
                 ):
        super().__init__()
        self._should_stop=False
        self._intense_interaction=False
        self._intense_interaction_just_ended=False
        self.task=None
        self.buffer_responses={}
        self._all_instruments=all_instruments
        self.active_instruments = active_instruments
        self.data_processing_config = data_processing_config
        self.websocket = ws_worker_config.pop("websocket")
        self.ws_worker_config=ws_worker_config
        self.generator_call = getattr(self.websocket, ws_worker_config["start_ws_func_name"])
        self.ws_instrument_key = data_processing_config["websocket_json_format"]["instrument_key"]
        self.ws_bid_key = data_processing_config["websocket_json_format"]["bid_key"]
        self.ws_ask_key = data_processing_config["websocket_json_format"]["ask_key"]
        self.ws_timestamp_key = data_processing_config["websocket_json_format"]["timestamp_key"]
        
        self.setUpdateMethod(data_processing_config)
        
        self._thread = QtCore.QThread()
        self.moveToThread(self._thread)
        self._thread.started.connect(self.start_worker)
    
    def setUpdateMethod(self, data_processing_config):
        if "buffer" in data_processing_config:
            if data_processing_config["buffer"]:
                if "timer_process_data" in data_processing_config:
                    self.timer_process_data=data_processing_config["timer_process_data"]
                else:
                    self.timer_process_data=2
                self._updater_method = self.buffer_updater
            else:
                self.timer_process_data=None
                self._updater_method=self.single_update
        else:
            self.timer_process_data=None
            self._updater_method=self.single_update
    
    def start_worker(self):
        match self.ws_worker_config["parallel_type"]:
            case "async":
                self.loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self.loop)
                self.task = self.loop.create_task(self.run_async())
                try:
                    self.loop.run_until_complete(self.task)
                except asyncio.CancelledError:
                    pass
                finally:
                    self.loop.close()
            case "threading":
                self.run_threading()
                
    async def run_async(self,):
            async for message in self.generator_call():
                if self._should_stop:
                    break
                self.update_price(message)

    def stop_worker(self):
        self._should_stop = True
                    
        if self._thread.isRunning():
            self._thread.quit()
            self._thread.wait()

        match self.ws_worker_config["parallel_type"]:
            case "async":
                if self.task and not self.task.done():
                    self.task.cancel()
                
    def update_price(self, websocket_response: Dict[Any, Any]):
        ticker = websocket_response[self.ws_instrument_key]    
        if ticker in self.active_instruments:
            timestamp = websocket_response[self.ws_timestamp_key]
            
            self._all_instruments[ticker].update(self.normalize_timestamp(timestamp),
                                                 websocket_response[self.ws_bid_key],
                                                 websocket_response[self.ws_ask_key]
                                                 )
                        

    def add_active_instruments(self, instruments: set[str]):
        self.active_instruments.update(instruments)
        
    def reset_active_instruments(self, new_active_instruments: set[str]=set()):
        self.active_instruments=new_active_instruments
            
    def check_enough_time(self):
        if time.time() - self.last_process_update > self.timer_process_data:            
            return True
        else:
            return False
    
    def buffer_updater(self, websocket_response):
        self.bulk_response(websocket_response)
        if self.check_enough_time():
            self.update_price_with_buffer()
        
    def bulk_response(self, websocket_responses):
        for websocket_response in websocket_responses:
            ticker = websocket_response[self.ws_instrument_key]
            self.buffer_responses[ticker] = websocket_response

    def update_price_with_buffer(self):
        for ticker, websocket_response in self.buffer_responses.copy().items():
            self.update_price(websocket_response)
            del self.buffer_responses[ticker]
        self.buffer_responses.clear()
        self.last_process_update=time.time()
        
    def start(self):
        self._thread.start()
        self._thread.setPriority(QtCore.QThread.LowestPriority)
    
    def single_update(self, websocket_response):
        self.update_price(websocket_response)
    
    @staticmethod
    def normalize_timestamp(ts: float) -> float:
        if ts > 1e14:     
            return ts * 1e-9
        elif ts > 1e11:     
            return ts * 1e-3
        else:              
            return ts
        
    def setIntenseInteraction(self, state: bool):
        if self._intense_interaction and not state:
            self._intense_interaction_just_ended = True
        self._intense_interaction = state



class ABCCalibrationWorker(QtCore.QObject, metaclass=QABCMeta):
    calibratedSignal = QtCore.Signal(dict)
    def __init__(self,
                 *,
                 active_instruments: set[str],
                 update_timer: int,
                 calibration_engines: Dict[str, AbstractSurfaceEngine], 
                 **kwargs
                 ):
        super().__init__(**kwargs)
        self.active_instruments=active_instruments
        self._update_timer=update_timer
        self.calibration_engines=calibration_engines
        
        self._running=False
        self._intense_interaction=False
        
        self._thread = QtCore.QThread()
        self._thread.started.connect(self.start_worker)
        
    def work(self):
        while self._running:
            while self._intense_interaction:
                QtCore.QThread.msleep(200)
            self._internal_work()
            QtCore.QThread.msleep(self._update_timer)    
            
    def setIntenseInteraction(self, flag: bool):
        self._intense_interaction=flag
    
    def start_worker(self):
        self.moveToThread(self._thread)
        self._running=True
        self._thread.started.connect(self.work)
        self._thread.start()
        
    def stop_worker(self):
        self._running=False
        if self._thread.isRunning():
            self._thread.quit() 
            self._thread.wait() 
    
    def isRunning(self): return all((self._running, self._thread.isRunning()))
    
    @abstractmethod
    def _internal_work(self):...
    

class SurfaceCalibration(ABCCalibrationWorker):
    def __init__(self,
                 *,
                 option_chain_container: Dict[str, OptionChain],
                 vol_vect_container: Dict[str, VolVector],
                 **kwargs,
                 ):
        super().__init__(**kwargs)
        self.option_chain_container=option_chain_container
        self.vol_vect_container=vol_vect_container
    
    def _internal_work(self):
        valid_calibrations=[]
        for px_type, engine in self.calibration_engines.items():
            option_chain = self.option_chain_container[px_type]
            vol_vector = self.vol_vect_container[px_type]
            vol_vector.update(**option_chain.getDataKwargs())
            engine.calibrate(*vol_vector.calibration_args())
            valid_calibrations.append(engine.valid_calibration())

        if any(valid_calibrations):
            self.calibratedSignal.emit(self.calibration_engines)
            
    