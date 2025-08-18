from PySide6 import QtWidgets, QtCore, QtGui
import sys

class OptionsTab(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        layout = QtWidgets.QVBoxLayout(self)

        self.tool_button = QtWidgets.QToolButton()
        self.tool_button.setText("Option Title")
        self.tool_button.setPopupMode(QtWidgets.QToolButton.InstantPopup)

        menu = QtWidgets.QMenu(self.tool_button)

        self.actions = []
        for i in range(5):
            action = QtGui.QAction(f"Option {i + 1}", self)
            action.setCheckable(True)
            menu.addAction(action)
            self.actions.append(action)

        self.action_group = QtGui.QActionGroup(self)
        self.action_group.setExclusive(False)
        for action in self.actions:
            self.action_group.addAction(action)

        # Set the menu to the tool button
        self.tool_button.setMenu(menu)

        # Add the tool button to the layout
        layout.addWidget(self.tool_button)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dropdown Options with QToolButton")
        self.resize(400, 200)

        tabs = QtWidgets.QTabWidget()
        self.setCentralWidget(tabs)

        options_tab = OptionsTab()
        tabs.addTab(options_tab, "Options")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
