from typing import Dict, List, Callable, Union, Any
from functools import partial
from PySide6 import QtWidgets, QtGui
import sys

class RefSlotsMenu(QtWidgets.QMenu):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._connected_slots: Dict[str, List[Dict]] = {}
        self._action_objects: Dict[str, QtGui.QAction] = {}
        
    def addAction(self, action: QtGui.QAction, slots: List[Dict[str, Any]]) -> None:
        """
        Store slot configurations for an action WITHOUT connecting them.
        (Assumes connections are already handled externally)
        
        Args:
            action: The QAction to add
            slots: List of slot configurations (just stores references):
                'slot': The callable
                'connection_method': Signal type used (e.g., 'triggered')
                'args': Fixed positional args (if any)
                'kwargs': Fixed keyword args (if any)
        """
        self._action_objects[action.text()] = action
        self._connected_slots[action.text()] = slots  # Just store the configs
        super().addAction(action)  # Only adds the action to the menu
    
    def _connect_slots(self, action: QtGui.QAction, slot_configs: List[Dict]) -> None:
        for config in slot_configs:
            slot = config['slot']
            method = config['connection_method']
            args = config['args']
            kwargs = config['kwargs']
            
            signal = getattr(action, method, None)
            if signal is None:
                raise AttributeError(f"Action has no signal '{method}'")
            
            if args or kwargs:
                signal.connect(partial(slot, *args, **kwargs))
            else:
                signal.connect(slot)
    def map_slots_to_new_action(self, source_action: QtGui.QAction, target_action: QtGui.QAction) -> None:
        """
        Copy all stored slot configurations from source_action to target_action.
        Disconnects any existing connections on target_action first.
        
        Args:
            source_action: The action to copy slot configurations from
            target_action: The action to apply the slot configurations to
        """
        # Get source action text (used as key in our storage)
        
        super().addAction(source_action)
        
        source_text = source_action.text()
        
        if source_text not in self._connected_slots:
            raise KeyError(f"No slot configurations stored for action '{source_text}'")
        
        # First disconnect all existing connections on target action
        
        # Get all slot configs from source action
        slot_configs = self._connected_slots[source_text]
        
        # Connect each slot configuration to the target action
        for config in slot_configs:
            slot = config['slot']
            method = config['connection_method']
            args = config.get('args', ())
            kwargs = config.get('kwargs', {})
            
            signal = getattr(target_action, method, None)
            if signal is None:
                raise AttributeError(f"Target action has no signal '{method}'")
            
            if args or kwargs:
                signal.connect(partial(slot, *args, **kwargs))
            else:
                signal.connect(slot)
        
        # Store the configurations with the target action's text as key
        target_text = target_action.text()
        self._connected_slots[target_text] = slot_configs.copy()
        self._action_objects[target_text] = target_action
        
        self.addAction(source_action, target_action)
        
        
        
    def reconnect_slots(self, action_text: str, new_signal: str) -> None:
        if action_text not in self._connected_slots:
            raise KeyError(f"No action with text '{action_text}' found")
            
        action = self._action_objects[action_text]
        slot_configs = self._connected_slots[action_text]
        
        # First disconnect all existing connections
        for config in slot_configs:
            old_signal = getattr(action, config['connection_method'])
            try:
                old_signal.disconnect(config['slot'])
            except TypeError:
                pass
        
        # Update connection method in all configs
        for config in slot_configs:
            config['connection_method'] = new_signal
        
        # Reconnect with new signal
        self._connect_slots(action, slot_configs)
    
    def get_action(self, text: str) -> QtGui.QAction:
        return self._action_objects.get(text)
    
    def get_slot_configs(self, action_text: str) -> List[Dict]:
        return self._connected_slots.get(action_text, [])
            
    def add_signal_to_existing_slots(self, action_text: str, new_signal_name: str) -> None:
        """
        Connect all existing slots of an action to a new signal
        
        Args:
            action_text: Text of the action to modify
            new_signal_name: Name of the new signal to connect to (e.g. 'triggered', 'toggled')
        """
        if action_text not in self._connected_slots:
            raise KeyError(f"No action with text '{action_text}' found")
            
        action = self._action_objects[action_text]
        slot_configs = self._connected_slots[action_text]
        
        # First, disconnect all slots from their current signals
        for config in slot_configs:
            old_signal = getattr(action, config['connection_method'])
            slot = config['slot']
            args = config.get('args', ())
            kwargs = config.get('kwargs', {})
            
            try:
                if args or kwargs:
                    # Disconnect the partial version
                    old_signal.disconnect(partial(slot, *args, **kwargs))
                else:
                    # Disconnect the direct slot
                    old_signal.disconnect(slot)
            except (TypeError, RuntimeError):
                # Ignore if not connected
                pass
        
        # Get the new signal
        new_signal = getattr(action, new_signal_name, None)
        if new_signal is None:
            raise AttributeError(f"Action has no signal '{new_signal_name}'")
        
        # Connect all existing slots to the new signal
        for config in slot_configs:
            slot = config['slot']
            args = config.get('args', ())
            kwargs = config.get('kwargs', {})
            
            if args or kwargs:
                new_signal.connect(partial(slot, *args, **kwargs))
            else:
                new_signal.connect(slot)
        
        # Update the connection method in config for future reference
        for config in slot_configs:
            config['connection_method'] = new_signal_name
                
                
# Test handlers
def handler1(checked, name):
    print(f"Handler1: {name} is {checked}")

def handler2(checked):
    print(f"Handler2: {checked}")

def handler3(checked, extra_arg, kwarg=None):
    print(f"Handler3: Checked={checked}, Extra={extra_arg}, KW={kwarg}")


def basic_handler(checked):
    print(f"Basic handler - Checked: {checked}")

def named_handler(checked, name):
    print(f"Named handler - {name} is {checked}")

def partial_handler(checked, fixed_arg, kwarg=None):
    print(f"Partial handler - Checked: {checked}, Fixed: {fixed_arg}, KW: {kwarg}")

# Create application
app = QtWidgets.QApplication(sys.argv)
# Create main window with close button
window = QtWidgets.QMainWindow()
window.setWindowTitle("Menu Close Example")
window.resize(300, 200)
# Create our custom menu
menu = RefSlotsMenu("Demo Menu")
# Existing action with slots connected to 'triggered'
action = QtGui.QAction("Test Action", menu)
action.setCheckable(True)  # Required for 'toggled' signal
menu.addAction(action, [
    {'slot': handler1, 'connection_method': 'triggered', 'args': (True,)},
    {'slot': handler2, 'connection_method': 'triggered'}
])

# Replace 'triggered' with 'toggled' (disconnects old signals automatically)
menu.add_signal_to_existing_slots("Test Action", "toggled")
# Add the target action to the menu

tool_button = QtWidgets.QToolButton()
tool_button.setText("Show Menu")
tool_button.setPopupMode(QtWidgets.QToolButton.InstantPopup)
tool_button.setMenu(menu)

# Add button to toolbar
toolbar = window.addToolBar("Main Toolbar")
toolbar.addWidget(tool_button)

# Show window
window.show()

# Execute application
sys.exit(app.exec())