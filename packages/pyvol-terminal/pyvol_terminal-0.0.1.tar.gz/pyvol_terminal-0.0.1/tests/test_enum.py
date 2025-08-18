#%%
from enum import Flag, auto

class ItemChangeFlag(Flag):
    """Custom flags for item changes (like Qt's GraphicsItemChange)."""
    ITEM_POSITION_CHANGE = auto()      # 1
    ITEM_VISIBLE_CHANGE = auto()       # 2
    ITEM_SELECTION_CHANGE = auto()     # 4
    ITEM_PARENT_CHANGE = auto()        # 8
    ITEM_TRANSFORM_CHANGE = auto()     # 16
    
    
class MyCustomItem:
    def __init__(self):
        self._position = (0, 0)
        self._visible = True

    def itemChange(self, change: ItemChangeFlag, value):
        """Mimics QGraphicsItem.itemChange()."""
        if change == ItemChangeFlag.ITEM_POSITION_CHANGE:
            print(f"Position changed to: {value}")
            self._position = value
        elif change == ItemChangeFlag.ITEM_VISIBLE_CHANGE:
            print(f"Visibility changed to: {value}")
            self._visible = value
        elif change in (ItemChangeFlag.ITEM_SELECTION_CHANGE | ItemChangeFlag.ITEM_PARENT_CHANGE):
            print(f"Combined change detected: {change}")
        else:
            print(f"Unhandled change: {change}")

        return value  # (Optional: Return modified value, like Qt)
    
item = MyCustomItem()

# Single flag (position change)
item.itemChange(ItemChangeFlag.ITEM_POSITION_CHANGE, (100, 200))


combined_flags = ItemChangeFlag.ITEM_SELECTION_CHANGE | ItemChangeFlag.ITEM_PARENT_CHANGE
item.itemChange(combined_flags, None)

# Check if a flag is set in a combined value
flags = ItemChangeFlag.ITEM_VISIBLE_CHANGE | ItemChangeFlag.ITEM_TRANSFORM_CHANGE
if ItemChangeFlag.ITEM_VISIBLE_CHANGE in flags:
    print("Visibility flag is set!")  # This runs
    
    
#%%%

from enum import Flag, auto

class ItemChangeFlag(Flag):
    """Flags representing different item change types"""
    ITEM_VISIBLE_CHANGE = auto()
    ITEM_POSITION_CHANGE = auto()
    ITEM_SELECTION_CHANGE = auto()
    ITEM_PARENT_CHANGE = auto()
    ITEM_TRANSFORM_CHANGE = auto()

class GraphicsItem:
    def __init__(self, parent=None):
        self.visible = True
        self.explicitly_hidden = False
        self.parent = parent  # Reference to parent item

    def set_visible_helper(self, new_visible, explicitly=False, update=True, hidden_by_panel=False):
        """
        Mimics QGraphicsItemPrivate::setVisibleHelper
        - new_visible: Target visibility state
        - explicitly: Whether this is an explicit user-set visibility change
        - update: Whether to trigger visual updates
        - hidden_by_panel: Special case for panel visibility
        """
        # Update explicit hidden flag
        if explicitly:
            self.explicitly_hidden = not new_visible

        # Check if visibility is already in target state
        if self.visible == new_visible:
            return

        # Don't show if parent exists and is hidden
        if self.parent and new_visible and not self.parent.visible:
            return

        # Call itemChange to potentially modify the visibility
        modified_visible = self.item_change(
            ItemChangeFlag.ITEM_VISIBLE_CHANGE,
            new_visible
        )

        # Check if itemChange modified the visibility
        if self.visible == modified_visible:
            return

        # Update visibility state
        self.visible = modified_visible
        
        # Additional logic would go here (update children, emit signals, etc.)
        if update:
            self.update_visuals()
    
    def item_change(self, change, value):
        """
        Customizable change handler - similar to QGraphicsItem.itemChange
        Override this in subclasses to modify behavior
        """
        # Base implementation just returns the value unchanged
        return value

    def update_visuals(self):
        """Placeholder for visual update logic"""
        print(f"Visibility updated to: {self.visible}")
        # Would typically trigger redraw/update here

# Example subclass with custom itemChange behavior
class CustomItem(GraphicsItem):
    def item_change(self, change, value):
        if change == ItemChangeFlag.ITEM_VISIBLE_CHANGE:
            print(f"Visibility change requested: {value}")
            # Add custom logic here - e.g., prevent hiding in some cases
            if value is False:
                print("Preventing item from being hidden!")
                return True  # Override to remain visible
            return value
        return super().item_change(change, value)

# Usage example
if __name__ == "__main__":
    parent_item = GraphicsItem()
    parent_item.visible = False  # Parent is hidden
    
    child_item = CustomItem(parent=parent_item)
    
    print("Trying to show child (should be blocked by parent):")
    child_item.set_visible_helper(True)
    # Output: (no change, blocked by parent)
    
    print("\nTrying to hide child with custom logic:")
    child_item.set_visible_helper(False)
    # Output: 
    # Visibility change requested: False
    # Preventing item from being hidden!
    # Visibility updated to: True