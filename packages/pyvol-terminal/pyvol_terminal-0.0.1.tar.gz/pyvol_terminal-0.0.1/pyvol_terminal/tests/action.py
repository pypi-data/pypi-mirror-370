import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QMenuBar, QToolBar
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QAction
import sys


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Create menu bar
        menubar = self.menuBar()
        
        # Create File menu
        file_menu = menubar.addMenu("File")
        
        # Create actions with different display text and icon text
        action1 = QAction(QIcon.fromTheme("document-new"), "New Document", self)
        action1.setIconText("New")  # Shorter text for icon display
        
        action2 = QAction(QIcon.fromTheme("document-open"), "Open Existing File...", self)
        action2.setIconText("Open")  # Shorter text for icon display
        
        action3 = QAction(QIcon.fromTheme("document-save"), "Save Current Document", self)
        action3.setIconText("Save")  # Shorter text for icon display
        
        # Add actions to menu
        file_menu.addAction(action1)
        file_menu.addAction(action2)
        file_menu.addAction(action3)
        
        # Create toolbar and force it to show text
        toolbar = QToolBar("Main Toolbar")
        toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)  # Show text under icons
        self.addToolBar(toolbar)
        
        # Add actions to toolbar
        toolbar.addAction(action1)
        toolbar.addAction(action2)
        toolbar.addAction(action3)
        
        # Connect actions to slots
        action1.triggered.connect(lambda: print("New action triggered"))
        action2.triggered.connect(lambda: print("Open action triggered"))
        action3.triggered.connect(lambda: print("Save action triggered"))
        
        self.setWindowTitle("QAction Text Display Demo")
        self.setGeometry(100, 100, 400, 300)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())