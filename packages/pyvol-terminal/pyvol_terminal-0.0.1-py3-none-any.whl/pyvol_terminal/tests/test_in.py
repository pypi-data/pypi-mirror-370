from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QGraphicsItem
from PySide6 import QtWidgets


class EnumContainer:
    
    ItemCoordinateCache = QGraphicsItem.CacheMode.ItemCoordinateCache
    DeviceCoordinateCache = QGraphicsItem.CacheMode.DeviceCoordinateCache
    
    # GraphicsItemChange enums
    ItemEnabledChange = QGraphicsItem.GraphicsItemChange.ItemEnabledChange
    ItemEnabledHasChanged = QGraphicsItem.GraphicsItemChange.ItemEnabledHasChanged
    ItemPositionChange = QGraphicsItem.GraphicsItemChange.ItemPositionChange
    ItemPositionHasChanged = QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged
    ItemTransformChange = QGraphicsItem.GraphicsItemChange.ItemTransformChange
    ItemTransformHasChanged = QGraphicsItem.GraphicsItemChange.ItemTransformHasChanged
    ItemRotationChange = QGraphicsItem.GraphicsItemChange.ItemRotationChange
    ItemRotationHasChanged = QGraphicsItem.GraphicsItemChange.ItemRotationHasChanged
    ItemScaleChange = QGraphicsItem.GraphicsItemChange.ItemScaleChange
    ItemScaleHasChanged = QGraphicsItem.GraphicsItemChange.ItemScaleHasChanged
    ItemTransformOriginPointChange = QGraphicsItem.GraphicsItemChange.ItemTransformOriginPointChange
    ItemTransformOriginPointHasChanged = QGraphicsItem.GraphicsItemChange.ItemTransformOriginPointHasChanged
    ItemSelectedChange = QGraphicsItem.GraphicsItemChange.ItemSelectedChange
    ItemSelectedHasChanged = QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged
    ItemVisibleChange = QGraphicsItem.GraphicsItemChange.ItemVisibleChange
    ItemVisibleHasChanged = QGraphicsItem.GraphicsItemChange.ItemVisibleHasChanged
    ItemParentChange = QGraphicsItem.GraphicsItemChange.ItemParentChange
    ItemParentHasChanged = QGraphicsItem.GraphicsItemChange.ItemParentHasChanged
    ItemChildAddedChange = QGraphicsItem.GraphicsItemChange.ItemChildAddedChange
    ItemChildRemovedChange = QGraphicsItem.GraphicsItemChange.ItemChildRemovedChange
    ItemSceneChange = QGraphicsItem.GraphicsItemChange.ItemSceneChange
    ItemSceneHasChanged = QGraphicsItem.GraphicsItemChange.ItemSceneHasChanged
    ItemCursorChange = QGraphicsItem.GraphicsItemChange.ItemCursorChange
    ItemCursorHasChanged = QGraphicsItem.GraphicsItemChange.ItemCursorHasChanged
    ItemToolTipChange = QGraphicsItem.GraphicsItemChange.ItemToolTipChange
    ItemToolTipHasChanged = QGraphicsItem.GraphicsItemChange.ItemToolTipHasChanged
    ItemFlagsChange = QGraphicsItem.GraphicsItemChange.ItemFlagsChange
    ItemFlagsHaveChanged = QGraphicsItem.GraphicsItemChange.ItemFlagsHaveChanged
    ItemOpacityChange = QGraphicsItem.GraphicsItemChange.ItemOpacityChange
    ItemOpacityHasChanged = QGraphicsItem.GraphicsItemChange.ItemOpacityHasChanged
    ItemScenePositionHasChanged = QGraphicsItem.GraphicsItemChange.ItemScenePositionHasChanged

    ItemIsMovable = QGraphicsItem.GraphicsItemFlag.ItemIsMovable.value
    ItemIsSelectable = QGraphicsItem.GraphicsItemFlag.ItemIsSelectable.value
    ItemIsFocusable = QGraphicsItem.GraphicsItemFlag.ItemIsFocusable.value
    ItemClipsToShape = QGraphicsItem.GraphicsItemFlag.ItemClipsToShape.value
    ItemClipsChildrenToShape = QGraphicsItem.GraphicsItemFlag.ItemClipsChildrenToShape.value
    ItemIgnoresTransformations = QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations.value
    ItemIgnoresParentOpacity = QGraphicsItem.GraphicsItemFlag.ItemIgnoresParentOpacity.value
    ItemDoesntPropagateOpacityToChildren = QGraphicsItem.GraphicsItemFlag.ItemDoesntPropagateOpacityToChildren.value
    ItemStacksBehindParent = QGraphicsItem.GraphicsItemFlag.ItemStacksBehindParent.value
    ItemUsesExtendedStyleOption = QGraphicsItem.GraphicsItemFlag.ItemUsesExtendedStyleOption.value
    ItemHasNoContents = QGraphicsItem.GraphicsItemFlag.ItemHasNoContents.value
    ItemSendsGeometryChanges = QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges.value
    ItemAcceptsInputMethod = QGraphicsItem.GraphicsItemFlag.ItemAcceptsInputMethod.value
    ItemIsPanel = QGraphicsItem.GraphicsItemFlag.ItemIsPanel.value
    ItemSendsScenePositionChanges = QGraphicsItem.GraphicsItemFlag.ItemSendsScenePositionChanges.value
    ItemContainsChildrenInShape = QGraphicsItem.GraphicsItemFlag.ItemContainsChildrenInShape.value
    
