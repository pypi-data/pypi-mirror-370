from __future__ import annotations 
from typing import List, Optional, Any, Tuple, Union, Dict, TYPE_CHECKING, Callable
if TYPE_CHECKING:
    
    from pandas import DataFrame
    from ..utils import ws_pyvol_keymap


from .utils import InstrumentManager, InstrumentContainer, BaseMap, OptionMap, ManagerMap
import pandas as pd
from collections import defaultdict
from .instruments import ABCInstrument, Option, Future, Spot, SpotSpecifications, FutureSpecifications, OptionInvSpecifications


def create_instrument_manager(instruments_config,
                              name=None,
                              ws_pyvol_map: ws_pyvol_keymap=None,
                              ) -> InstrumentManager:
    objects_container_all={}
    name_type_container_all = {}
    instrument_manager_kwargs = {"config" : instruments_config}
    
    #create_option_pair_objects(instruments_config["option"]["data"])
    
    for instrument_type in instruments_config:
        if instrument_type in instruments_config:
            
            df: pd.DataFrame = instruments_config[instrument_type]["data"]
            df = df.rename(columns={ws_pyvol_map.ticker : "ticker"})
            
            
            instrument_container, name_type_container = globals()[f"create_{instrument_type}_objects"](df,
                                                                                                       instruments_config,
                                                                                                       objects_container_all)

            objects_container_all = objects_container_all | instrument_container.objects
            name_type_container_all = name_type_container_all | name_type_container
            instrument_manager_kwargs[f"{instrument_type}_instrument_container"] = instrument_container
    manager_map = ManagerMap(name_type_container_all)
    instrument_manager_kwargs["manager_map"]=manager_map
    instrument_manager_kwargs["all_instrument_objects"]=objects_container_all
    instrument_manager_kwargs["name"]=name
    return InstrumentManager(**instrument_manager_kwargs)

def _create_maps(instrument_object_dict):        
    index_name_map = {idx: name for idx, name in enumerate(instrument_object_dict)}
    name_index_map = {name: idx for idx, name in enumerate(instrument_object_dict)}
    return BaseMap(index_name_map, name_index_map)

def create_spot_objects(df, config, *args):
    object_container = {}
    ticker_category_map={}
    if not df is None:
        ticker = df["ticker"].item()        
        kwargs = {key : value for key, value in config["spot"].items()}
        specs = SpotSpecifications(ticker=ticker,
                                   px_quotation="USD"
                                   )
        cls = config["spot"]["object"]
        instrument_object = cls(specs, **kwargs)
        ticker_category_map[ticker] = "spot"
        object_container[ticker] = instrument_object
            
    maps = _create_maps(object_container)
    spot_container = InstrumentContainer(object_container, config["spot"]["price_types"], maps, "spot", df)
    return spot_container, ticker_category_map
    

def create_future_objects(df, config, other_objects: Dict[str, ABCInstrument]):   
    ticker_category_map = {}
    object_container = {}
    for future_row in df.iterrows():
        future_row = future_row[1]
        ticker = future_row["ticker"]
        expiry = future_row["expiry"]
        ticker_category_map[ticker] = "future"    

        if "underlying_map" in config["future"]:
            if isinstance(config["future"]["underlying_map"], str):
                underlying_ticker=config["future"]["underlying_map"][ticker]
                underlying_object = other_objects[underlying_ticker]
            elif isinstance(config["future"]["underlying_map"], Dict):
                underlying_ticker=config["future"]["underlying_map"][ticker]
                underlying_object = other_objects[underlying_ticker]
            else:
                raise KeyError("You have specified an underyling map, but the underlying object has not been instantiated yet. Make sure underlying objects are instantiated first.")
        else:   
            underlying_object=None
      #  args = [ticker, expiry]
        kwargs = config["future"]
        kwargs["ticker"] = ticker
        kwargs["expiry"] = expiry
        kwargs["underlying_ticker"] = underlying_ticker
        kwargs["specs"] = FutureSpecifications(ticker=ticker,
                                               px_quotation="USD"
                                               )

        if "interest_rate_config" in config["future"]:
            kwargs["interest_rate_engine"] = config["future"]["interest_rate_config"]["engine"]
        if "dividend_rate_config" in config["future"]:
            kwargs["dividend_rate_engine"] = config["future"]["dividend_rate_config"]["engine"]
        cls = config["future"]["object"]
        instrument_object = cls(**kwargs)        
        object_container[ticker]=instrument_object
            
    maps = _create_maps(object_container)
    futures_instrument_container = InstrumentContainer(object_container, config["future"]["price_types"], maps, "future", df)
    return futures_instrument_container, ticker_category_map


