

class PriceText(str):
    def __new__(cls, instrument_objects):
        if isinstance(instrument_objects, (dict, list)):
            price_text_map = {instrument_object.ticker : "" for instrument_object in instrument_objects}
        else:
            price_text_map = {instrument_objects.ticker : ""}
            print("else")
        joined = cls._create_spot_text(price_text_map)
        obj = super().__new__(cls, joined)
        obj.price_text_map = price_text_map
        obj.text_updated_callbacks=[]
        if isinstance(instrument_objects, (dict, list)):
            for instrument_object in instrument_objects:
                instrument_object.add_price_callbacks(obj.update)
        else:
            instrument_objects.add_price_callbacks(obj.update)
        return obj
    
    def add_text_updated_callback(self, callback):
        self.text_updated_callbacks.append(callback)

    def update(self, instrument_object):
        spot_name, value = instrument_object.ticker, instrument_object.mid
        self.price_text_map[spot_name] = value
        self._updated_value = PriceText._create_spot_text(self.price_text_map)
        for callback in self.text_updated_callbacks:
            callback(self)

    def __str__(self):
        return getattr(self, '_updated_value', super().__str__())

    def __repr__(self):
        return f"PriceText({str(self)!r}, price_text_map={self.price_text_map})"

    @classmethod
    def _create_spot_text(cls, price_text_map):
        total_spot_string = ""
        for i, (ticker, value) in enumerate(price_text_map.items()):
            if isinstance(value, str):
                if len(value) > 0:
                    value_str = f"{float(value):,.2f}"
                else:
                    value_str = value
            else:
                value_str = f"{value:,.2f}"
            if i == 0:
                total_spot_string = total_spot_string + f"{ticker}: {value_str}"
            else:
                total_spot_string = total_spot_string + f"\n{ticker}: {value_str}"
        return total_spot_string
    