class CustomGraphicsItem(QGraphicsItem):
    def itemChange(self, change, value):
        print(f"change: {change}")
        print(f"value: {value}")

        ret = super().itemChange(change, value)
        print(f"ret: {ret}")
        return 

class CustomGraphicsItem2(QGraphicsItem):
    """
    A custom QObject class that emulates QGraphicsItem's cache modes,
    item change enums, and flags functionality.
    """
    
    # Cache modes
    itemChanged = Signal(QGraphicsItem.GraphicsItemChange, object)  # change, value
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._cache_mode = self.NoCache
        self._flags = 0
        self._position = (0, 0)
        self._visible = True
        self._enabled = True
        self._selected = False
        self._transform = None
        self._rotation = 0.0
        self._scale = 1.0
        self._transform_origin = (0, 0)
        self._z_value = 0.0
        self._opacity = 1.0
        
    def itemChange(self, change, value):
        print(f"change: {change}")
        print(f"value: {value}")

        ret = QGraphicsItem.GraphicsItemChange(change, value)
        print(f"ret: {ret}")
        if change == CustomGraphicsItem.ItemPositionChange:
            print(f"Item changed: {change}, New value: {value}")
        """
        Handle item changes. Can be overridden in subclasses for custom behavior.
        Returns the new value after processing.
        """
        #self.itemChanged.emit(change, value)
        return value
    
    # Cache mode property
    @property
    def cacheMode(self):
        return self._cache_mode
    
    @cacheMode.setter
    def cacheMode(self, value):
        if self._cache_mode != value:
            self._cache_mode = value
    
    @property
    def flags(self):
        return self._flags
    
    @flags.setter
    def flags(self, value):
        if self._flags != value:
            new_value = self.itemChange(self.ItemFlagsChange, value)
            self._flags = new_value
            self.itemChange(self.ItemFlagsHaveChanged, new_value)
    
    # Position property
    @property
    def position(self):
        return self._position
    
    @position.setter
    def position(self, value):
        if self._position != value:
            new_value = self.itemChange(self.ItemPositionChange, value)
            self._position = new_value
            self.itemChange(self.ItemPositionHasChanged, new_value)
    
    # Visibility property
    @property
    def visible(self):
        return self._visible
    
    @visible.setter
    def visible(self, value):
        if self._visible != value:
            new_value = self.itemChange(self.ItemVisibleChange, value)
            self._visible = new_value
            self.itemChange(self.ItemVisibleHasChanged, new_value)
    
    # Enabled property
    @property
    def enabled(self):
        return self._enabled
    
    @enabled.setter
    def enabled(self, value):
        if self._enabled != value:
            new_value = self.itemChange(self.ItemEnabledChange, value)
            self._enabled = new_value
            self.itemChange(self.ItemEnabledHasChanged, new_value)
    
    # Selected property
    @property
    def selected(self):
        return self._selected
    
    @selected.setter
    def selected(self, value):
        if self._selected != value:
            new_value = self.itemChange(self.ItemSelectedChange, value)
            self._selected = new_value
            self.itemChange(self.ItemSelectedHasChanged, new_value)
    
    # Transform property
    @property
    def transform(self):
        return self._transform
    
    @transform.setter
    def transform(self, value):
        if self._transform != value:
            new_value = self.itemChange(self.ItemTransformChange, value)
            self._transform = new_value
            self.itemChange(self.ItemTransformHasChanged, new_value)
    
    # Rotation property
    @property
    def rotation(self):
        return self._rotation
    
    @rotation.setter
    def rotation(self, value):
        if self._rotation != value:
            new_value = self.itemChange(self.ItemRotationChange, value)
            self._rotation = new_value
            self.itemChange(self.ItemRotationHasChanged, new_value)
    
    # Scale property
    @property
    def scale(self):
        return self._scale
    
    @scale.setter
    def scale(self, value):
        if self._scale != value:
            new_value = self.itemChange(self.ItemScaleChange, value)
            self._scale = new_value
            self.itemChange(self.ItemScaleHasChanged, new_value)
    
    # Transform origin point property
    @property
    def transformOriginPoint(self):
        return self._transform_origin
    
    @transformOriginPoint.setter
    def transformOriginPoint(self, value):
        if self._transform_origin != value:
            new_value = self.itemChange(self.ItemTransformOriginPointChange, value)
            self._transform_origin = new_value
            self.itemChange(self.ItemTransformOriginPointHasChanged, new_value)
    
    # Opacity property
    @property
    def opacity(self):
        return self._opacity
    
    @opacity.setter
    def opacity(self, value):
        if self._opacity != value:
            new_value = self.itemChange(self.ItemOpacityChange, value)
            self._opacity = new_value
            self.itemChange(self.ItemOpacityHasChanged, new_value)
    
    def setCacheMode(self, mode, logical_cache_size=None, device_cache_size=None):
        """
        Set the cache mode for this item.
        Optionally provide cache sizes for ItemCoordinateCache or DeviceCoordinateCache modes.
        """
        self._cache_mode = mode
        # Here you would typically store the cache sizes if needed
        self._logical_cache_size = logical_cache_size
        self._device_cache_size = device_cache_size
    
    def setFlag(self, flag, enabled=True):
        """Set or clear a flag for this item."""
        flag_int = flag.value if hasattr(flag, 'value') else flag
        if enabled:
            new_flags = self._flags | flag_int
        else:
            new_flags = self._flags & ~flag_int
        
        if self._flags != new_flags:
            self.flags = new_flags
    
    def setParent(self, parent):
        """
        Override setParent to handle parent change notifications
        """
        old_parent = self.parent()
        super().setParent(parent)
        if old_parent != parent:
            self.itemChange(self.ItemParentChange, parent)
            self.itemChange(self.ItemParentHasChanged, parent)
            