def create_option_objects(df, config, other_objects: Dict[str, ABCInstrument|List[ABCInstrument]]):
    object_container = {}
    ticker_category_map = {}
    
    df["strike"] = pd.to_numeric(df["strike"], errors='coerce')
    df["expiry"] = pd.to_numeric(df["expiry"], errors='coerce')
    underlying_px_type = config["option"]["underyling_price_type"]
    
    paired_options, pairs = create_option_pair_objects(df)
    
    del config["option"]["underyling_price_type"]
    print(other_objects.keys())
    objects_to_be_paired = {}
    name_underlying_object = {}
    for _, option_row in df.iterrows():
        ticker = option_row["ticker"]
        
        if "underlying_map" in config["option"]:
            if isinstance(config["option"]["underlying_map"], str):
                underlying_object = other_objects[config["option"]["underlying_map"][ticker]]
            elif isinstance(config["option"]["underlying_map"], Dict):
                underlying_object = other_objects[config["option"]["underlying_map"][ticker]]
        else:
            underlying_object_list: List[ABCInstrument]=[]
            for ob in other_objects:
                if ob.instrument_type=="spot":
                    underlying_object_list.append(ob)
            if len(underlying_object_list) != 1:
                raise KeyError("You need to specify an underyling for the options if you have multiple spot objects")
            else:
                underlying_object = underlying_object_list[0]
                
        ticker_category_map[ticker] = "option"    
        
        flag=option_row["flag"]
        
        args = [option_row["strike"], option_row["expiry"], flag]
        kwargs = {"interest_rate_engine" : config["option"]["interest_rate_config"]["engine"],
                  "dividend_rate_engine" : config["option"]["dividend_rate_config"]["engine"]}

        opt_engine = config["option"]["engine"](*args, **kwargs)
        name_underlying_object[ticker] = underlying_object
        
        specs = O
        
        cls = config["option"]["object"]
        
        instrument_object = cls(ticker=ticker,
                                underlying_ticker=underlying_object.ticker,
                                underlying_px_type=underlying_px_type,
                                strike=option_row["strike"],
                                expiry=option_row["expiry"],
                                flag=option_row["flag"],
                                option_engine=opt_engine,
                                **config["option"]
                                )
        underlying_object.add_child_derivative_callback(instrument_object.update_from_underlying)
        object_container[ticker]=instrument_object
        
    
    options_map = _create_option_map(df, object_container)
    
   # object_container.update(pair_objects)
    
                    
    options_instrument_container = InstrumentContainer(object_container,
                                                       config["option"]["price_types"],
                                                       options_map,
                                                       "option",
                                                       df)   
    return options_instrument_container, ticker_category_map

    
def create_option_pair_objects(df: DataFrame):
    grouped = df.groupby(['strike', 'expiry'])
    pairs = []
    for _, group in grouped:
        if set(group['flag']) >= {'c', 'p'}:
            # Create all c-p pairs
            calls = group[group['flag'] == 'c']
            puts = group[group['flag'] == 'p']
            for _, call_row in calls.iterrows():
                for _, put_row in puts.iterrows():
                    pairs.append([call_row['ticker'], put_row['ticker']])

    has_both_flags = grouped['flag'].transform(lambda x: set(x) >= {'c', 'p'})

    df_filtered = df[has_both_flags]
    
    
    return df_filtered["ticker"].to_list(), pairs

