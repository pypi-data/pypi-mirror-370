#%%%

from dataclasses import dataclass, field
from typing import Dict

@dataclass
class MyDataclass:
    _x: Dict[str, str] = field(init=False, default=dict)
    
    def __post_init__(self):
        self._x = {"1": "1"}
    
    def func(self):
        print(self._x)
    
    
mydc = MyDataclass()
mydc.func()
        