from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QComboBox
)
from PySide6.QtCore import Slot, Qt
from PySide6 import QtWidgets

class Terminal(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # Create button layout with 4 buttons
        button_layout = QHBoxLayout()
        self.buttons = []
        for i in range(1, 5):
            button = QPushButton(f"Button {i}")
            button.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
            button.clicked.connect(self.create_button_handler(i))
            self.buttons.append(button)
            button_layout.addWidget(button)
        
        
        self.combo_box = QComboBox()
        self.combo_box.addItems(["No Instrument Selected", "Option 2", "Option 3", "Option 4"])
        self.combo_box.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Maximum)
        self.combo_box.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.combo_box.currentIndexChanged.connect(self.update_button_state)
        
        main_layout.addWidget(self.combo_box)
        main_layout.addLayout(button_layout)
        
        
        self.update_button_state(0)
        self.adjustSize()              # Resize widget to fit contents
        self.setFixedSize(self.size())  # Lock size
            
    def update_button_state(self, index):
        """Enable/disable buttons based on combo box selection"""
        # Disable buttons for first option, enable for others
        state = index != 0
        for button in self.buttons:
            button.setEnabled(state)
    
    def create_button_handler(self, button_id):
        """Create a slot handler for button clicks"""
        @Slot()
        def handler():
            # Get current combo box text
            selected_option = self.combo_box.currentText()
            print(f"Button {button_id} clicked with option: {selected_option}")
            # Add your custom button handling logic here
        return handler

if __name__ == "__main__":
    app = QApplication([])
    
    widget = Terminal()
    widget.setWindowTitle("Combo Button Widget")
    widget.resize(400, 200)
    widget.show()
    
    app.exec()