def handle_item_change(change, value):
    # Map change enums to names for demonstration
    change_names = {
        CustomGraphicsItem.ItemPositionChange: "PositionChange",
        CustomGraphicsItem.ItemPositionHasChanged: "PositionHasChanged",
        CustomGraphicsItem.ItemVisibleChange: "VisibleChange",
        CustomGraphicsItem.ItemSelectedChange: "SelectedChange",
        CustomGraphicsItem.ItemFlagsChange: "FlagsChange",
        # Add other change types as needed
    }
    print(f"Item changed: {change_names.get(change, change)}, New value: {value}")


app = QtWidgets.QApplication([])

item = CustomGraphicsItem()

# Connect to the itemChanged signal
#item.itemChanged.connect(handle_item_change)

# Set some flags
item.setFlag(CustomGraphicsItem.ItemIsMovable)
item.setFlag(CustomGraphicsItem.ItemIsSelectable)
item.setFlag(CustomGraphicsItem.ItemSendsGeometryChanges)

# Make changes that will trigger notifications
item.position = (100, 100)  # Will emit PositionChange and PositionHasChanged
item.visible = False        # Will emit VisibleChange
item.selected = True        # Will emit SelectedChange
item.flags = CustomGraphicsItem.ItemIsMovable | CustomGraphicsItem.ItemIsSelectable  # Will emit FlagsChange

# Set cache mode
item.setCacheMode(CustomGraphicsItem.DeviceCoordinateCache)


#app.exec()
