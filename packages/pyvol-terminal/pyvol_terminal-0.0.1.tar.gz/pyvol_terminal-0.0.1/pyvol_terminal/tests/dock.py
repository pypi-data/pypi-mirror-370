import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QDockWidget, QTextEdit, 
                               QMenu, QLabel, QWidget)
from PySide6.QtCore import Qt, QEvent, QPoint
from PySide6.QtGui import QContextMenuEvent


class DockWidget(QDockWidget):
    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.setAllowedAreas(Qt.AllDockWidgetAreas)
        
        # Create content for the dock
        content = QLabel("Right-click the title bar to dock/undock this widget")
        content.setAlignment(Qt.AlignCenter)
        self.setWidget(content)
        
        # Track floating state changes
        self.topLevelChanged.connect(self.handle_floating_change)
        
        # Install event filter for both docked and floating states
        self.update_event_filter()
    
    def handle_floating_change(self, floating):
        self.update_event_filter()
    
    def update_event_filter(self):
        # Remove any existing filter
        try:
            self.title_bar.removeEventFilter(self)
        except:
            pass
        
        # Find the current title bar widget
        if self.isFloating():
            # For floating state, the title bar is the window's title bar
            self.title_bar = self.findChild(QWidget, "qt_dockwidget_floatwindow")
        else:
            # For docked state, use the standard title bar
            self.title_bar = self.findChild(QWidget, "qt_dockwidget_titlebar")
        
        if self.title_bar:
            self.title_bar.installEventFilter(self)
    
    def eventFilter(self, obj, event):
        # Handle right-click on title bar
        if (obj == self.title_bar and 
            event.type() == QEvent.MouseButtonRelease and 
            event.button() == Qt.RightButton):
            
            # For floating windows, we need to adjust the position
            if self.isFloating():
                pos = self.mapToGlobal(QPoint(event.pos().x(), self.title_bar.height()))
            else:
                pos = event.globalPos()
            
            self.show_titlebar_menu(pos)
            return True
        return super().eventFilter(obj, event)
    
    def show_titlebar_menu(self, pos):
        menu = QMenu(self)
        
        # Toggle floating state action
        if self.isFloating():
            action_text = "Dock"
        else:
            action_text = "Float"
            
        float_action = menu.addAction(action_text)
        float_action.triggered.connect(self.toggle_floating)
        
        # Add other standard actions
        close_action = menu.addAction("Close")
        close_action.triggered.connect(self.close)
        
        menu.exec(pos)
    
    def toggle_floating(self):
        self.setFloating(not self.isFloating())


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DockWidget Right-Click Example")
        self.setGeometry(100, 100, 800, 600)
        
        # Central widget
        self.setCentralWidget(QTextEdit("Main Window Content"))
        
        # Create dock widget
        self.dock = DockWidget("Tool Panel", self)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dock)
        
        # Make it float initially to demonstrate the feature
        self.dock.setFloating(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())