def _create_option_map(df: DataFrame,
                       object_container: Dict[str, Option],
                       ) -> OptionMap:
    grouped = df.groupby(['strike', 'expiry'])
    put_call_pair_map = {}
    for (strike, expiry), group in grouped:
        calls = group[group['flag'] == 'c']
        puts = group[group['flag'] == 'p']
        
        for _, row in calls.iterrows():
            name_call = row['ticker']
            name_put = puts['ticker'].values[0] if not puts.empty else None
            put_call_pair_map[name_call] = name_put
            if not name_put is None:
                opt_put = object_container[name_put]
                opt_call = object_container[name_call]
                opt_put.add_metric_callbacks(opt_call.update_from_OTM_sister)
                opt_call.add_metric_callbacks(opt_put.update_from_OTM_sister)

        for _, row in puts.iterrows():
            name_put = row['ticker']
            name_call = calls['ticker'].values[0] if not calls.empty else None
            put_call_pair_map[name_put] = name_call
            
    underlying_ticker_map={}
    name_underlying_map={}

    for name, opt in object_container.items():
        underlying_ticker = opt.underlying_ticker
        if not name in name_underlying_map:
            name_underlying_map[name]=underlying_ticker
        if not underlying_ticker in underlying_ticker_map:
            underlying_ticker_map[underlying_ticker] = [name]
        else:
            underlying_ticker_map[underlying_ticker].append(name)
            
    expiry_strike_map = defaultdict(set)
    strike_expiry_map = defaultdict(set)
    expiry_instrument_map = defaultdict(list)
    strike_instrument_map = defaultdict(list)
    expiry_strike_instrument_map = defaultdict(lambda: defaultdict(list))
    strike_expiry_instrument_map = defaultdict(lambda: defaultdict(list))
    expiry_strike_type_instrument_map = defaultdict(lambda: defaultdict(dict))
    strike_expiry_type_instrument_map = defaultdict(lambda: defaultdict(dict))
    type_expiry_strike_instrument_map = defaultdict(lambda: defaultdict(dict))

    for _, row in df.iterrows():
        expiry = row["expiry"]
        strike = row["strike"]
        ticker = row["ticker"]
        flag = row["flag"]
        
        expiry_strike_map[expiry].add(strike)
        strike_expiry_map[strike].add(expiry)
        expiry_instrument_map[expiry].append(ticker)
        strike_instrument_map[strike].append(ticker)
        expiry_strike_instrument_map[expiry][strike].append(ticker)
        strike_expiry_instrument_map[strike][expiry].append(ticker)

        if ticker in put_call_pair_map:
            pair_instr = put_call_pair_map[ticker]
            if flag == 'c':
                expiry_strike_type_instrument_map[expiry][strike]["c"] = ticker
                expiry_strike_type_instrument_map[expiry][strike]["p"] = pair_instr
                strike_expiry_type_instrument_map[strike][expiry]["c"] = ticker
                strike_expiry_type_instrument_map[strike][expiry]["p"] = pair_instr
                type_expiry_strike_instrument_map["c"][expiry][strike] = ticker
                type_expiry_strike_instrument_map["p"][expiry][strike] = pair_instr
            elif flag == 'p':
                expiry_strike_type_instrument_map[expiry][strike]["p"] = ticker
                expiry_strike_type_instrument_map[expiry][strike]["c"] = pair_instr
                strike_expiry_type_instrument_map[strike][expiry]["p"] = ticker
                strike_expiry_type_instrument_map[strike][expiry]["c"] = pair_instr
                type_expiry_strike_instrument_map["p"][expiry][strike] = ticker
                type_expiry_strike_instrument_map["c"][expiry][strike] = pair_instr

    map_kwargs={}
    
    map_kwargs["index_name_map"] = {idx: name for idx, name in enumerate(object_container)}
    map_kwargs["name_index_map"] = {name: idx for idx, name in enumerate(object_container)}
    map_kwargs["underlying_ticker_map"]=underlying_ticker_map
    map_kwargs["name_underlying_map"]=name_underlying_map

    map_kwargs["expiry_strike_map"] = {k: sorted(v) for k, v in expiry_strike_map.items()}
    map_kwargs["strike_expiry_map"] = {k: sorted(v) for k, v in strike_expiry_map.items()}
    map_kwargs["expiry_instrument_map"] = dict(expiry_instrument_map)
    map_kwargs["strike_instrument_map"] = dict(strike_instrument_map)
    map_kwargs["expiry_strike_instrument_map"] = {k: {sk: sv for sk, sv in v.items()} for k, v in expiry_strike_instrument_map.items()}
    map_kwargs["strike_expiry_instrument_map"] = {k: {sk: sv for sk, sv in v.items()} for k, v in strike_expiry_instrument_map.items()}
    map_kwargs["expiry_strike_type_instrument_map"] = {k: {sk: dict(sv) for sk, sv in v.items()} for k, v in expiry_strike_type_instrument_map.items()}
    map_kwargs["strike_expiry_type_instrument_map"] = {k: {sk: dict(sv) for sk, sv in v.items()} for k, v in strike_expiry_type_instrument_map.items()}
    map_kwargs["type_expiry_strike_instrument_map"] = {k: {sk: dict(sv) for sk, sv in v.items()} for k, v in type_expiry_strike_instrument_map.items()}
    map_kwargs["put_call_map"] = put_call_pair_map
    return OptionMap(**map_kwargs)
