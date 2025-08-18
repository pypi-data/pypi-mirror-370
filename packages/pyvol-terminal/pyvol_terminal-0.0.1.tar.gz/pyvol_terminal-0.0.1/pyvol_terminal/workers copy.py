from __future__ import annotations 
from typing import List, Optional, Tuple, Union, Dict, TYPE_CHECKING, Callable, Any
if TYPE_CHECKING:
    from instruments.utils import InstrumentManager
    from pandas import DataFrame
    from engines.surface_engines import AbstractSurfaceEngine
    from data_classes.classes import BaseDomain, Domain, OptionChain, VolatilityData, VolVector
    
from PySide6 import QtCore
import asyncio
import queue
import time
import numpy as np

class WebsocketWorker(QtCore.QThread):
    update_signal = QtCore.Signal(list, bool)  

    def __init__(self,parallel_type=None, ws_transport_method=None, websocket=None,
                 start_ws_func_name="", q=None, multiple_levels=False,
                 qt_timer_seconds=2, bulk_response=False):
        super().__init__()
        self._is_running = True  
        self.stop_flag=False
        self.parallel_type=parallel_type
        self._should_stop = False
        self.price_generator = websocket
        self.start_ws_func_name=start_ws_func_name
        self.all_response = []
        self.bulk_response = bulk_response
        self.q=q
        self.loop=None
        self.task=None
        self.qt_timer_seconds=qt_timer_seconds
        self.multiple_levels=multiple_levels
        self.ws_transport_method=ws_transport_method
        self.generator_call = getattr(self.price_generator, start_ws_func_name)            
        self._should_stop = False
        
        if self.ws_transport_method == "queue":
            self.queue_timer = QtCore.QTimer()
            self.queue_timer.timeout.connect(self.get_queue)
            self.queue_timer.start(self.qt_timer_seconds * 1000)
    
    def get_queue(self):
        all_responses = []
        while True:
            try:
                response = self.q.get_nowait()
                all_responses.append(response)
            except queue.Empty:
                break 
        if len(all_responses) > 0:
            self.update_signal.emit(all_responses, True)
            
    def run_threading(self,):
        self.generator_call()

    async def run_async(self,):
        async for message in self.generator_call():
            if self._should_stop:  
                break          
            self.update_signal.emit([message], False)

    def run(self):
        match self.parallel_type:
            case "async":
                self.loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self.loop)
                self.loop.run_until_complete(self.run_async())
                self.loop.close()
            case "threading":
                self.run_threading()

                                
    def stop(self):
        self._should_stop = True
        self._is_running = False
        """
        if self.loop:
            self.loop.close()
        """
        self.quit()
        self.wait()

        


def get_updater_dict():
    return {""}


class PriceProcessor(QtCore.QObject):
    processedSig = QtCore.Signal()
    
    def __init__(self,
                 instrument_manager: InstrumentManager,
                 data_processing_config):
        super().__init__()
        self.instrument_manager=instrument_manager
        self.last_buffer_responses={}
        self.last_process_update=time.time()
        self.data_processing_config=data_processing_config
        websocket_json_format = data_processing_config["websocket_json_format"]
        self.ws_instrument_key = websocket_json_format["instrument_key"]
        self.ws_bid_key = websocket_json_format["bid_key"]
        self.ws_ask_key = websocket_json_format["ask_key"]
        self.ws_timestamp_key = websocket_json_format["timestamp_key"]
        self.last_buffer_update_time=time.time()
        self._last_update_checker_timer=time.time()
        
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
    
    def update_interface_signal():
        pass
    
    def _update_displays(self):
        self.update_interface_signal.emit()
    
    def single_update(self, websocket_response):
        self.update_price(websocket_response)
        self.processedSig.emit()
    
    def update_price(self, websocket_response):
        ticker = websocket_response[self.ws_instrument_key]    
        timestamp = websocket_response[self.ws_timestamp_key]
        bid = websocket_response[self.ws_bid_key]
        ask = websocket_response[self.ws_ask_key]
        self.instrument_manager.update_price(ticker, timestamp, bid, ask)  # Ensures sister option is ITM/OTM
        
        if time.time() - self._last_update_checker_timer > 20:
            for option_object in self.instrument_manager.all_instrument_objects.values():
                if time.time() - option_object.last_update_time > 20:
                    option_object.update(ticker, timestamp, bid, ask)

    def check_enough_time(self):
        if time.time() - self.last_process_update > self.timer_process_data:            
            return True
        else:
            return False
    
    def buffer_updater(self, websocket_response):
        self.bulk_response(websocket_response)
        if self.check_enough_time():
            self.update_price_with_buffer()
        self.processedSig.emit()
    
    
    QtCore.Slot()
    def update(self, websocket_response):
        self._updater_method(websocket_response)
    
    def bulk_response(self, websocket_responses):
        for websocket_response in websocket_responses:
            ticker = websocket_response[self.ws_instrument_key]
            self.last_buffer_responses[ticker] = websocket_response
                
    def update_response_buffer(self, websocket_response):
        ticker = websocket_response[self.ws_instrument_key]
        self.last_buffer_responses[ticker] = websocket_response

    def update_price_with_buffer(self):
        for ticker, websocket_response in self.last_buffer_responses.copy().items():
            self.update_price(websocket_response)
            del self.last_buffer_responses[ticker]
        self.last_buffer_responses.clear()
        self.last_process_update=time.time()



class SurfaceEvaluate(QtCore.QThread):
    calibratedSignal = QtCore.Signal()
    
    def __init__(self,
                 raw_options_container: Dict[str, OptionChain],
                 update_timer: float=0.,
                 engine_container: Dict[str, SurfaceEvaluate]={},
                 vol_vect_container: Dict[str, Dict[str, VolVector]]={},
                 **kwargs,
                 ):
        super().__init__()
        self.raw_options_container=raw_options_container
        self.vol_vect_container=vol_vect_container
        self._update_timer=update_timer
        self.surface_engine_container: Dict[str, AbstractSurfaceEngine]=engine_container
        self._last_calibration=time.time()
        self._last_price_process=time.time()
        self._timer = None
    
    @QtCore.Slot()
    def price_process_response(self):
        self._last_price_process=time.time()
    
    def calibrate_surfaces(self):
        if self._last_price_process > self._last_calibration:
            for px_type, surface_engine in self.surface_engine_container.items():
                for vol_vect_container in self.vol_vect_container.values():
                    raw_options = self.raw_options_container[px_type]
                    vol_vector = vol_vect_container[px_type]
                    vol_vector.update(**raw_options.getDataKwargs())
                
                    surface_engine.calibrate(*vol_vector.data())

            self._last_calibration=time.time()
            self.calibratedSignal.emit()
    
    def add_vol_vect_container(self, name, vol_vect_container):
        self.vol_vect_container[name]=vol_vect_container
        
    def remove_vol_vect_container(self, name):
        del self.vol_vect_container[name]

    def run(self):
        self.timer = QtCore.QTimer()
        self.timer.moveToThread(self)
        self.timer.timeout.connect(self.calibrate_surfaces)
        self.timer.start(self._update_timer*1000)
        self.exec()    


    
    def stop(self):
        if self._timer:
            self._timer.stop()
            self._timer.deleteLater()