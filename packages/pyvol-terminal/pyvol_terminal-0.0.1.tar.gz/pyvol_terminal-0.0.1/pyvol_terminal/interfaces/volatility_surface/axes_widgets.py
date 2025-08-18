from __future__ import annotations
from typing import List, Optional, Tuple, Union, Dict, TYPE_CHECKING



from ...gl_3D_graphing.graphics_items.GL3DAxisItem import GL3DAxisItem
import traceback

class PyVolGL3DAxisItem(GL3DAxisItem):
    def __init__(self, *args, **kwargs):
        self.tick_engine=kwargs.pop("tick_engine", None)
        super().__init__(*args, **kwargs)

    def tickStrings(self, values, scale, spacing):
        if not self.tick_engine is None:
            return self.tick_engine(values)
        else:
            return super().tickStrings(values, scale, spacing)
    
    def switch_axis(self, *args, **kwargs): 
        pass
    