def get_metric_attr_all():
    metric_dict = { "price" : {"multi_dim_flag": True},
                    "strike" : {"multi_dim_flag": False},
                    "expiry" : {"multi_dim_flag": False},
                    "ivol": {"multi_dim_flag": True},
                    "delta": {"multi_dim_flag": True},
                    "gamma": {"multi_dim_flag": True},
                    "vega": {"multi_dim_flag": True},
                    "theta": {"multi_dim_flag": True},
                    "rho": {"multi_dim_flag": True},
                    "moneyness": {"multi_dim_flag": False},
                    "log_moneyness": {"multi_dim_flag": False},
                    "standardised_moneyness" : {"multi_dim_flag": True},
                    "forward_moneyness" : {"mult_dim_flag" : False},
                    "OTM": {"multi_dim_flag": False},
                    "call_flag": {"multi_dim_flag": False},
                    "underlying_px": {"multi_dim_flag": False},
                }
    return metric_dict

def get_metric_category(metric):
    metric_dict = {
        "gamma": "greek",
        "delta": "greek",
        "vega": "greek",
        "theta": "greek",
        "rho": "greek",
        "mid": "price",
        "bid": "price",
        "ask": "price",
        "ivol": "volatility",
        "TVAR" : "volatility",
        "VAR" : "volatility", 
        "IVM" : "volatility",
        "IVA" : "volatility",
        "IVB" : "volatility",
        "strike": "strike",
        "expiry": "expiry",
        "moneyness": "moneyness",
        "log_moneyness": "moneyness",
        "standardised_moneyness": "moneyness",
        "forward_moneyness": "moneyness",
        "OTM": "flag",
        "call_flag": "flag",
        "underlying_px": "price"
    }
    
    return metric_dict.get(metric, None)


def get_metric_attr():
    metric_dict = { "price" : {"multi_dim_flag": True},
                    "strike" : {"multi_dim_flag": False},
                    "expiry" : {"multi_dim_flag": False},
                    "ivol": {"multi_dim_flag": True},
                    "OTM": {"multi_dim_flag": False},
                    "call_flag": {"multi_dim_flag": False},
                    "underlying_px": {"multi_dim_flag": False},
                }
    return metric_dict

def greeks_attr():
    metric_dict = {"delta": {"multi_dim_flag": True},
                    "gamma": {"multi_dim_flag": True},
                    "vega": {"multi_dim_flag": True},
                    "theta": {"multi_dim_flag": True},
                    "rho": {"multi_dim_flag": True}
                    }
    return metric_dict

def moneyness_attr():
    metric_dict = {"moneyness": {"multi_dim_flag": False},
                   "log_moneyness": {"multi_dim_flag": False},
                   "standardised_moneyness": {"multi_dim_flag": True},
                   "forward_moneyness" : {"mult_dim_flag" : False},
                    }
    return metric_dict